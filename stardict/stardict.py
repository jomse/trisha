
"""
This is heavily refactored version of https://github.com/lig/pystardict
StarDict format description can be found at
http://www.stardict.org/StarDictFileFormat

"""
import gzip
import hashlib
import os
import re
import struct

from collections import namedtuple
from contextlib import closing



def lazy_property(fn):
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazy(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy


class IfoParseError(Exception):
    pass


class _StarDictIfo:
    """
    Available properties:
        bookname
        wordcount
        synwordcount
        idxfilesize
        idxoffsetbits
        author
        email
        website
        description
        date
        sametypesequence
    """

    def __init__(self, dictionary):
        self._properties = {}
        self._filename = os.path.join(dictionary.location,
                                      '{}.ifo'.format(dictionary.name))
        self._properties = self._load_properties(self._filename)

    def __getattr__(self, item):
        item = item.lower()
        if item in self._properties:
            return self._properties[item]
        raise AttributeError("Unknown property '{0}'".format(item))

    def _load_properties(self, path):
        loaded_properties = self._load_ifo_file(path)
        self._validate(loaded_properties)
        self._transform(loaded_properties)

        properties = self._default_properties()
        properties.update(loaded_properties)

        return properties

    @staticmethod
    def _default_properties():
        return {
            'author': '',
            'date': '',
            'description': '',
            'email': '',
            'idxoffsetbits': 32,
            'sametypesequence': '',
            'website': ''
        }

    @staticmethod
    def _load_ifo_file(path):
        with open(path) as ifo_file:
            ifo_lines = ifo_file.readlines()
        if not ifo_lines:
            raise IfoParseError('Empty ifo file')
        key_value_pairs = [line.rstrip().split('=') for line in ifo_lines[1:]]
        return dict(key_value_pairs)

    @staticmethod
    def _validate(properties):
        required_options = ['version', 'bookname', 'idxfilesize', 'wordcount']
        missing_options = [option for option in required_options
                           if not properties.keys()]
        if missing_options:
            raise IfoParseError(
                'Required ifo file options {0} are missing'.format(
                    ','.join(missing_options)))

    def _transform(self, properties):
        self._set_digit_value(properties, 'synwordcount')
        self._set_digit_value(properties, 'idxfilesize')
        self._set_digit_value(properties, 'wordcount')

    @staticmethod
    def _set_digit_value(properties, key):
        value = properties.get(key)
        if not value:
            return
        if not value.isdigit():
            raise IfoParseError('{0} is not a digit'.format(key))
        properties[key] = int(value)


class IdxParseError(Exception):
    pass


_TranslationPosition = namedtuple('_TranslationPosition', ['offset', 'length'])


class _StarDictIdx:
    def __init__(self, dictionary, extension, compressed_extension):
        self._dictionary = dictionary

        filename = '{0}.{1}'.format(
            os.path.join(dictionary.location, dictionary.name), extension)
        filename_gz = '{0}.{1}'.format(
            os.path.join(dictionary.location, dictionary.name),
            compressed_extension)
        self._file = read_any_file(filename, filename_gz)

        if len(self._file) != dictionary.ifo.idxfilesize:
            raise IdxParseError(
                'size of the .idx file is incorrect. '
                'Expected: {0}, actual: {1}'.format(dictionary.ifo.idxfilesize,
                                                    len(self._file)))

        self._idx = self._parse_idx()

    def _parse_idx(self):
        offset_size = int(self._dictionary.ifo.idxoffsetbits / 8)
        idx_cords_bytes_size = str(offset_size + 4).encode()

        record_pattern = (br'([\d\D]+?\x00[\d\D]{' +
                          idx_cords_bytes_size + br'})')
        matched_records = re.findall(record_pattern, self._file)

        expected_word_count = self._dictionary.ifo.wordcount
        if len(matched_records) != expected_word_count:
            raise IdxParseError(
                'incorrect word number in idx file. '
                'Expected: {0}, actual: {1}'.format(expected_word_count,
                                                    len(matched_records)))

        return {word: position for word, position
                in self._word_records(matched_records, offset_size)}

    def _word_records(self, records, offset_size):
        for word_record in records:
            yield self._parse_word_record(word_record, offset_size)

    @staticmethod
    def _parse_word_record(record, offset_size):
        offset_format = {4: 'L', 8: 'Q'}[offset_size]
        word_end_position = record.find(b'\x00') + 1
        record_format = '!{0}c{1}L'.format(word_end_position,
                                           offset_format)
        record_tuple = struct.unpack(record_format, record)

        word = b''.join(record_tuple[:word_end_position - 1]).decode()
        translation = _TranslationPosition(offset=record_tuple[-2],
                                           length=record_tuple[-1])
        return word, translation

    def __getitem__(self, word):
        return self._idx[word]

    def __contains__(self, word):
        return word in self._idx

    def __eq__(self, another):
        return (hashlib.md5(self._file).hexdigest() ==
                hashlib.md5(another._file).hexdigest())

    def __ne__(self, another):
        return not self.__eq__(another)

    def words(self):
        return [key for key in self._idx.keys()]


class _StarDictDict:
    def __init__(self, dictionary, in_memory, dict_extension,
                 compressed_dict_extension):
        self._dictionary = dictionary
        self._in_memory = in_memory

        self._filename = os.path.join(
            dictionary.location, '{0}.{1}'.format(dictionary.name,
                                                  dict_extension))
        self._filename_dz = os.path.join(
            dictionary.location, '{0}.{1}'.format(dictionary.name,
                                                  compressed_dict_extension))

        if in_memory:
            self._file = read_any_file(self._filename,
                                       self._filename_dz)

    def __getitem__(self, word):
        position = self._dictionary.idx[word]

        if self._in_memory:
            translation = self._file[position.offset:
                                     position.offset + position.length]
            return translation.decode('utf-8')

        with closing(_open_any_file(self._filename, self._filename_dz)) as f:
            f.seek(position.offset)
            translation = f.read(position.length)
        return translation.decode('utf-8')


class Dictionary:
    def __init__(self, dict_dir, dict_name, in_memory=False,
                 dict_extension='dict', compressed_dict_extension='dict.dz',
                 idx_extension='idx', compressed_idx_extension='idx.gz'):
        self._dict_name = dict_name
        self._dict_dir = dict_dir

        self._in_memory = in_memory

        self._dict_extension = dict_extension
        self._compressed_dict_extension = compressed_dict_extension
        self._idx_extension = idx_extension
        self._compressed_idx_extension = compressed_idx_extension

        self._ifo = _StarDictIfo(self)

    @property
    def location(self):
        return self._dict_dir

    @property
    def name(self):
        return self._dict_name

    @property
    def bookname(self):
        return self._ifo.bookname

    @property
    def author(self):
        return self._ifo.author

    @property
    def email(self):
        return self._ifo.email

    @property
    def description(self):
        return self._ifo.description

    @property
    def date(self):
        return self._ifo.date

    @property
    def words(self):
        return self.idx.words()

    @property
    def ifo(self):
        return self._ifo

    @lazy_property
    def idx(self):
        idx = _StarDictIdx(self, self._idx_extension,
                           self._compressed_idx_extension)
        return idx

    @lazy_property
    def dict(self):
        dictionary = _StarDictDict(self, self._in_memory, self._dict_extension,
                                   self._compressed_dict_extension)
        return dictionary

    def get(self, key, default=''):
        return self.dict[key] if key in self.idx else default

    def has_word(self, key):
        return key in self.idx

    def __contains__(self, key):
        return key in self.idx

    def __eq__(self, another):
        return self.idx.__eq__(another._idx)

    def __ne__(self, another):
        return not self.__eq__(another)

    def __getitem__(self, key):
        return self.dict[key]

    def __len__(self):
        return self._ifo.wordcount

    def __repr__(self):
        return self._ifo.bookname

    def __hash__(self):
        return hash(self.bookname)

def read_any_file(filename, gz_filename):
    with closing(_open_any_file(filename, gz_filename)) as f:
        return f.read()


class FileOpenError(Exception):
    pass


def _open_any_file(filename, gz_filename):
    try:
        return open(filename, 'rb')
    except IOError:
        pass

    try:
        return gzip.open(gz_filename, 'rb')
    except IOError:
        raise FileOpenError('Failed to open {0} or {1}'.format(
            filename, gz_filename))

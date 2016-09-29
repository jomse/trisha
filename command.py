import os
import sys
import db_alchemy, quiz
import show


from stardict import Dictionary
from color import Color
from utils import pretty_print_dict


class CommandExecutor:
    def __init__(self, dictionaries):
        self._dictionaries = dictionaries
        self._invoker = CommandInvoker()
        self._commands = {
             '!q': Exit,
             '!c': AddDict,
             '!v': ShowUsedDictionaries,
             '!dd': DelDict,
             '!find': ShowAvailableDictionaries,
             '!t': Quiz,
             '!f': Filter,
             '!del': DelWord
        }
        self._non_custom_commands = {
            '!h': lambda _: print(self.invoker.history),
            '!man': self.manual
        }

    def manual(self,command):
        for values in self._commands.values():
            values.manual()
        print('!man - shows the manual')

    def execute_command(self, text):
        command, arguments = self.split_command(text)
        if command in self._commands:
            command_obj = self._commands[command](self._dictionaries, arguments)
            self.invoker.execute(command_obj)
        elif command in self._non_custom_commands:
            self._non_custom_commands[command](arguments)

        else:
            self.invoker.execute(Translate(self._dictionaries, text))

    @staticmethod
    def split_command(text):
        command = text.split(maxsplit=1)
        if len(command) == 2:
            return command[0], command[1]
        return text, None

    @property
    def invoker(self):
        return self._invoker


class Dictionaries:
    def __init__(self, output_lang, input_lang, dict_dir):
        self._db = db_alchemy.DataBase()
        self._available_dictionaries = self._find_dictionaries(dict_dir)
        self._used_dictionaries = set()
        if input_lang == 'en' and output_lang == 'ru':
            self.use_dictionary('quick_english-russian')
        if input_lang == 'ru' and output_lang == 'en':
            self.use_dictionary('quick_russian-english')

    def translate_word(self, text):
        translations = set(
            [dictionary[text] for dictionary in self._used_dictionaries
             if text in dictionary])
        for trans in translations:
            self._db.insert(text, trans)
        print('\n'.join(show.show_translation_list(translations)))

    def use_dictionary(self, dictionary_name):
        dictionary = self._find_dictionary(dictionary_name)
        if dictionary is None:
            raise Exception(
                'Dictionary {} is not found'.format(dictionary_name))
        self._used_dictionaries.add(dictionary)

    def remove_dictionary(self, name):
        self._used_dictionaries.remove(name)

    def delete_word(self, word):
        self._db.delete_word(word)
        print(str(Color.sYellow)+'Word '+str(word)+' has been removed'+str(Color.sWight))

    def delete_all_word(self):
        self._db.delete_all_word()
        print(str(Color.sYellow) + 'All word ' + ' has been removed' + str(Color.sWight))

    def quiz(self):
        while True:
            quiz.quiz_start(self)

    @property
    def used_dictionaries(self):
        return self._used_dictionaries

    @property
    def available_dictionaries(self):
        return self._available_dictionaries

    def __len__(self):
        return len(self._used_dictionaries)

    def __str__(self):
        booknames = ["{0}{1}".format(' ' * 16, dictionary.idx.bookname)
                     for dictionary in self._used_dictionaries]
        return "Connected dictionaries: \n {0}".format("\n".join(booknames))

    def _find_dictionary(self, dictionary_name):
        for dictionary in self._available_dictionaries:
            if dictionary.bookname == dictionary_name:
                return dictionary
        return None

    @staticmethod
    def _find_dictionaries(directory):
        dictionaries = []
        for root, directories, files in os.walk(directory, topdown=True):
            for file_ifo in files:
                if not file_ifo.endswith('.ifo'):
                    continue
                try:
                    dictionaries.append(
                       Dictionary(root, file_ifo[:-4], in_memory=False))
                except Exception:
                    # Failed to load a dictionary
                    pass
        return dictionaries


class Command:
    def __init__(self, dictionaries, arguments):
        self._dictionaries = dictionaries
        self._args = arguments

    def execute(self):
        raise NotImplementedError

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self._args)

    def __repr__(self):
        return self.__str__()


class Filter(Command):
    def execute(self):
        flist = []
        if self._args != None: flist = self._args.split()
        a = ''
        if '-a' in flist:
            flist.remove('-a')
            flist.sort()
            a = '-a'
        if flist != []:
            filtered_list = self._dictionaries._db.filter_by_word(flist)
            show.show_all_word(filtered_list)
        if flist == []:
            all_rec = self._dictionaries._db.pick_all_word(a)
            show.show_all_word(all_rec)

    @staticmethod
    def manual():
        print('!f [word]- filter by word')


class DelWord(Command):
    def execute(self):
        list_rec = self._args.split()
        if '-all' in list_rec:
            list_rec.remove('-all')
            self._dictionaries.delete_all_word()
        if list_rec != []:
            for word in list_rec:
                self._dictionaries.delete_word(word)

    @staticmethod
    def manual():
        print('!del [word] -all - delete word, -all delete all word')


class Quiz(Command):
    def execute(self):
        try:
            self._dictionaries.quiz()
        except Exception:
            print('\033[1;37m',end = '')

    @staticmethod
    def manual():
        print('!t - start Quiz')


class Exit(Command):
    def execute(self):
        sys.exit()

    @staticmethod
    def manual():
        print('!q - exit Trisha')


class AddDict(Command):
    def execute(self):
        self._dictionaries.use_dictionary(self._args)

    @staticmethod
    def manual():
      print('!c [NameDictionary] - connect to dictionary')


class ShowUsedDictionaries(Command):
    def execute(self):
        info = {dictionary.bookname: dictionary.ifo.wordcount
                for dictionary in self._dictionaries.used_dictionaries}
        print("Used dictionaries:")
        pretty_print_dict(info)

    @staticmethod
    def manual():
        print('!v  - view using dictionary')


class DelDict(Command):
    def execute(self):
        self._dictionaries.remove_dictionary(self._args)

    @staticmethod
    def manual():
        print('!dd [NameDictionary] - delete dictionary')


class ShowAvailableDictionaries(Command):
    def execute(self):
        info = {dictionary.bookname: dictionary.ifo.wordcount
                for dictionary in self._dictionaries.available_dictionaries}
        print("Available dictionaries:")
        pretty_print_dict(info)

    @staticmethod
    def manual():
        print('!find - view available dictionary')


class Translate(Command):
    def execute(self):
        self._dictionaries.translate_word(self._args)


class CommandInvoker:
    def __init__(self):
        self._history = ()

    @property
    def history(self):
        return self._history

    def execute(self, command):
        self._history = self._history + (command, )
        command.execute()


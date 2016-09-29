import os
import sys
import db_alchemy, quiz
import show

from stardict import Dictionary

from utils import pretty_print_dict


class CommandExecutor:
    def __init__(self, dictionaries):
        self._dictionaries = dictionaries
        self._invoker = CommandInvoker()
        self._commands = {
             '!h': lambda _: print(self.invoker.history),
             '!q': lambda args: self.invoker.execute(
                 Exit(self._dictionaries, args)),
             '!c': lambda args: self.invoker.execute(
                 AddDict(self._dictionaries, args)),
             '!v': lambda args: self.invoker.execute(
                 ShowUsedDictionaries(self._dictionaries, args)),
             '!dd': lambda args: self.invoker.execute(
                 DelDict(self._dictionaries, args)),
             '!f': lambda args: self.invoker.execute(
                  ShowAvailableDictionaries(self._dictionaries, args)),
             '!man': lambda args: self.invoker.execute(
                  ShowAvailableCommand(self._dictionaries,self._commands)),
             '!t': lambda args: self._invoker.execute(
                  Quiz(self._dictionaries, args))


        }

    def execute_command(self, text):
        command, arguments = self.split_command(text)
        if command in self._commands:
            self._commands[command](arguments)
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
        #print('\n'.join(translations))

    def use_dictionary(self, dictionary_name):
        dictionary = self._find_dictionary(dictionary_name)
        if dictionary is None:
            raise Exception(
                'Dictionary {} is not found'.format(dictionary_name))
        self._used_dictionaries.add(dictionary)

    def remove_dictionary(self, name):
        self._used_dictionaries.remove(name)


    def quiz(self):
        while True:
            quiz.quiz_start(self)
            '''
            text = input('! ')
            text = text.split()
            if text[0] == '!q':
                raise Exception('Quite quiz')
            if text[0] == '!d':
                self._db.delete(text[1])
            if text[0] == '!p':
                self._db.pick_word()
            if text[0] == '!a':
                self._db.pick_all_word()
            if text[0] == '!w':
                rec_list = self._db.oldest_records([])
                rec = self._db.rand_rec(rec_list)
                status = quiz.quiz_view(rec_list, rec)
                if status == 1:
                    #self._db.delete(rec)
                    print('YOU A RIGHT')

            else:
                self._db.select(text[0])
            '''


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

    def man(self):
        raise NotImplementedError

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self._args)

    def __repr__(self):
        return self.__str__()


class Quiz(Command):
    def execute(self):
        try:
            self._dictionaries.quiz()
        except Exception:
            pass




class Exit(Command):
    def execute(self):
        sys.exit()


class AddDict(Command):
    def execute(self):
        self._dictionaries.use_dictionary(self._args)


class ShowUsedDictionaries(Command):
    def execute(self):
        info = {dictionary.bookname: dictionary.ifo.wordcount
                for dictionary in self._dictionaries.used_dictionaries}
        print("Used dictionaries:")
        pretty_print_dict(info)


class DelDict(Command):
    def execute(self):
        self._dictionaries.remove_dictionary(self._args)


class ShowAvailableCommand(Command):
    def execute(self):
        print(" ".join(["%s" % command for command in self._args.keys() ]))



class ShowAvailableDictionaries(Command):
    def execute(self):
        info = {dictionary.bookname: dictionary.ifo.wordcount
                for dictionary in self._dictionaries.available_dictionaries}
        print("Available dictionaries:")
        pretty_print_dict(info)


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

    def print_manual(self, command):
        command.man()

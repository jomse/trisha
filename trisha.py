#!/usr/bin/env python3
import argparse
import os

import command


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lin', dest='input_lang', default='en',
                        metavar='LANGUAGE', help='input language')
    parser.add_argument('--lout', dest='output_lang', default='ru',
                        metavar='LANGUAGE', help='language output')

    parser.add_argument('--dict-dir', dest='dict_dir',
                        default=os.path.join(os.path.dirname(__file__), 'dict'),
                        metavar='PATH', help='dictionaries directory')
    return parser.parse_args()


def translate_words(dictionaries):
    executor = command.CommandExecutor(dictionaries)
    while True:
        try:
            text = input('translate word: ')
        except EOFError:
            break
        executor.execute_command(text)


def main():
    args = parse_arguments()
    print('{} -> {}'.format(args.input_lang, args.output_lang))
    dictionaries = command.Dictionaries(args.output_lang, args.input_lang,
                                        args.dict_dir)
    try:
        translate_words(dictionaries)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

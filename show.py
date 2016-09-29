import sys
import os

def show_translation_list(translition):
    new_translition = []
    for tr in translition:
        new_translition.append('                '+' '.join(tr.split('\n')))
    return new_translition


def show_translation_word(translition):
    new_translition = 'НЫЫЫЫА'
    new_translition = (' '.join(translition.split('\n')))
    return new_translition
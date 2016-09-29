import sys
import os
import const
from color import Color


def show_translation_list(translition):
    new_translition = []
    for tr in translition:
        new_translition.append(' '*16+' '.join(tr.split('\n')))
    return new_translition


def show_translation_word(translition):
    new_translition = (' '.join(translition.split('\n')))
    return new_translition


def show_filter_head():
    rows, columns = os.popen('stty size', 'r').read().split()
    size_w, size_d, size_t = columns_partition(columns)
    print(str(Color.sBlue)+' '*round(size_w/4)+'Word'.ljust(size_w), \
          ' '*round(size_d/4)+'Date'.ljust(size_d),' '*round(size_t/4)+'Transfer'.ljust(size_t)+str(Color.sWight))


def show_filteredlist_by_word(filtered_list):
    flag = 0
    rows, columns = os.popen('stty size', 'r').read().split()
    size_w, size_d, size_t = columns_partition(columns)

    if const.filter_view == 'ez' and flag == 0:
        oldest = filtered_list[0].date
        for rec in filtered_list:
            if oldest > rec.date:
                oldest = rec.date

    print(filtered_list[0].word.ljust(size_w), str(oldest)[:19].ljust(size_d))
    flag = 1

    if const.filter_view != 'ez':
        for rec in filtered_list:
            if (flag == 1):
                if len(show_translation_word(rec.transfer)) < size_t:
                    print(''.ljust(size_w), str(rec.date)[:19].ljust(size_d), show_translation_word(rec.transfer))
                if len(show_translation_word(rec.transfer)) >= size_t:
                    print(''.ljust(size_w), str(rec.date)[:19].ljust(size_d), show_translation_word(rec.transfer)[:size_t])
                    i = size_t
                    while i<=len(show_translation_word(rec.transfer)):
                        print(' '*(size_d+size_w+1), show_translation_word(rec.transfer)[i:i+size_t])
                        i+=size_t
            if flag ==0:
                if len(show_translation_word(rec.transfer)) < size_t:
                    print(rec.word.ljust(size_w), str(rec.date)[:19].ljust(size_d), show_translation_word(rec.transfer))
                if len(show_translation_word(rec.transfer)) >= size_t:
                    print(rec.word.ljust(size_w), str(rec.date)[:19].ljust(size_d), show_translation_word(rec.transfer)[:size_t])
                    i = size_t
                    while i<=len(show_translation_word(rec.transfer)):
                        print(' '*(size_d+size_w+1),show_translation_word(rec.transfer)[i:i+size_t])
                        i+=size_t
                flag = 1


def show_all_word(all_word):
    useable_rec = []
    show_filter_head()
    for rec in all_word:
        index = rec.word
        if not(rec.word in useable_rec):
            list = [rec1 for rec1 in all_word if rec1.word == index]
            useable_rec.append(rec.word)
            show_filteredlist_by_word(list)


def columns_partition(columns):
    columns = int(columns)
    size_word = round((columns*1)/10)
    size_date = 20
    size_tranlation = columns - size_date - size_word
    return size_word, size_date, size_tranlation-2

import show
import const
import os
from color import Color


def quiz_view(q_list, q_word):
    rows, columns = os.popen('stty size', 'r').read().split()
    columns =int(columns)
    print(str(Color.sYellow)+'_'*(round(columns/8))+'TEST: '+str(const.number_of_tests) +\
          '_' * (round(columns/8))+str(Color.sWight))
    print(str(Color.sGray)+'Translane --> '+str(Color.sWight), end=' ')
    print((str(Color.sMagenta)+'{}'+str(Color.sWight)).format(q_word.word))
    i = 0
    qwe = {}
    for rec in q_list:
        if i < const.quiz_list_len:
            qwe[rec] = i
            print((str(Color.sMagenta)+' [{0}]'+str(Color.sWight)+' {1}').format(i, show.show_translation_word(rec.transfer)))
            i += 1
    text = input(str(Color.sWight)+'---> '+str(Color.sWight))
    if text == '!q': raise Exception('Exit Quiz')
    if int(text) == qwe[q_word]:
        print(str(Color.sBlue)+' You was right'+str(Color.sWight))
        const.number_of_tests += 1
        return 1
    if int(text) != qwe[q_word]:
        print(str(Color.sHRed)+' ERROR'+str(Color.sWight))
        quiz_view(q_list, q_word)


def quiz_start(dict):
    rec_list = dict._db.oldest_records([])
    rec = dict._db.rand_rec(rec_list)
    status = quiz_view(rec_list, rec)
    if status == 1:
        dict._db.update_date(rec)



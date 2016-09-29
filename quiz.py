#import color
import show


def quiz_view(q_list, q_word):
    print('\033[1;38m_________\033[1;m')
    print('\033[1;30mTranslane --> \033[1;30m',end=' ')
    print('\033[1;35m{}\033[1;m'.format(q_word.word))
    i = 0
    qwe = {}
    for rec in q_list:
        qwe[rec] = i
        print(' \033[1;35m[{0}]\033[1;m {1}'.format(i, show.show_translation_word(rec.transfer)))
        i += 1
    text = input('\033[1;30m---> \033[1;30m')
    if int(text) == qwe[q_word]:
        print('\033[1;34m You was right\033[1;m')
        print('\033[1;38m_________\033[1;m')
        return 1
    if int(text) != qwe[q_word]:
        print('\033[1;41m ERROR\033[1;m')
        print('\033[1;38m_________\033[1;m')
        quiz_view(q_list, q_word)
    raise Exception('End Quiz')

def quiz_start(dict):
    rec_list = dict._db.oldest_records([])
    rec = dict._db.rand_rec(rec_list)
    status = quiz_view(rec_list, rec)
    if status == 1:
        # self._db.delete(rec)
        print('YOU A RIGHT')


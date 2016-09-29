#!/usr/bin/env python3
import sqlalchemy
import os
import datetime
import random
import const
import sys
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, ForeignKey
from sqlalchemy.orm import mapper, Session, sessionmaker


class DataBase():
    def __init__(self):
        self._engine = create_engine('sqlite:///' + os.path.join(os.path.dirname(__file__), 'db', 'DictionaryBD.db'), echo = False)
        metadata = MetaData()
        words_table = Table('users', metadata,
                         Column('id', Integer, primary_key=True, autoincrement=True),
                         Column('word', String),
                         Column('transfer', String),
                         Column('date', DateTime))
        metadata.create_all(self._engine)
        mapper(Word, words_table)
        session_init = sessionmaker(bind=self._engine)
        session_init.configure(bind=self._engine)
        self._session = session_init()

    def session_init(self):
        session_init = sessionmaker(bind = self._engine)
        session_init.configure(bind = self._engine)
        return session_init()

    def insert(self, text, translate):
        session = self._session
        current_date = datetime.datetime.now()
        words = Word(text, translate, current_date)
        session.add(words)
        session.commit()

    def select(self, text):
        session = self._session
        translations = session.query(Word).filter_by(word=text)
        for row in translations:
            print(row)

    def update_date(self, record):
        session = self._session
        current_date = datetime.datetime.now()
        rec_update = {'word': record.word, 'transfer': record.transfer, 'date': current_date}
        session.query(Word).filter_by(word = record.word, transfer = record.transfer, date = record.date).update(rec_update)
        session.commit()
        return 1

    def delete_word(self, rec):
        session = self._session
        session.query(Word).filter_by(word=rec).delete(synchronize_session=False)
        session.commit()

    def delete_all_word(self):
        session = self._session
        current_date = datetime.datetime.now()
        session.query(Word).delete(synchronize_session=False)
        session.commit()

    def pick_word(self):
        '''choose a random old record'''
        session = self._session
        all_records = session.query(Word).all()
        if len(all_records) < const.num_len:
            raise Exception('No words')
        oldest_rec = self.oldest_records([])
        for record in oldest_rec:
            print('@! {0}'.format(record))
        rand = self.rand_rec(oldest_rec)
        print('$ {}'.format(rand))
        return rand

    def pick_all_word(self, a):
        '''choose all record'''
        session = self._session
        if a == '-a' : return session.query(Word).order_by(Word.word).all()
        return session.query(Word).all()

    def rand_rec(self, pickable_record):
        """ pick one random record from the list of oldest"""
        return pickable_record[random.randint(0,len(pickable_record)-1)]

    def oldest_records(self, pickable_old_record):
        """gaining in the list of old records"""
        session = self._session
        all_records = session.query(Word).order_by(Word.date).all()
        for row in all_records:
            if (not(row.word in [rec.word for rec in pickable_old_record])) and (len(pickable_old_record)< const.num):
                pickable_old_record.append(row)
        while len(pickable_old_record) != const.quiz_list_len:
            row_skip_num = random.randint(0,len(pickable_old_record)-1)
            pickable_old_record.remove(pickable_old_record[row_skip_num])
        return pickable_old_record

    def filter_by_word(self, fword):
        session = self._session
        filtered_list_end = []
        for word in fword:
            filtered_list = session.query(Word).order_by(Word.date).filter_by(word = word)
            filtered_list_end +=filtered_list

        return filtered_list_end


class Word():
    def __init__(self, word, transfer, date):
        self.word = word
        self.transfer = transfer
        self.date = date

    def __repr__(self):
        return ("<Word: {0} - {1}: {2}>".format(self.word, self.transfer, self.date))


def test_your_self():
    db = DataBase()
    old_recs = db.oldest_records([])
    while True:
        text = input('! ')
        text = text.split()
        print(db.rand_rec(old_recs))

if __name__ == '__main__':
    print (sqlalchemy.__version__)
    test_your_self()



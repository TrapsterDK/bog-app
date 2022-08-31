import sqlite3
from dataclasses import dataclass
import decimal

@dataclass
class Book:
    titel: str
    price: decimal
    stock: int
    author: list
    genre: list

class Database(object):
    def __init__(self, filename="database.db"):
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor()

        self.create_table()

    def __del__(self):
        self.con.close()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cur.close()
        if isinstance(exc_value, Exception):
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()

        
    @staticmethod
    def _price_to_decimal(price):
        return decimal.Decimal(price) / decimal.Decimal(100)


    def create_table(self):
        #books
        self.cur.execute("""CREATE TABLE IF NOT EXISTS books
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titel STRING NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        );""")

        #genre
        self.cur.execute("""CREATE TABLE IF NOT EXISTS genre
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name STRING
        );""")
        
        #author
        self.cur.execute("""CREATE TABLE IF NOT EXISTS author
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name STRING
        );""")

        #book_to_author
        self.cur.execute("""CREATE TABLE IF NOT EXISTS book_to_author
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            author_id INTEGER
        );""")
        
        #book_to_genre
        self.cur.execute("""CREATE TABLE IF NOT EXISTS book_to_genre
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            genre_id INTEGER
        );""")
        
        self.con.commit()

    def add_book(self, book: Book):
        pass

    def get_book(self, book: Book):
        pass
    
    def get_books(self, ):
        pass
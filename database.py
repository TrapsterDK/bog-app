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
    id: int = None

    
@dataclass
class Book_Search_Query:
    titel: str = None
    author: list = None
    genre: list = None
    id: int = None

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
    def _int_to_decimal(integer):
        return decimal.Decimal(integer) / decimal.Decimal(100)

    @staticmethod
    def _decimal_to_int(dec):
        return int(decimal.Decimal(dec) * decimal.Decimal(100))

    def create_table(self):
        #transactions
        self.cur.execute("""CREATE TABLE IF NOT EXISTS transactions
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date INTEGER NOT NULL,
            book_id INTEGER NOT NULL
        );""")

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

    def get_book(self, id: int):
        pass
    
    def get_books(self, query: Book_Search_Query):
        pass

    def edit_book(self, id: int, book_new_info: Book):
        pass

    def sell_book(self, id: int):
        pass
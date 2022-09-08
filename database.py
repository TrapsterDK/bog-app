import sqlite3
from dataclasses import dataclass
import decimal
import time

@dataclass
class Book:
    title: str
    price: decimal
    stock: int
    authors: list[str]
    genres: list[str]
    id: int = None
    
@dataclass
class Book_Search_Query:
    title: str = None
    author: str = None
    genre: str = None
    id: int = None

@dataclass
class Transaction:
    book_id: int
    quantity: int = 1
    time: int = None
    id: int = None

class Database(object):
    def __init__(self, filename="database.db"):
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor()

        self._create_table()

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
    def _int_to_decimal(integer: int) -> decimal:
        return decimal.Decimal(integer) / decimal.Decimal(100)

    @staticmethod
    def _decimal_to_int(dec):
        return int(decimal.Decimal(dec) * decimal.Decimal(100))

    def _create_table(self):
        #books
        self.cur.execute("""CREATE TABLE IF NOT EXISTS books
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title STRING NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        );""")

        #genre
        self.cur.execute("""CREATE TABLE IF NOT EXISTS genres
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name STRING UNIQUE ON CONFLICT IGNORE
        );""")
        
        #author
        self.cur.execute("""CREATE TABLE IF NOT EXISTS authors
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name STRING UNIQUE ON CONFLICT IGNORE
        );""")
        
        #transactions
        self.cur.execute("""CREATE TABLE IF NOT EXISTS transactions
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            book_id INTEGER,
            FOREIGN KEY (book_id)
                REFERENCES books (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
        );""")

        #book_to_author
        self.cur.execute("""CREATE TABLE IF NOT EXISTS book_to_author
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (book_id)
                REFERENCES books (id) 
                ON UPDATE CASCADE
                ON DELETE CASCADE,
            FOREIGN KEY (author_id)
                REFERENCES authors (id) 
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );""")
        
        #book_to_genre
        self.cur.execute("""CREATE TABLE IF NOT EXISTS book_to_genre
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            FOREIGN KEY (book_id)
                REFERENCES books (id) 
                ON UPDATE CASCADE
                ON DELETE CASCADE,
            FOREIGN KEY (genre_id)
                REFERENCES genres (id) 
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );""")
        
        self.con.commit()

    def _insert_genres(self, genres: list[str]) -> list[str]:
        #insert genres if not exist
        genre_ids = []
        for genre in genres:
            self.cur.execute("""SELECT id FROM genres WHERE name = (?)""", (genre, ))
            select = self.cur.fetchone()
            if select is None:
                self.cur.execute("""INSERT INTO genres (name) VALUES (?)""", (genre, ))
                genre_ids.append(self.cur.lastrowid)
            else:
                genre_ids.append(select[0])
        return genre_ids

        
    def _insert_authors(self, authors: list[str]) -> list[str]:
        author_ids = []
        for author in authors:
            self.cur.execute("""SELECT id FROM authors WHERE name = (?)""", (author, ))
            select = self.cur.fetchone()
            if select is None:
                self.cur.execute("""INSERT INTO authors (name) VALUES (?)""", (author, ))
                author_ids.append(self.cur.lastrowid)
            else:
                author_ids.append(select[0])
        return author_ids

    def add_books(self, books: list[Book]) -> None:
        for book in books:
            #insert book
            self.cur.execute("""INSERT INTO books(title, price, stock) VALUES(?, ?, ?)""", (book.title, self._decimal_to_int(book.price), book.stock, ))
            book_id = self.cur.lastrowid

            #insert new genres and authors
            author_ids = self._insert_authors(book.authors)
            genre_ids = self._insert_genres(book.genres)

            #insert new genres and authors to book_to_author and book_to_genre
            self.cur.executemany("""INSERT INTO book_to_author(book_id, author_id) VALUES(?, ?)""", [(book_id, author_id,) for author_id in author_ids])
            self.cur.executemany("""INSERT INTO book_to_genre(book_id, genre_id) VALUES(?, ?)""", [(book_id, genre_id,) for genre_id in genre_ids])

        self.con.commit()
    
    #get single book by id
    def get_book(self, id: int) -> Book:
        self.cur.execute("""SELECT books.id, books.title, books.price, books.stock, group_concat(authors.name), group_concat(genres.name) FROM books
        LEFT JOIN book_to_author ON books.id = book_to_author.book_id
        LEFT JOIN book_to_genre ON books.id = book_to_genre.book_id
        JOIN authors ON book_to_author.author_id = authors.id
        JOIN genres ON book_to_genre.genre_id = genres.id
        WHERE books.id = (?)
        GROUP BY books.id""", (id,))
        select = self.cur.fetchone()
        if select is None:
            return None
        return Book(select[1], self._int_to_decimal(select[2]), select[3], select[4].split(","), select[5].split(","), select[0])

    #get list of books by search query
    def get_books(self, query: Book_Search_Query, limit:int=25, offset:int=0) -> list[Book]:
        #get books using search params title, author, genre and id and ignore the query if they are none using group_concat to get all authors and genres without duplicates with DISTINCT
        self.cur.execute("""SELECT books.id, books.title, books.price, books.stock, group_concat(authors.name), group_concat(genres.name) FROM books
        LEFT JOIN book_to_author ON books.id = book_to_author.book_id
        LEFT JOIN book_to_genre ON books.id = book_to_genre.book_id
        JOIN authors ON book_to_author.author_id = authors.id
        JOIN genres ON book_to_genre.genre_id = genres.id
        WHERE instr(books.title, IFNULL((?), '')) > 0
        AND instr(authors.name, IFNULL((?), '')) > 0
        AND instr(genres.name, IFNULL((?), '')) > 0
        AND instr(books.id, IFNULL((?), '')) > 0
        GROUP BY books.id
        LIMIT (?) OFFSET (?)""", (query.title, query.author, query.genre, query.id, limit,offset,))
        select = self.cur.fetchall()
        if select is None:
            return None
        return [Book(row[1], self._int_to_decimal(row[2]), row[3], row[4].split(","), row[5].split(","), row[0]) for row in select]

    def edit_book(self, book_id: int, book_new_info: Book) -> None:
        #error check in case book does not exist
        if(self.get_book(id) == None):
            raise ValueError("Book not found")

        #update book info
        self.cur.execute("""UPDATE books SET title = (?), price = (?), stock = (?) WHERE id = (?)""", 
        (book_new_info.title, self._decimal_to_int(book_new_info.price), book_new_info.stock, book_id, ))
        
        #delete old genres and authors
        self.cur.execute("""DELETE FROM book_to_author WHERE book_id = (?)""", (book_id, ))
        self.cur.execute("""DELETE FROM book_to_genre WHERE book_id = (?)""", (book_id, ))

        #insert new genres and authors
        author_ids = self._insert_authors(book_new_info.authors)
        genre_ids = self._insert_genres(book_new_info.genres)

        #insert new genres and authors to book_to_author and book_to_genre
        self.cur.executemany("""INSERT INTO book_to_author(book_id, author_id) VALUES(?, ?)""", [(book_id, author_id,) for author_id in author_ids])
        self.cur.executemany("""INSERT INTO book_to_genre(book_id, genre_id) VALUES(?, ?)""", [(book_id, genre_id,) for genre_id in genre_ids])

        self.con.commit()

    #time is unix timestamp in seconds, if transaction time is None it will be set to current time
    def sell_book(self, transaction:Transaction) -> None:
        #error check in case book does not exist or out of stock
        book = self.get_book(transaction.book_id)
        if(book == None):
            raise ValueError("Book not found")
        elif(book.stock-transaction.quantity < 0):
            raise ValueError(f"Only {book.stock} left in stock, cannot sell {transaction.quantity}")

        #update stock
        self.cur.execute("""UPDATE books SET stock = stock - (?) WHERE id = (?)""", (transaction.quantity, transaction.book_id, ))

        if(transaction.time == None):
            transaction.time = int(time.time())

        #add transaction
        self.cur.execute("""INSERT INTO transactions(date, book_id, quantity, price) VALUES(?, ?, ?, ?)""", (transaction.time, transaction.book_id, transaction.quantity, self._decimal_to_int(book.price),))

        self.con.commit()

if __name__ == "__main__":
    with Database() as db:
        db.add_books([Book("test" + str(i), 100, 10, ["test"], ["test"]) for i in range(1, 1000)])
        #print(db.get_books(Book_Search_Query(id=93), offset=1, limit=5))
        #db.get_books(Book_Search_Query(id=93))
        #print(db.sell_book(153, 2, 100))
        
        pass 
import sqlite3
from dataclasses import dataclass
import decimal
import time
import json
from enum import Enum
from typing import Callable, Optional
from os.path import exists


@dataclass
class MinBook:
    title:              str
    authors:            Optional[list[str]] = None
    group:              Optional[str] = None
    product_code:       Optional[int] = None
    id:                 Optional[int] = None


@dataclass
class Book:
    title:              str
    price:              Optional[decimal.Decimal] = None
    stock:              Optional[int] = None
    age:                Optional[str] = None
    authors:            Optional[list[str]] = None
    binding:            Optional[str] = None
    brand:              Optional[str] = None
    dimensions:         Optional[str] = None
    edition:            Optional[int] = None
    editor:             Optional[str] = None
    exam:               Optional[str] = None
    group:              Optional[str] = None
    image:              Optional[str] = None
    imprint:            Optional[str] = None
    isbn10:             Optional[int] = None
    isbn13:             Optional[int] = None
    language:           Optional[str] = None
    model:              Optional[int] = None
    pages:              Optional[int] = None
    product_code:       Optional[int] = None
    publication_month:  Optional[str] = None
    publication_year:   Optional[int] = None
    publisher:          Optional[str] = None
    series:             Optional[str] = None
    type_:              Optional[str] = None
    university:         Optional[str] = None
    weight:             Optional[int] = None
    id:                 Optional[int] = None


def Book_to_MinBook(book: Book) -> MinBook:
    return MinBook(
        title=          book.title,
        authors=        book.authors,
        group=          book.group,
        product_code=   book.product_code,
        id=             book.id
    )


def MinBook_to_Book(book_min: MinBook) -> Book:
    return Book(
        title=          book_min.title,
        authors=        book_min.authors,
        group=          book_min.group,
        product_code=   book_min.product_code,
        id=             book_min.id
    )


@dataclass
class Book_Search_Query:
    title:              Optional[str] = None
    author:             Optional[str] = None
    group:              Optional[str] = None
    product_code:       Optional[int] = None


@dataclass
class Transaction:
    book_id:            int
    quantity:           int
    time:               Optional[int] = None
    id:                 Optional[int] = None


#column, 0 for descending 1 for ascending
class sort_by(Enum):
    product_code_desc = ("books.product_code",  0)
    product_code_asc =  ("books.product_code",  1)
    group_desc =        ("group_.name",          0)
    group_asc =         ("group_.name",          1)
    author_desc =       ("author.name",         0)
    author_asc =        ("author.name",         1)
    title_desc =        ("books.title",         0)
    title_asc =         ("books.title",         1)


# alot of sus sql https://www.sqlite.org/windowfunctions.html
_SQL_SELECT_MINBOOK = """
SELECT 
books.id,
books.title,
group_concat(author.name),
group_.name,
books.product_code"""


_SQL_SELECT_BOOK = _SQL_SELECT_MINBOOK + """,
books.age,
binding.name,
brand.name,
books.dimensions,
books.edition,
editor.name,
exam.name,
group_.name,
books.image,
imprint.name,
books.isbn10,
books.isbn13,
language.name,
books.model,
books.pages,
books.price,
month.name,
books.publication_year,
publisher.name,
series.name,
type.name,
university.name,
books.weight,
books.stock"""


_SQL_JOIN_MINBOOK = """
LEFT JOIN group_ ON group_.id = books.group_id

LEFT JOIN book_author ON books.id = book_author.book_id
LEFT JOIN author ON book_author.author_id = author.id
"""


_SQL_JOIN_BOOK = _SQL_JOIN_MINBOOK + """
LEFT JOIN binding ON binding.id = books.binding_id
LEFT JOIN brand ON brand.id = books.brand_id
LEFT JOIN editor ON editor.id = books.editor_id
LEFT JOIN exam ON exam.id = books.exam_id
LEFT JOIN imprint ON imprint.id = books.imprint_id
LEFT JOIN language ON language.id = books.language_id
LEFT JOIN month ON month.id = books.publication_month_id
LEFT JOIN publisher ON publisher.id = books.publisher_id
LEFT JOIN series ON series.id = books.series_id
LEFT JOIN type ON type.id = books.type_id
LEFT JOIN university ON university.id = books.university_id
"""


_SQL_WHERE_ID = """
WHERE books.id = ?
LIMIT 1
"""


def _sql_is_null(string: str, index:int) -> str:
    return f"(?{index} IS NULL OR " + string + ")"

# check if str value is in column
def _sql_instr_str(name: str, index: int) -> str:
    return _sql_is_null(f"instr(LOWER({name}), LOWER(?{index})) > 0", index)

# check if int value is in column
def _sql_instr_int(name: str, index: int) -> str:
    return _sql_is_null(f"instr({name}, ?{index}) > 0", index)


_SQL_WHERE_QUERY = """
WHERE """ + "\nAND ".join(
    [to_query(column, i) for i, (to_query, column) in 
        enumerate([
            (_sql_instr_str, "books.title"),
            (_sql_instr_str, "author.name"),
            (_sql_instr_str, "group_.name"),
            (_sql_instr_int, "books.product_code")], 
        start=1)]) + """
        
GROUP BY books.id
ORDER BY {} COLLATE NOCASE {} NULLS {}
LIMIT (?) OFFSET (?) """


_SQL_FROM = """
FROM books
"""


_SQL_SELECT_MINBOOK_ID_FULL =       _SQL_SELECT_MINBOOK +   _SQL_FROM + _SQL_JOIN_MINBOOK + _SQL_WHERE_ID
_SQL_SELECT_BOOK_ID_FULL =          _SQL_SELECT_BOOK +      _SQL_FROM + _SQL_JOIN_BOOK +    _SQL_WHERE_ID
_SQL_SELECT_MINBOOK_QUERY_FULL =    _SQL_SELECT_MINBOOK +   _SQL_FROM + _SQL_JOIN_MINBOOK + _SQL_WHERE_QUERY
_SQL_SELECT_BOOK_QUERY_FULL =       _SQL_SELECT_BOOK +      _SQL_FROM + _SQL_JOIN_BOOK +    _SQL_WHERE_QUERY


_DEFAULT_SORT_BY = sort_by.product_code_desc
_DEFAULT_SEARH_LIMIT = 50


class Database(object):
    # INITIALIZE AND DEINITIALIZE  
    def __init__(self, filename="database.db"):
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor()

        self._create_tables()

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
    # INITIALIZE AND DEINITIALIZE  

    # price convertion
    @staticmethod
    def _int_to_decimal(integer: int) -> decimal.Decimal | None:
        if integer is None:
            return None

        return decimal.Decimal(integer) / decimal.Decimal(100)

    @staticmethod
    def _decimal_to_int(dec: decimal.Decimal) -> int | None:
        if dec is None:
            return None

        return int(decimal.Decimal(dec) * decimal.Decimal(100))


    # insert something into a table and get id no matter if it exists or not
    # returns if unique_value is None
    def _insert_or_ignore(self, table: str, unique_column: str, unique_value: str) -> int:
        if(unique_value is None): 
            return None
            
        self.cur.execute(f"""SELECT id FROM {table} WHERE {unique_column} = (?)""", (unique_value, ))
        select = self.cur.fetchone()

        if select:
            return select[0]

        self.cur.execute(f"""INSERT INTO {table} ({unique_column}) VALUES (?)""", (unique_value,))
        return self.cur.lastrowid

    # _insert_or_ignore for list
    def _insert_or_ignore_list(self, table: str, unique_column: str, unique_values: list[str]) -> list[int]:
        if(unique_values is None): 
            return []
        
        ids = []
        for value in unique_values:
            ids.append(self._insert_or_ignore(table, unique_column, value))
        return ids


    # insert into a many to many table
    def _insert_many_to_many(self, many_table: str, many_column_single: str, many_column_list: str, single_id: int, list_id: list[int]) -> None:
        self.cur.executemany(f"""INSERT INTO {many_table} ({many_column_single}, {many_column_list}) VALUES (?, ?)""", [(single_id, id,) for id in list_id])

    # delete from a many to many table
    def _delete_many_to_many(self, many_table: str, column: str, where_value: int) -> None:
        self.cur.execute(f"""DELETE FROM {many_table} WHERE {column} = (?)""", (where_value,))


    # check if id exists in table
    def _id_exist(self, table: str, id: int) -> bool:
        self.cur.execute(f"""SELECT id FROM {table} WHERE id = (?)""", (id, ))

        if self.cur.fetchone() is None: 
            return False

        return True
    
            
    @staticmethod
    def _row_to_minbook(row: list) -> MinBook:
        return MinBook(
            id =                row[0],
            title =             row[1],
            authors =           row[2].split(',') if row[2] else None,
            group =             row[3],
            product_code =      row[4]
        )

    @staticmethod
    def _row_to_book(row: list) -> Book:
        minbook = Database._row_to_minbook(row)
        book = MinBook_to_Book(minbook)

        book.age =               row[5]
        book.binding =           row[6] 
        book.brand =             row[7]
        book.dimensions =        row[8]
        book.edition =           row[9]
        book.editor =            row[10]    
        book.exam =              row[11]
        book.group =             row[12]
        book.image =             row[13]
        book.imprint =           row[14]    
        book.isbn10 =            row[15]
        book.isbn13 =            row[16]
        book.language =          row[17]    
        book.model =             row[18]
        book.pages =             row[19]    
        book.price =             Database._int_to_decimal(row[20])
        book.publication_month = row[21]
        book.publication_year =  row[22]
        book.publisher =         row[23]
        book.series =            row[24]
        book.type_ =             row[25]
        book.university =        row[26]
        book.weight =            row[27]    
        book.stock =             row[28]

        return book


    def _create_tables(self) -> None:
        # master tables
        self.cur.execute("""CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            binding_id INTEGER,
            brand_id INTEGER,
            dimensions TEXT,
            edition INTEGER,
            editor_id INTEGER,
            exam_id INTEGER,
            group_id INTEGER,
            image TEXT,
            imprint_id INTEGER,
            isbn10 INTEGER,
            isbn13 INTEGER,
            language_id INTEGER,
            model INTEGER,
            title TEXT NOT NULL, 
            pages INTEGER,
            price INTEGER,
            product_code INTEGER,
            publication_month_id INTEGER,
            publication_year INTEGER,
            publisher_id INTEGER,
            series_id INTEGER,
            type_id INTEGER,
            university_id INTEGER,  
            weight INTEGER,
            stock INTEGER,

            FOREIGN KEY (binding_id)
                REFERENCES binding (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (brand_id)
                REFERENCES brand (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (editor_id)
                REFERENCES editor (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (exam_id)
                REFERENCES exam (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (group_id)
                REFERENCES group_ (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (imprint_id)
                REFERENCES imprint (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (language_id)
                REFERENCES language (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (publication_month_id)
                REFERENCES month (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (publisher_id)
                REFERENCES publisher (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (series_id)
                REFERENCES series (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (type_id)
                REFERENCES type (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (university_id)
                REFERENCES university (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            book_id INTEGER,

            FOREIGN KEY (book_id)
                REFERENCES books (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
            )""")

        # many to one
        self.cur.execute("""CREATE TABLE IF NOT EXISTS author(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            info TEXT
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS binding(
            id INTEGER PRIMARY KEY AUTOINCREMENT,   
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS brand(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS editor(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS exam(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS group_(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS imprint(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS language(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS month(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS publisher(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS series(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS type(
            id INTEGER PRIMARY KEY AUTOINCREMENT,   
            name TEXT NOT NULL UNIQUE
            )""")
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS university(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )""")

        #many to many
        self.cur.execute("""CREATE TABLE IF NOT EXISTS book_author(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            
            FOREIGN KEY (book_id)
                REFERENCES books (id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
            FOREIGN KEY (author_id)
                REFERENCES author (id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
            )""")

        self.con.commit()


    def add_book(self, book: Book) -> None:
        self.add_books([book])

    def add_books(self, books: list[Book]) -> None:
        for book in books:
            # insert book parameters alphabetically
            self.cur.execute("""INSERT INTO books (
                age,
                binding_id,
                brand_id,
                dimensions,
                edition,
                editor_id,
                exam_id,
                group_id,
                image,
                imprint_id,
                isbn10,
                isbn13,
                language_id,
                model,
                title,
                pages,
                price,
                product_code,
                publication_month_id,
                publication_year,
                publisher_id,
                series_id,
                type_id,
                university_id,
                weight,
                stock
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                book.age,
                self._insert_or_ignore("binding", "name", book.binding),
                self._insert_or_ignore("brand", "name", book.brand),
                book.dimensions,
                book.edition,
                self._insert_or_ignore("editor", "name", book.editor),
                self._insert_or_ignore("exam", "name", book.exam),
                self._insert_or_ignore("group_", "name", book.group),
                book.image,
                self._insert_or_ignore("imprint", "name", book.imprint),
                book.isbn10,    
                book.isbn13,
                self._insert_or_ignore("language", "name", book.language),
                book.model,
                book.title,
                book.pages,
                self._decimal_to_int(book.price),
                book.product_code,
                self._insert_or_ignore("month", "name", book.publication_month),
                book.publication_year,
                self._insert_or_ignore("publisher", "name", book.publisher),
                self._insert_or_ignore("series", "name", book.series),
                self._insert_or_ignore("type", "name", book.type_),
                self._insert_or_ignore("university", "name", book.university),
                book.weight,
                book.stock))

            book_id = self.cur.lastrowid

            author_ids = self._insert_or_ignore_list("author", "name", book.authors)
            self._insert_many_to_many("book_author", "book_id", "author_id", book_id, author_ids)
        
        self.con.commit()


    # internal book getter from query
    def _get_book(self, query: str, args: tuple, row_to_book: Callable) -> Book | MinBook:
        self.cur.execute(query, args)

        row = self.cur.fetchone()

        if row is None: 
            return None

        return row_to_book(row)

    # get book by exact id
    def get_book(self, id: int) -> Book:
        return self._get_book(_SQL_SELECT_BOOK_ID_FULL, (id,), self._row_to_book)
        
    # get minbook by exact id
    def get_minbook(self, id: int) -> MinBook:
        return self._get_book(_SQL_SELECT_MINBOOK_ID_FULL, (id,), self._row_to_minbook)


    # internal book getter from query
    def _get_books_query(self, sql_query: str, query: Book_Search_Query, sort: sort_by, limit: int, offset: int, row_to_book: Callable) -> list[Book | MinBook]:
        #execute query
        self.cur.execute(sql_query.format(sort.value[0], *(("ASC", "LAST") if sort.value[1] == 1 else ("DESC", "FIRST"))), 
            (query.title, query.author, query.group, query.product_code, limit, offset))
            
        return [row_to_book(row) for row in self.cur]

    # get list of books by search query
    def get_books(self, query: Book_Search_Query, sort: sort_by = _DEFAULT_SORT_BY, limit: int = _DEFAULT_SEARH_LIMIT, offset: int = 0) -> list[Book]: 
        return self._get_books_query(_SQL_SELECT_BOOK_QUERY_FULL, query, sort, limit, offset, self._row_to_book)

    # get list of minbooks by search query
    def get_minbooks(self, query: Book_Search_Query, sort: sort_by = _DEFAULT_SORT_BY, limit: int = _DEFAULT_SEARH_LIMIT, offset: int = 0) -> list[MinBook]:
        return self._get_books_query(_SQL_SELECT_MINBOOK_QUERY_FULL, query, sort, limit, offset, self._row_to_minbook)


    # uses book id to update book
    def edit_book(self, book: Book) -> None:
        # serror check in case book does not exist
        if (not self._id_exist("books", book.id)):
            raise ValueError("Book not found")
        
        # update book info
        self.cur.execute("""UPDATE books SET
            age = ?,
            binding_id = ?,
            brand_id = ?,
            dimensions = ?,
            edition = ?,
            editor_id = ?,
            exam_id = ?,
            group_id = ?,
            image = ?,
            imprint_id = ?,
            isbn10 = ?,
            isbn13 = ?,
            language_id = ?,
            model = ?,
            title = ?,
            pages = ?,
            price = ?,
            product_code = ?,
            publication_month_id = ?,
            publication_year = ?,
            publisher_id = ?,
            series_id = ?,
            type_id = ?,
            university_id = ?,
            weight = ?,
            stock = ?
            WHERE id = ?""", (
            book.age,
            self._insert_or_ignore("binding", "name", book.binding),
            self._insert_or_ignore("brand", "name", book.brand),
            book.dimensions,
            book.edition,
            self._insert_or_ignore("editor", "name", book.editor),
            self._insert_or_ignore("exam", "name", book.exam),
            self._insert_or_ignore("group_", "name", book.group),
            book.image,
            self._insert_or_ignore("imprint", "name", book.imprint),
            book.isbn10,    
            book.isbn13,
            self._insert_or_ignore("language", "name", book.language),
            book.model,
            book.title,
            book.pages,
            self._decimal_to_int(book.price),
            book.product_code,
            self._insert_or_ignore("month", "name", book.publication_month),
            book.publication_year,
            self._insert_or_ignore("publisher", "name", book.publisher),
            self._insert_or_ignore("series", "name", book.series),
            self._insert_or_ignore("type", "name", book.type_),
            self._insert_or_ignore("university", "name", book.university),
            book.weight,
            book.stock,
            book.id))
            
        self._delete_many_to_many("book_author", "book_id", book.id)
        author_ids = self._insert_or_ignore_list("author", "name", book.authors)
        self._insert_many_to_many("book_author", "book_id", "author_id", book.id, author_ids)

        self.con.commit()


    # time is unix timestamp in seconds, if transaction time is None it will be set to current time
    def sell_book(self, transaction: Transaction) -> None:
        # error check in case book does not exist or out of stock
        book = self.get_book(transaction.book_id)
        if (book is None):
            raise ValueError("Book not found")
        elif (book.stock-transaction.quantity < 0):
            raise ValueError(f"Only {book.stock} left in stock, cannot sell {transaction.quantity}")

        # update stock
        self.cur.execute("""UPDATE books SET stock = stock - (?) WHERE id = (?)""", (transaction.quantity, transaction.book_id, ))

        if (transaction.time is None):
            transaction.time = int(time.time())

        # add transaction
        self.cur.execute("""INSERT INTO transactions(date, book_id, quantity, price) VALUES(?, ?, ?, ?)""",
            (transaction.time, transaction.book_id, transaction.quantity, self._decimal_to_int(book.price),))

        self.con.commit()


# load database from json file
def _load_data_from_final_json(db: Database, name: str) -> None:
    with open(name, encoding="utf-8") as f:
        books = []
        data = json.load(f)

        for book in data['Books']:
            books.append(Book(
                age = book['Age'],
                authors = book['Author'],
                binding = book['Binding'],
                brand = book['Brand'],
                dimensions = book['Dimensions (L X B X H)'],
                edition = book['Edition'],
                editor = book['Editor'],
                exam = book['Exam'],
                group = book['Group'],
                image = book['Image'],
                imprint = book['Imprint'],
                isbn10 = book['ISBN_10'],
                isbn13 = book['ISBN_13'],
                language = book['Language'],
                model = book['Model'],
                title = book['Name'],
                pages = book['Pages'],
                price = book['Price'],
                product_code = book['Product_Code_2'],
                publication_month = book['Publication_Month'],
                publication_year = book['Publication_Year'],
                publisher = book['Publisher'],
                series = book['Series_Name'],
                type_ = book['Type'],
                university = book['University'],
                weight = book['Weight_Gram'],
                stock = 0))
        db.add_books(books)


if __name__ == "__main__":
    exist = not exists('database.db')
    with Database() as db:
        if(exist):
            _load_data_from_final_json(db, "final.json")

        book = db.get_book(2)
        print(book)
        
        #book.authors = ["Heynig", "Stic", "WIFI"]
        #db.edit_book(book)
        #print(db.get_book(2))

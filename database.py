import sqlite3
from dataclasses import dataclass
import decimal
import time
import json

@dataclass
class BookMin:
    title: str
    author: str = None
    genre: str = None
    product_code: int = None
    id: int = None

@dataclass
class Book:
    title: str
    price: decimal
    stock: int
    age: str = None
    author: str = None
    binding: str = None
    brand: str = None
    dimensions: str = None
    edition: int = None
    editor: str = None
    exam: str = None
    group:str = None
    image: str = None
    imprint: str = None
    isbn10: int = None
    isbn13: int = None
    language: str = None
    model: int = None
    pages: int = None
    product_code: int = None
    publication_month: str = None
    publication_year: int = None
    publisher: str = None
    series: str = None
    type_: str = None
    university: str = None
    weight: int = None
    genre: str = None
    id: int = None

def Book_to_BookMin(book: Book):
    book_min = BookMin(
        title=book.title, 
        author=book.author, 
        genre=book.genre, 
        product_code=book.product_code, 
        id=book.id)
    return book_min

def BookMin_to_Book(book_min: BookMin):
    book = Book(
        title=book_min.title, 
        author=book_min.author, 
        genre=book_min.genre, 
        product_code=book_min.product_code, 
        id=book_min.id)
    return book
    
@dataclass
class Book_Search_Query:
    title: str = None
    author: str = None
    genre: str = None
    product_code: int = None
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
        self.cur.execute("""CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            author_id INTEGER,
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
            genre_id INTEGER,
            stock INTEGER,

            FOREIGN KEY (author_id)
                REFERENCES author (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
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
                ON DELETE SET NULL,
            FOREIGN KEY (genre_id)
                REFERENCES genre (id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
            )""")
            
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
            
        self.cur.execute("""CREATE TABLE IF NOT EXISTS genre(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
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

        self.con.commit()

    #insert something into a table and get id no matter if it exists or not
    #returns if unique_value is None
    def _insert_or_ignore(self, table: str, unique_column: str, unique_value: str, other_columns:list[str] = None, other_values: list[str] = None) -> int:
        if(unique_value is None): return None
        self.cur.execute(f"""SELECT id FROM {table} WHERE {unique_column} = (?)""", (unique_value, ))
        select = self.cur.fetchone()

        if select is None:
            columns = [unique_column]
            if other_columns != None: columns.extend(other_columns)
            values = [unique_value]
            if other_values != None: values.extend(other_values)

            self.cur.execute(f"""INSERT INTO {table} ({", ".join(columns)}) VALUES ({", ".join(["?"] * len(values))})""", values)
            return self.cur.lastrowid
        return select[0]

    def add_book(self, book: Book) -> None:
        self.add_books([book])

    def add_books(self, books: list[Book]) -> None:
        for book in books:
            #insert book parameters alphabetically
            self.cur.execute("""INSERT INTO books (
                age,
                author_id,
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
                genre_id,
                stock
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                book.age,
                self._insert_or_ignore("author", "name", book.author),
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
                self._insert_or_ignore("genre", "name", book.genre),
                book.stock
                ))
        
        self.con.commit()

    def get_book(self, query: Book_Search_Query, offset:int=0) -> Book:
        books = self.get_books(query, 1, offset)
        if books:
            return books[0]
        return None

    #get list of books by search query
    #Book_Search_Query id is used as exact match, all other parameters are used as LIKE
    def get_books(self, query: Book_Search_Query, limit:int=25, offset:int=0) -> list[Book]:
        self.cur.execute(f"""SELECT 
            books.id,
            books.age,
            author.name,
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
            books.title,
            books.pages,
            books.price,
            books.product_code,
            month.name,
            books.publication_year,
            publisher.name,
            series.name,
            type.name,
            university.name,
            books.weight,
            genre.name,
            books.stock
            FROM books

            LEFT JOIN author ON author.id = books.author_id
            LEFT JOIN binding ON binding.id = books.binding_id
            LEFT JOIN brand ON brand.id = books.brand_id
            LEFT JOIN editor ON editor.id = books.editor_id
            LEFT JOIN exam ON exam.id = books.exam_id
            LEFT JOIN group_ ON group_.id = books.group_id
            LEFT JOIN imprint ON imprint.id = books.imprint_id
            LEFT JOIN language ON language.id = books.language_id
            LEFT JOIN month ON month.id = books.publication_month_id
            LEFT JOIN publisher ON publisher.id = books.publisher_id
            LEFT JOIN series ON series.id = books.series_id
            LEFT JOIN type ON type.id = books.type_id
            LEFT JOIN university ON university.id = books.university_id
            LEFT JOIN genre ON genre.id = books.genre_id
            
            WHERE ((?1) IS NULL OR instr(LOWER(books.title), LOWER(?1)) > 0)
            AND   ((?2) IS NULL OR instr(LOWER(author.name), LOWER(?2)) > 0)
            AND   ((?3) IS NULL OR instr(LOWER(genre.name), LOWER(?3)) > 0)
            AND   ((?4) IS NULL OR instr(books.product_code, (?4)) > 0)
            AND   ((?5) IS NULL OR books.id = (?5))
            GROUP BY books.id
            LIMIT (?) OFFSET (?)""", (query.title, query.author, query.genre, query.product_code, query.id, limit, offset))
        
        books = []
        for book in self.cur:
            books.append(Book(
                id=book[0],
                age=book[1],
                author=book[2],
                binding=book[3],
                brand=book[4],
                dimensions=book[5],
                edition=book[6],
                editor=book[7],
                exam=book[8],
                group=book[9],
                image=book[10],
                imprint=book[11],
                isbn10=book[12],
                isbn13=book[13],
                language=book[14],
                model=book[15],
                title=book[16],
                pages=book[17],
                price=self._int_to_decimal(book[18]),
                product_code=book[19],
                publication_month=book[20],
                publication_year=book[21],
                publisher=book[22],
                series=book[23],
                type_=book[24],
                university=book[25],
                weight=book[26],
                genre=book[27],
                stock=book[28]
            ))
        return books

    #uses book id to update book
    def edit_book(self, book: Book) -> None:
        #error check in case book does not exist
        if(self.get_books(Book_Search_Query(id=book.id)) == None):
            raise ValueError("Book not found")

        #update book info
        self.cur.execute("""UPDATE books SET
            age = ?,
            author_id = ?,
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
            genre_id = ?,
            stock = ?
            WHERE id = ?""", (
            book.age,
            self._insert_or_ignore("author", "name", book.author),
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
            self._insert_or_ignore("genre", "name", book.genre),
            book.stock,
            book.id
            ))

        self.con.commit()

    #time is unix timestamp in seconds, if transaction time is None it will be set to current time
    def sell_book(self, transaction:Transaction) -> None:
        #error check in case book does not exist or out of stock
        book = self.get_book(Book_Search_Query(id=transaction.book_id))
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

def load_data_from_final_json(db, name):
    with open(name) as f:
        books = []
        data = json.load(f)

        for book in data['Books']:
            if(book['Product_Code_1'] == None): print(book)
            books.append(Book(
            age = book['Age'],
            author = book['Author'],
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
    with Database() as db:
        #load_data_from_final_json(db, "final.json")
        '''
        print(db.get_book(Book_Search_Query(id=141, title="cand")))
        book = db.get_book(Book_Search_Query(id=141, title="cand"))
        book.stock = 10
        db.edit_book(book)

        db.sell_book(Transaction(book_id=141, quantity=1))
        '''
        pass
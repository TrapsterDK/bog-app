

from dataclasses import dataclass
import json
from typing import Optional

@dataclass
class Book:
    title:              str
    authors:            Optional[list[str]] = None
    group:              Optional[str] = None
    product_code:       Optional[int] = None
    price:              Optional[int] = None
    stock:              Optional[int] = None
    id:                 Optional[int] = None

# load database from json file
def _load_data_to_book(db, name: str) -> None:
    with open(name, encoding="utf-8") as f:
        books = []

        data =json.load(f)
        for book in data['Books']:
            books.append(Book(
                authors = book['Author'],
                group = book['Group'],
                title = book['Name'],
                product_code = book['Product_Code_2'],
                price = book['Price'],
                stock = 0))

        # ADD BOOKS TIL DATABASE
        db.add_books(books)
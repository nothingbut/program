from fastapi import FastAPI, Path
import csv
from pydantic import BaseModel
from bsconfig import BookShelfConfig
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

class Book(BaseModel):
    id: str
    title: str
    author: str = ''
    description: str = ''
    category: str
    subcategory: str

class Category(BaseModel):
    id: int
    name: str
    subcategories: set

with open('%s/shelf.csv' % BookShelfConfig().getBookShelf(), 'r') as f:
    reader = csv.DictReader(f)
    books = []
    categories = dict()

    for row in reader:
        book = Book(**row)
        books.append(book)
        if book.category in categories.keys():
            category = categories.get(book.category)
            category.subcategories.add(book.subcategory)
        else:
            subcategories = set()
            subcategories.add(book.subcategory)
            category = Category(**{'id': len(categories), 'name': book.category,'subcategories': subcategories})
            categories.setdefault(book.category, category)

    for category in categories.values():
        print(category)

@app.get("/books/")
async def read_books():
    return {"data": [book.dict() for book in books]}

@app.get("/books/{book_id}")
async def read_book(book_id: str = Path(...)):
    return {"data": [book for book in books if book.id == book_id]}

@app.get("/categories/")
async def read_categories():
    return {"data": [category.dict() for category in categories.values()]}

@app.get("/categories/{category_id}")
async def read_category(category_id: int = Path(...)):
    for category in categories.values():
        print(category)
    return {"data": [category for category in categories.values() if category.id == category_id]}

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

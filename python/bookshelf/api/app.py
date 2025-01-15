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
    cat: str
    sub: str

class Category(BaseModel):
    id: int
    name: str

with open('%s/shelf.csv' % BookShelfConfig().getBookShelf(), 'r') as f:
    reader = csv.DictReader(f)
    books = []
    categories = []
    current_category = None
    for row in reader:
        book = Book(**row)
        books.append(book)

        if not current_category or book.cat != current_category:
            current_category = book.cat 
            categories.append(Category(id=len(categories), name=current_category))
    categories.sort(key=lambda x: x.id)
    
@app.get("/books/{book_id}")
# Load CSV data into memory

# Routes

@app.get("/books/")
async def read_books():
    return {"data": [book.dict() for book in books]}

@app.get("/categories/")
async def read_categories():
    return {"data": [cat.dict() for cat in categories]}

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
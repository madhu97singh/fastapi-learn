import os

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:secret@localhost:3306/fastapi_learn"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)


class Item(BaseModel):
    name: str
    price: float
    description: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None


class ItemOut(Item):
    id: int

    model_config = ConfigDict(from_attributes=True)


app = FastAPI(title="Learn FastAPI")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/contact-us")
def contact():
    return "contact us"


@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(ItemDB).all()


@app.get("/items/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ItemDB, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: Item, db: Session = Depends(get_db)):
    new_item = ItemDB(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.put("/items/{item_id}", response_model=ItemOut)
def replace_item(item_id: int, item: Item, db: Session = Depends(get_db)):
    stored = db.get(ItemDB, item_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.model_dump().items():
        setattr(stored, field, value)
    db.commit()
    db.refresh(stored)
    return stored


@app.patch("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, changes: ItemUpdate, db: Session = Depends(get_db)):
    stored = db.get(ItemDB, item_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(stored, field, value)
    db.commit()
    db.refresh(stored)
    return stored


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ItemDB, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

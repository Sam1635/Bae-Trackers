from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Product
import database_models
from database import engine, session
import os

app = FastAPI()

# -------------------------------
# CORS CONFIG (Netlify + Local)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# DATABASE STARTUP INIT
# -------------------------------
@app.on_event("startup")
def startup_db():
    database_models.Base.metadata.create_all(bind=engine)

    db = session()
    try:
        count = db.query(database_models.Product).count()
        if count == 0:
            products = [
                Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
                Product(id=2, name="Laptop", description="A powerful laptop", price=999.99, quantity=30),
                Product(id=3, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
                Product(id=4, name="Table", description="A wooden table", price=199.99, quantity=20),
            ]
            for product in products:
                db.add(database_models.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()

# -------------------------------
# DB DEPENDENCY
# -------------------------------
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.get("/")
def home():
    return {"message": "FastAPI is running! 🚀"}

# -------------------------------
# GET ALL PRODUCTS
# -------------------------------
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()

# -------------------------------
# GET PRODUCT BY ID
# -------------------------------
@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if product:
        return product
    return {"detail": "Product not found!"}

# -------------------------------
# CREATE PRODUCT
# -------------------------------
@app.post("/products")
def create_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# -------------------------------
# UPDATE PRODUCT
# -------------------------------
@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()

    if not db_product:
        return {"detail": "Product not found!"}

    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.quantity = product.quantity

    db.commit()
    return {"message": "Product updated successfully!"}

# -------------------------------
# DELETE PRODUCT
# -------------------------------
@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()

    if not db_product:
        return {"detail": "Product not found!"}

    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully!"}

# -------------------------------
# RENDER ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
    )

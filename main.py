from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  
from models import Product
import database_models
from database import engine, session 
from sqlalchemy.orm import Session

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initial mock data
products = [
    Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    Product(id=2, name="Laptop", description="A powerful laptop", price=999.99, quantity=30),
    Product(id=3, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
    Product(id=4, name="Table", description="A wooden table", price=199.99, quantity=20),
]

database_models.Base.metadata.create_all(bind=engine)

def init_db():
    db = session()
    try:
        count=db.query(database_models.Product).count()
        if count == 0:
            for product in products:
                db.add(database_models.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()
init_db()
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "FastAPI is running! 🚀"}

#Get All Products
@app.get("/products")
def get_products(db: Session= Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return db_products

#Get Product by ID
@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session= Depends(get_db)):
    product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if product:
        return product
    return {"detail": "No products found!"}

#Add New Product
@app.post("/products")
def create_product(product: Product, db: Session= Depends(get_db)):
    db_product = db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return {"message": "Product created successfully!"}

#Update Product
@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session= Depends(get_db)):
    db_product=db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description    
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return {"message": "Product updated successfully!"}
    return {"detail": "Product not found!"}

#Delete Product
@app.delete("/products/{id}")
def delete_product(id: int, db: Session= Depends(get_db)):
    db_product= db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully!"}
    return {"detail": "Product not found!"}



from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import sqlite3
from datetime import datetime
import uuid


app = FastAPI(title="Red Card - Retail API")


# ============================================================
# STATIC FILES
# ============================================================

# Product images
app.mount("/images", StaticFiles(directory="images"), name="images")


# Main CSS file
@app.get("/style.css")
def serve_css():
    return FileResponse("style.css", media_type="text/css")


# Checkout CSS file
@app.get("/checkout.css")
def serve_checkout_css():
    return FileResponse("checkout.css", media_type="text/css")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA MODELS
# ============================================================

class Purchase(BaseModel):
    customer_id: str
    customer_name: str
    phone: Optional[str] = None
    ship_mode: Optional[str] = "Standard"
    product_id: str
    product_name: str
    quantity: int
    sales: float


class LoginRequest(BaseModel):
    customer_name: str
    phone: str
    email: str
    dob: Optional[str] = None


# ============================================================
# DATABASE
# ============================================================

def get_db_connection():
    conn = sqlite3.connect("retail_sales_normalized.db")
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# HTML PAGE ROUTES
# ============================================================

@app.get("/")
def serve_catalog():
    return FileResponse("catalog.html")


@app.get("/index.html")
def serve_checkout():
    return FileResponse("index.html")


# ============================================================
# USER & AUTH ROUTES
# ============================================================

@app.post("/api/login")
def login_user(req: LoginRequest):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT "Customer ID" FROM customers '
            'WHERE LOWER("Customer Name") = LOWER(?)',
            (req.customer_name,)
        )

        row = cursor.fetchone()

        if row:
            customer_id = row["Customer ID"]

        else:
            customer_id = f"WEB-CUST-{uuid.uuid4().hex[:6].upper()}"

            cursor.execute(
                '''
                INSERT INTO customers
                ("Customer ID", "Customer Name", "State")
                VALUES (?, ?, ?)
                ''',
                (
                    customer_id,
                    req.customer_name,
                    "Online"
                )
            )

            conn.commit()

        return {
            "status": "success",
            "customer_id": customer_id,
            "customer_name": req.customer_name,
            "phone": req.phone,
            "email": req.email,
            "dob": req.dob
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if "conn" in locals():
            conn.close()


# ============================================================
# CUSTOMER ORDERS
# ============================================================

@app.get("/api/orders/{customer_id}")
def get_user_orders(customer_id: str):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT
                o."Order Date",
                p."Product Name",
                oi.Quantity,
                oi.Sales
            FROM orders o
            JOIN order_items oi
                ON o."Order ID" = oi."Order ID"
            JOIN products p
                ON oi."Product ID" = p."Product ID"
            WHERE o."Customer ID" = ?
            ORDER BY o."Order Date" DESC
            ''',
            (customer_id,)
        )

        orders = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return {
            "status": "success",
            "orders": orders
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if "conn" in locals():
            conn.close()


# ============================================================
# BESTSELLERS
# ============================================================

@app.get("/api/bestsellers")
def get_bestsellers():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get actual bestsellers based on quantity sold
        cursor.execute(
            '''
            SELECT
                p."Product ID",
                p."Product Name",
                p."Unit Price",
                p."Category of Goods",
                SUM(oi.Quantity) AS TotalSold
            FROM products p
            JOIN order_items oi
                ON p."Product ID" = oi."Product ID"
            GROUP BY p."Product ID"
            ORDER BY TotalSold DESC
            LIMIT 4
            '''
        )

        bestsellers = [
            dict(row)
            for row in cursor.fetchall()
        ]

        # Fallback if no orders exist
        if not bestsellers:

            cursor.execute(
                '''
                SELECT
                    "Product ID",
                    "Product Name",
                    "Unit Price",
                    "Category of Goods"
                FROM products
                LIMIT 4
                '''
            )

            bestsellers = [
                dict(row)
                for row in cursor.fetchall()
            ]

        return {
            "status": "success",
            "bestsellers": bestsellers
        }

    except Exception as e:

        print("\n--- BESTSELLER DATABASE ERROR ---")
        print(f"Reason: {str(e)}")
        print("---------------------------------\n")

        try:

            cursor.execute(
                '''
                SELECT
                    "Product ID",
                    "Product Name",
                    "Unit Price",
                    "Category of Goods"
                FROM products
                LIMIT 4
                '''
            )

            fallback_items = [
                dict(row)
                for row in cursor.fetchall()
            ]

            return {
                "status": "success",
                "bestsellers": fallback_items,
                "warning": str(e)
            }

        except Exception as inner_e:

            raise HTTPException(
                status_code=500,
                detail=str(inner_e)
            )

    finally:
        if "conn" in locals():
            conn.close()


# ============================================================
# CATEGORIES
# ============================================================

@app.get("/api/categories")
def get_categories():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT DISTINCT
                "Category of Goods"
            FROM products
            WHERE "Category of Goods" IS NOT NULL
            '''
        )

        categories = [
            row[0]
            for row in cursor.fetchall()
        ]

        return {
            "categories": categories
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if "conn" in locals():
            conn.close()


# ============================================================
# PRODUCTS
# ============================================================

@app.get("/api/products")
def get_products(
    search: str = "",
    category: str = ""
):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                "Product ID",
                "Product Name",
                "Unit Price",
                "Category of Goods"
            FROM products
            WHERE "Product Name" LIKE ?
        '''

        params = [
            f"%{search}%"
        ]

        if category:

            query += '''
                AND "Category of Goods" = ?
            '''

            params.append(category)

        query += " LIMIT 50"

        cursor.execute(
            query,
            params
        )

        products = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return {
            "products": products
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if "conn" in locals():
            conn.close()


# ============================================================
# PURCHASE / ORDER
# ============================================================

@app.post("/api/buy")
def register_purchase(
    purchase: Purchase
):

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        order_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        order_id = (
            f"WEB-ORD-"
            f"{uuid.uuid4().hex[:6].upper()}"
        )

        # Insert order
        cursor.execute(
            '''
            INSERT INTO orders
            ("Order ID", "Customer ID", "Order Date", "Ship Mode")
            VALUES (?, ?, ?, ?)
            ''',
            (
                order_id,
                purchase.customer_id,
                order_date,
                purchase.ship_mode
            )
        )

        # Insert order item
        cursor.execute(
            '''
            INSERT INTO order_items
            ("Order ID", "Product ID", "Quantity", "Sales")
            VALUES (?, ?, ?, ?)
            ''',
            (
                order_id,
                purchase.product_id,
                purchase.quantity,
                purchase.sales
            )
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Order securely logged!",
            "order_id": order_id
        }

    except Exception as e:

        if "conn" in locals():
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if "conn" in locals():
            conn.close()


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    print("=" * 50)
    print("Starting Red Card Server...")
    print("Website: http://127.0.0.1:8000/")
    print("Checkout: http://127.0.0.1:8000/index.html")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
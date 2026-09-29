# CartNest — Full-Stack Retail E-Commerce Application

CartNest is a full-stack retail e-commerce application built using **HTML, CSS, JavaScript, Python, FastAPI, SQLite, and Power BI**.

The project combines a web-based shopping platform with a backend REST API, normalized database, order management system, and business intelligence dashboard. Historical retail sales data is cleaned and transformed before being stored in a structured SQLite database. The application then uses this data to provide products, categories, bestsellers, customer information, and order functionality.

The system also allows new orders placed through the website to be stored in the database, creating a connection between the operational e-commerce application and business analytics.

---

## 1. Project Overview

CartNest provides a complete shopping experience where users can browse products, search and filter the catalog, add products to a cart, enter delivery details, and place orders.

### Main Features

- Product catalog with images
- Product search
- Category filtering
- Data-driven bestseller section
- Shopping cart
- Quantity modification
- Cart persistence using browser `localStorage`
- Customer profile functionality
- Customer order history
- Checkout page
- Delivery-address validation
- PIN-code based city/state lookup
- Standard and Express shipping
- FastAPI REST APIs
- SQLite database storage
- Power BI business analytics

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, FastAPI |
| Server | Uvicorn |
| Database | SQLite |
| Data Processing | Pandas |
| API Validation | Pydantic |
| Client-side Storage | Browser `localStorage` |
| Address Lookup | India Post PIN-code API |
| Business Intelligence | Microsoft Power BI |
| Product Images | Local `/images` directory |

---

## 3. System Architecture

The overall system follows a layered architecture:

```text
Retail Sales Dataset
        ↓
Data Cleaning & Transformation
        ↓
Normalized SQLite Database
        ↓
FastAPI Backend
        ↓
HTML / CSS / JavaScript Frontend
        ↓
Customer Interaction
        ↓
New Orders
        ↓
SQLite Database
        ↓
Power BI Dashboard

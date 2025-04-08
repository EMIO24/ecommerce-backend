# ecommerce-backend
A Django REST API for managing e-commerce products with authentication and search functionality
E-Commerce API Documentation
Overview
This API provides endpoints for managing an e-commerce platform with features for:

User authentication and authorization

Product and category management

Order processing

Product reviews

API Base URL
Copy
http://localhost:8000/api/
Authentication
All endpoints (except registration and login) require authentication using token-based authentication.

Register a New User
Endpoint: POST /register/
Request Body:

json
Copy
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "newpassword"
}


Login
Endpoint: POST /api-token-auth/
Request Body:

json
Copy
{
    "username": "testuser1",
    "password": "testpassword1"
}

Response:
json
Copy
{
    "token": "your_auth_token_here"
}


Categories
List All Categories
Endpoint: GET /categories/
Create Category (Admin Only)
Endpoint: POST /categories/

Headers:
Copy
Authorization: Token your_admin_token_here

Request Body:
json
Copy
{
    "name": "Electronics"
}


Products
List All Products
Endpoint: GET /products/
Filter Products
Available filters:

category: Filter by category ID

price_min: Minimum price

price_max: Maximum price

stock_available: true/false

Example:

Copy
GET /products/?category=1&price_min=50&price_max=1000&stock_available=true
Create Product (Admin Only)
Endpoint: POST /products/

Headers:

Copy
Authorization: Token your_admin_token_here
Request Body:

json
Copy
{
    "name": "Laptop",
    "description": "Powerful laptop",
    "price": 1200.00,
    "category": 1,
    "stock_quantity": 10,
    "image_url": "http://example.com/laptop.jpg"
}
Orders
Create Order
Endpoint: POST /orders/

Headers:

Copy
Authorization: Token your_user_token_here
Request Body:

json
Copy
{
    "items": [
        {
            "item": 1,
            "quantity": 1
        },
        {
            "item": 2,
            "quantity": 2
        }
    ]
}
List User's Orders
Endpoint: GET /orders/

Headers:

Copy
Authorization: Token your_user_token_here
Reviews
Create Review
Endpoint: POST /reviews/

Headers:

Copy
Authorization: Token your_user_token_here
Request Body:

json
Copy
{
    "product": 1,
    "rating": 4,
    "text": "Good product"
}
List Reviews for Product
Endpoint: GET /reviews/?product_id=1

Testing with Postman
Import the Postman collection provided

Set the base_url environment variable to your API endpoint

Run the setup requests in order to create test data:

Create admin user

Create regular user

Create categories

Create products

Execute the test requests for orders and other endpoints

Example Test Data
After running the setup requests, you'll have:

Users:

Admin: adminuser / adminpassword

Regular user: testuser1 / testpassword1

Categories:

ID 1: Electronics

Products:

ID 1: Laptop (10 in stock)

ID 2: Smartphone (20 in stock)

Error Responses
Common error responses include:

401 Unauthorized: Missing or invalid authentication token

403 Forbidden: User doesn't have permission for the action

400 Bad Request: Invalid request data

404 Not Found: Resource doesn't exist
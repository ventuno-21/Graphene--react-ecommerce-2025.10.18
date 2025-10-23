# 🛒 Full-Stack E-Commerce App (Django + React + GraphQL)  

This is a full-stack e-commerce web application built with **Django**, **GraphQL**, and **React (Vite)**. It supports user authentication, product browsing, cart management (for both guests and logged-in users), and dynamic cart updates via Apollo Client.  

---

## 🚀 Features

- 🔐 User login, registration, and logout  
- 🛍️ Product listing and detail pages  
- 🛒 Cart functionality for guests and authenticated users  
- 📦 Add to cart with quantity control and stock validation  
- 🧮 Cart preview in navbar with live item count  
- 🧹 Remove items and update quantities with instant UI sync  
- 🌐 GraphQL API powered by Django and Graphene  
- ⚡ Fast frontend with React + Vite + Apollo Client  
- 📸 Product image rendering with fallback support  
- 💬 SweetAlert2 for user feedback  

---

## 🧱 Tech Stack

| Layer       | Technology                         |
|-------------|-------------------------------------|
| Backend     | Django, Graphene, PostgreSQL        |
| Frontend    | React, Vite, Apollo Client, Tailwind CSS |
| Auth        | JWT or session-based (via Django)   |
| Styling     | Tailwind CSS, ShadCN UI             |
| Alerts      | SweetAlert2                         |
| Media       | Local media or Cloudinary (optional)|
| Deployment  | Render (or any cloud platform)      |

---

## 📦 Installation

### 1. Backend Setup (Django)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run server
python manage.py runserver
Make sure your .env includes:

Codice
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://...
```

2. Frontend Setup (React + Vite)
```bash
# Install dependencies
npm install

# Start dev server

npm run dev
Create a .env file in the frontend root:  
```

Codice
VITE_API_URL=http://localhost:5000/graphql/  
🧪 GraphQL Queries & Mutations  
All frontend data is fetched via GraphQL using Apollo Client. Key operations include:  
  
GET_PRODUCTS  
GET_PRODUCT  
GET_CART  
ADD_TO_CART  
REMOVE_FROM_CART  
UPDATE_CART_ITEM_QUANTITY    

🛠️ Development Notes  
Cart supports both authenticated and guest users via union types (CartItemType, GuestCartItemType)  
Navbar cart preview updates instantly using refetchQueries and awaitRefetchQueries  
Decimal fields in GraphQL must be wrapped with Decimal() in Python to avoid type errors  
Product images use VITE_API_URL to construct media URLs dynamically  
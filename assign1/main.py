from fastapi import FastAPI, Query
 
app = FastAPI()
 
# ── Temporary data — acting as our database for now ──────────
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop stand',      'price': 2999, 'category': 'Stationery',   'in_stock': True },
    {'id': 6, 'name': 'Mechanical keyboard', 'price': 1185, 'category': 'Electronics', 'in_stock': True },
    {'id': 7, 'name': 'Webcam',              'price': 1160, 'category': 'Electronics',  'in_stock': True },
]
 
# ── Endpoint 0 — Home ────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
# ── Endpoint 1 — Return all products ──────────────────────────
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}


@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only')
):
    result = products          # start with all products
 
    if category:
        result = [p for p in result if p['category'] == category]
 
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
 
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
 
    return {'filtered_products': result, 'count': len(result)}


@app.get('/products/search/{keyword}')
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p['name'].lower()]
    if not result:
        return {"message": "No products matched your search"}
    return {"matched_products": result, "total_count": len(result)}

@app.get('/products/deals')
def get_product_deals():
    cheapest = min(products, key=lambda p: p['price'])
    expensive = max(products, key=lambda p: p['price'])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
         }

 
# ── Endpoint 2 — Return one product by its ID ──────────────────
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

@app.get('/store/summary')
def get_store_summary():
    store_name: str= "My E-commerce Store"
    total_products = len(products)
    in_stock = len([p for p in products if p['in_stock']])
    out_of_stock= total_products - in_stock
    categories = sorted(set(p['category'].capitalize() for p in products))

    return {
        "store_name": store_name,
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories }
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List,Optional

app = FastAPI()
feedback = []

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items:        List[OrderItem] = Field(..., min_items=1)
 
# ── Pydantic model ───────────────────────────────────────────────────────────
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    price: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    in_stock: Optional[bool] = None

class CustomerFeedback(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    rating:           int = Field(..., ge=1,le=5)
    comment:          str = Field(None,max_length=300)

 
# ── Data ────────────────────────────────────────────────────────────────────
products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','in_stock':True},
    {'id':2,'name':'Notebook',      'price': 99,'category':'Stationery', 'in_stock':True},
    {'id':3,'name':'USB Hub',        'price':799,'category':'Electronics','in_stock':False},
    {'id':4,'name':'Pen Set',         'price': 49,'category':'Stationery', 'in_stock':True},
]
orders = []
order_counter = 1
 
# ── Endpoints ───────────────────────────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
 
@app.get('/products/filter')   # NOTE: must come BEFORE /products/{product_id}
def filter_products(
    category:  str  = Query(None),
    min_price: int  = Query(None),
    max_price: int  = Query(None),
    in_stock:  bool = Query(None)
):
    result = products
    if category:             result = [p for p in result if p['category']==category]
    if min_price:            result = [p for p in result if p['price']>=min_price]
    if max_price:            result = [p for p in result if p['price']<=max_price]
    if in_stock is not None: result = [p for p in result if p['in_stock']==in_stock]
    return {'filtered_products': result, 'count': len(result)}

@app.get('/products/summary')
def get_product_summary():
    total_products = len(products)
    in_stock_products = [p for p in products if p["in_stock"]]
    out_of_stock = total_products - len(in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = [c for c in {p["category"] for p in products}]

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock_products),
        "out_of_stock_count": out_of_stock,
        "most_expensive": {"name": most_expensive["name"], "price": most_expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }


@app.get('/products/{product_id}/price')
def get_product_price(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}
 
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {"name": product['name'],
                    "price": product['price'] }
    return {'error': 'Product not found'}

 
@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter

    product = next((p for p in products if p['id'] == order_data.product_id), None)

    if product is None:
        return {'error': 'Product not found'}

    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}

    total_price = product['price'] * order_data.quantity

    order = {
        'order_id': order_counter,
        'customer_name': order_data.customer_name,
        'product': product['name'],
        'quantity': order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'total_price': total_price,
        'status': 'confirmed'
         }

    orders.append(order)

    order_counter += 1

    return {
        'message': 'Order placed successfully',
        'order': order
    }

@app.get('/orders/{order_id}')
def get_single_order(order_id: int):
    order = next((o for o in orders if o['order_id'] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    return order

@app.patch('/orders/{order_id}/confirm')
def confirm_order(order_id: int):
    order = next((o for o in orders if o['order_id'] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    order['status'] = 'confirmed'
    return order

@app.post('/bulk/orders')
def place_bulk_order(order_data: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order_data.items:
        product = next((p for p in products if p['id'] == item.product_id), None)
        
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
            continue
            
        if not product['in_stock']:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} out of stock"})
            continue

        item_total = product['price'] * item.quantity
        grand_total += item_total
        confirmed.append({
            "product": product['name'],
            "qty": item.quantity,
            "price_each": product['price']
        })

    return {
        "company": order_data.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}


@app.post('/feedback')
def submit_feedback(data: CustomerFeedback):
    feedback_item = data.model_dump()
    feedback.append(feedback_item)
    return {
        "message": "Feedback submitted successfully",
        "feedback": feedback_item,
        "total_feedback": len(feedback)
    }


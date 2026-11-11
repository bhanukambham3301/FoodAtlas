import os
import sys
import json
from flask import Flask, render_template, request, redirect, flash, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

UTILS_DIR = os.path.join(BASE_DIR, 'utils')
if UTILS_DIR not in sys.path:
    sys.path.insert(0, UTILS_DIR)

# Smart Import with Fallback logic for helper or pandas
try:
    from helper import get_recommendations_by_city
except ModuleNotFoundError:
    try:
        from utils.helper import get_recommendations_by_city
    except ModuleNotFoundError:
        import pandas as pd


        def get_recommendations_by_city(city_name):
            if not city_name:
                return []

            csv_path = os.path.join(BASE_DIR, 'restaurants.csv')

            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                df = pd.read_csv(csv_path)
                df.columns = df.columns.astype(str).str.replace('\ufeff', '').str.strip().str.lower()
                column_mapping = {
                    'restaurant name': 'name',
                    'restaurant_name': 'name',
                    'city name': 'city',
                    'city_name': 'city',
                    'location': 'city',
                    'cuisines': 'cuisine',
                    'cuisine': 'cuisine',
                    'image url': 'image',
                    'image_url': 'image'
                }
                df.rename(columns=column_mapping, inplace=True)
            else:
                sample_data = {
                    'id': [1, 2, 3, 4, 5, 6, 7],
                    'name': ['Bukhara', 'Britannia & Co.', 'Mavalli Tiffin Room', 'Paradise Biryani', 'Toit Brewpub',
                             'Mainland China', 'Haldiram'],
                    'city': ['Delhi', 'Mumbai', 'Bengaluru', 'Hyderabad', 'Bengaluru', 'Kolkata', 'Delhi'],
                    'address': [
                        'ITC Maurya, Diplomatic Enclave, New Delhi',
                        '11 Sprott Rd, Fort, Mumbai',
                        '14 Lalbagh Fort Rd, Bengaluru',
                        'MG Road, Secunderabad, Hyderabad',
                        '100 Feet Rd, Indiranagar, Bengaluru',
                        'Park Street, Kolkata',
                        'Connaught Place, New Delhi'
                    ],
                    'cuisine': [
                        'North Indian, Kebab',
                        'Parsi, Berry Pulao',
                        'South Indian, Dosa, Filter Coffee',
                        'Hyderabadi Biryani, Kebabs',
                        'Brewery, Continental, Pizza',
                        'Chinese, Asian, Dim Sums',
                        'Chaat, North Indian Sweets'
                    ],
                    'rating': [4.8, 4.6, 4.7, 4.5, 4.7, 4.6, 4.4],
                    'image': [
                        "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500",
                        "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500",
                        "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=500",
                        "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=500",
                        "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500",
                        "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500",
                        "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=500"
                    ]
                }
                df = pd.DataFrame(sample_data)

            if 'city' not in df.columns:
                return []

            filtered = df[df['city'].astype(str).str.strip().str.lower() == city_name.strip().lower()].copy()
            if filtered.empty:
                return []

            if 'rating' in filtered.columns:
                filtered = filtered.sort_values(by='rating', ascending=False)

            records = filtered.to_dict(orient='records')
            return records

# Safe import for menu data from menu_data.py
try:
    from menu_data import menu_database

    print("Successfully loaded menu_database from menu_data.py")
except ModuleNotFoundError:
    print("WARNING: menu_data.py not found! Using empty menu dictionary.")
    menu_database = {}


# Helper function to get a flat list of items from menu_database for details/ordering views
def get_all_menu_items():
    items = []
    if isinstance(menu_database, dict):
        for cat, cat_items in menu_database.items():
            if isinstance(cat_items, list):
                items.extend(cat_items)
    elif isinstance(menu_database, list):
        items = menu_database
    return items


# Flask Initialization (Initialized only once)
app = Flask(__name__)
app.secret_key = 'food_atlas_secret_key'

# App Name Variable
app_name = "FoodAtlas"

# File path to store login data permanently
USERS_FILE = os.path.join(BASE_DIR, 'users.json')


def load_users():
    if not os.path.exists(USERS_FILE):
        default_users = {"admin": {"email": "admin@foodatlas.com", "password": "1234"}}
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=4)
        return default_users

    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"admin": {"email": "admin@foodatlas.com", "password": "1234"}}


def save_user(username, email, password):
    users = load_users()
    users[username] = {
        "email": email,
        "password": password
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


@app.route('/')
def welcome():
    return render_template('welcome.html', app_name=app_name)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash("Please fill in all fields.")
            return render_template('signup.html')

        users_db = load_users()

        if username in users_db:
            flash("Username already exists! Please choose another or Login.")
            return render_template('signup.html')

        save_user(username, email, password)
        flash("Account created successfully! Please Sign In now.")
        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        users_db = load_users()

        if username in users_db:
            user_data = users_db[username]
            saved_password = user_data.get('password') if isinstance(user_data, dict) else user_data

            if saved_password == password:
                return redirect('/home')

        flash("Invalid credentials, please try again.")

    return render_template('login.html')


@app.route('/home')
def home():
    # Debug print for menu items
    all_items = get_all_menu_items()
    for item in all_items:
        print(f"Name: {item.get('name')} | Category: '{item.get('category')}' | Type: '{item.get('type')}'")

    return render_template('index.html', menu=menu_database)


@app.route('/menu')
def view_menu():
    return render_template('menu.html', menu=menu_database)


@app.route('/search', methods=['GET'])
def search():
    city = request.args.get('city', '').strip()
    restaurants = get_recommendations_by_city(city)
    return render_template('results.html', restaurants=restaurants, city=city)


@app.route('/results')
def results():
    city = request.args.get('city', '').strip()
    restaurants = get_recommendations_by_city(city)
    return render_template('results.html', restaurants=restaurants, city=city)


@app.route('/details')
def details():
    restaurant_name = request.args.get('name', 'Restaurant').strip()
    city = request.args.get('city', '')

    # Pull menu items dynamically from menu_data.py
    selected_menu = get_all_menu_items()

    # Debug print for menu items
    for item in selected_menu:
        print(f"Name: {item.get('name')} | Category: '{item.get('category')}' | Type: '{item.get('type')}'")

    return render_template('details.html', restaurant_name=restaurant_name, city=city, menu=selected_menu)


@app.route('/table-order', methods=['GET', 'POST'])
def table_order():
    if request.method == 'POST':
        data = request.get_json()
        print("Table Direct Order Received:", data)
        return jsonify({
            "status": "success",
            "message": f"Order placed successfully for Table {data.get('table_no')} at {data.get('restaurant')}!"
        })

    restaurant_name = request.args.get('name', 'Restaurant').strip()
    city = request.args.get('city', '').strip()

    # Pull menu items dynamically from menu_data.py
    selected_menu = get_all_menu_items()

    # Debug print for menu items
    for item in selected_menu:
        print(f"Name: {item.get('name')} | Category: '{item.get('category')}' | Type: '{item.get('type')}'")

    return render_template('table_order.html', restaurant_name=restaurant_name, city=city, menu=selected_menu)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
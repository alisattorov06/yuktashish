from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Frontend’dan so‘rovlarga ruxsat berish uchun

# Ma'lumotlar bazasini boshlash
def init_db():
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cargos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, direction TEXT, weight REAL, volume REAL, price REAL, phone TEXT, type TEXT)''')
    conn.commit()
    conn.close()

# Asosiy route (sinov uchun)
@app.route('/')
def home():
    return jsonify({"message": "Yuktashish API ishlayapti!"}), 200

# Ro'yxatdan o'tish
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'name' not in data or 'role' not in data:
        return jsonify({"error": "Name va role kerak"}), 400
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, role) VALUES (?, ?)", (data['name'], data['role']))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return jsonify({"message": "Foydalanuvchi ro'yxatdan o'tdi", "user_id": user_id}), 201

# Yuk qo'shish
@app.route('/add-cargo', methods=['POST'])
def add_cargo():
    data = request.get_json()
    required_fields = ['direction', 'weight', 'volume', 'price', 'phone', 'type']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Barcha maydonlar kerak"}), 400
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("INSERT INTO cargos (direction, weight, volume, price, phone, type) VALUES (?, ?, ?, ?, ?, ?)", 
              (data['direction'], data['weight'], data['volume'], data['price'], data['phone'], data['type']))
    conn.commit()
    cargo_id = c.lastrowid
    conn.close()
    return jsonify({"message": "Yuk qo'shildi", "cargo_id": cargo_id}), 201

# Yuklarni olish
@app.route('/cargos', methods=['GET'])
def get_cargos():
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cargos")
    cargos = [{"id": row[0], "direction": row[1], "weight": row[2], "volume": row[3], "price": row[4], "phone": row[5], "type": row[6]} 
              for row in c.fetchall()]
    conn.close()
    return jsonify(cargos), 200

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 10000))  # Render uchun dinamik port
    app.run(host='0.0.0.0', port=port, debug=True)

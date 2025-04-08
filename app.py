from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Sessiya uchun credentials ni qo'llab-quvvatlash
app.secret_key = 'your_secret_key_here'  # Sessiya uchun maxfiy kalit

# Ma'lumotlar bazasini yangilangan versiyasi
def init_db():
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 name TEXT, 
                 role TEXT,
                 email TEXT UNIQUE,
                 password TEXT)''')  # Parol uchun maydon qo'shildi
    c.execute('''CREATE TABLE IF NOT EXISTS cargos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 direction TEXT, 
                 weight REAL, 
                 volume REAL, 
                 price REAL, 
                 phone TEXT, 
                 type TEXT,
                 user_id INTEGER,
                 FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return jsonify({"message": "Yuktashish API ishlayapti!"}), 200

# Yangilangan ro'yxatdan o'tish funksiyasi
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['name', 'role', 'email', 'password']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Barcha maydonlar kerak"}), 400
    
    hashed_password = generate_password_hash(data['password'])
    
    try:
        conn = sqlite3.connect('yuktashish.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, role, email, password) VALUES (?, ?, ?, ?)", 
                 (data['name'], data['role'], data['email'], hashed_password))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        # Sessiyaga foydalanuvchi ma'lumotlarini saqlash
        session['user_id'] = user_id
        session['user_email'] = data['email']
        session['user_role'] = data['role']
        
        return jsonify({
            "message": "Foydalanuvchi ro'yxatdan o'tdi",
            "user_id": user_id,
            "email": data['email'],
            "role": data['role']
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Bu email allaqachon ro'yxatdan o'tgan"}), 400

# Tizimga kirish funksiyasi
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email va parol kerak"}), 400
    
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("SELECT id, email, role, password FROM users WHERE email=?", (data['email'],))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[3], data['password']):
        session['user_id'] = user[0]
        session['user_email'] = user[1]
        session['user_role'] = user[2]
        return jsonify({
            "message": "Kirish muvaffaqiyatli",
            "user_id": user[0],
            "email": user[1],
            "role": user[2]
        }), 200
    else:
        return jsonify({"error": "Noto'g'ri email yoki parol"}), 401

# Foydalanuvchi ma'lumotlari
@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return jsonify({"error": "Avtorizatsiya talab qilinadi"}), 401
    
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("SELECT id, name, role, email FROM users WHERE id=?", (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "id": user[0],
            "name": user[1],
            "role": user[2],
            "email": user[3]
        }), 200
    else:
        return jsonify({"error": "Foydalanuvchi topilmadi"}), 404

# Chiqish funksiyasi
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Chiqish muvaffaqiyatli"}), 200

# Yuk qo'shish funksiyasi (user_id bilan)
@app.route('/add-cargo', methods=['POST'])
def add_cargo():
    if 'user_id' not in session:
        return jsonify({"error": "Avtorizatsiya talab qilinadi"}), 401
    
    data = request.get_json()
    required_fields = ['direction', 'weight', 'volume', 'price', 'phone', 'type']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Barcha maydonlar kerak"}), 400
    
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("INSERT INTO cargos (direction, weight, volume, price, phone, type, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
             (data['direction'], data['weight'], data['volume'], data['price'], data['phone'], data['type'], session['user_id']))
    conn.commit()
    cargo_id = c.lastrowid
    conn.close()
    return jsonify({"message": "Yuk qo'shildi", "cargo_id": cargo_id}), 201

# Yuklarni olish (faqat o'z yuklarini)
@app.route('/my-cargos', methods=['GET'])
def get_my_cargos():
    if 'user_id' not in session:
        return jsonify({"error": "Avtorizatsiya talab qilinadi"}), 401
    
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cargos WHERE user_id=?", (session['user_id'],))
    cargos = [{"id": row[0], "direction": row[1], "weight": row[2], "volume": row[3], 
              "price": row[4], "phone": row[5], "type": row[6]} for row in c.fetchall()]
    conn.close()
    return jsonify(cargos), 200

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

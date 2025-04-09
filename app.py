from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Flask ilovasini yaratamiz
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'maxfiy-kalit-12345')

# CORS sozlamalari
CORS(app, supports_credentials=True)

# Ma'lumotlar bazasini yaratish
def init_db():
    try:
        conn = sqlite3.connect('yuktashish.db')
        cursor = conn.cursor()
        
        # Foydalanuvchilar jadvali
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            vehicle_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Yuklar jadvali
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cargos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            direction TEXT NOT NULL,
            weight REAL NOT NULL,
            volume REAL NOT NULL,
            price REAL NOT NULL,
            phone TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Xato: {e}")
    finally:
        if conn:
            conn.close()

# Ro'yxatdan o'tish
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Majburiy maydonlarni tekshirish
        required_fields = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({"xato": "Barcha maydonlarni to'ldiring"}), 400
            
        # Parolni hash qilish
        hashed_password = generate_password_hash(data['password'])
        
        conn = sqlite3.connect('yuktashish.db')
        cursor = conn.cursor()
        
        # Foydalanuvchini bazaga qo'shish
        cursor.execute('''
        INSERT INTO users (name, email, password, role, phone, company, vehicle_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['email'],
            hashed_password,
            data['role'],
            data.get('phone', ''),
            data.get('company', ''),
            data.get('vehicle_type', '')
        ))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "xabar": "Ro'yxatdan o'tish muvaffaqiyatli",
            "user_id": user_id
        }), 201
        
    except sqlite3.IntegrityError:
        return jsonify({"xato": "Bu email allaqachon ro'yxatdan o'tgan"}), 400
    except Exception as e:
        return jsonify({"xato": str(e)}), 500

# Tizimga kirish
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"xato": "Email va parol kiritishingiz kerak"}), 400
        
        conn = sqlite3.connect('yuktashish.db')
        cursor = conn.cursor()
        
        # Foydalanuvchini qidirish
        cursor.execute('SELECT id, name, email, password, role FROM users WHERE email = ?', (data['email'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"xato": "Foydalanuvchi topilmadi"}), 404
        
        # Parolni tekshirish
        if not check_password_hash(user[3], data['password']):
            return jsonify({"xato": "Noto'g'ri parol"}), 401
        
        # Sessiyaga saqlash
        session['user_id'] = user[0]
        session['user_email'] = user[2]
        session['user_role'] = user[4]
        
        return jsonify({
            "xabar": "Kirish muvaffaqiyatli",
            "foydalanuvchi": {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "role": user[4]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"xato": str(e)}), 500

# Foydalanuvchi ma'lumotlari
@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return jsonify({"xato": "Kirish talab qilinadi"}), 401
    
    try:
        conn = sqlite3.connect('yuktashish.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, email, role, phone, company, vehicle_type FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"xato": "Foydalanuvchi topilmadi"}), 404
        
        return jsonify({
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "phone": user[4],
            "company": user[5],
            "vehicle_type": user[6]
        }), 200
        
    except Exception as e:
        return jsonify({"xato": str(e)}), 500

# Yuk qo'shish
@app.route('/add-cargo', methods=['POST'])
def add_cargo():
    if 'user_id' not in session:
        return jsonify({"xato": "Kirish talab qilinadi"}), 401
    
    try:
        data = request.get_json()
        required_fields = ['direction', 'weight', 'volume', 'price', 'phone', 'type']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({"xato": "Barcha maydonlarni to'ldiring"}), 400
        
        conn = sqlite3.connect('yuktashish.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO cargos (user_id, direction, weight, volume, price, phone, type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            data['direction'],
            data['weight'],
            data['volume'],
            data['price'],
            data['phone'],
            data['type']
        ))
        
        conn.commit()
        cargo_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "xabar": "Yuk muvaffaqiyatli qo'shildi",
            "cargo_id": cargo_id
        }), 201
        
    except Exception as e:
        return jsonify({"xato": str(e)}), 500

# Tizimdan chiqish
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"xabar": "Chiqish muvaffaqiyatli"}), 200

# Dasturni ishga tushirish
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-very-secret-key-123')
CORS(app, supports_credentials=True)

# Ma'lumotlar bazasini ishga tushirish
def init_db():
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    
    # Foydalanuvchilar jadvali
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        phone TEXT,
        company_name TEXT,
        vehicle_type TEXT
    )
    ''')
    
    # Yuklar jadvali
    c.execute('''
    CREATE TABLE IF NOT EXISTS cargos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        direction TEXT NOT NULL,
        weight REAL NOT NULL,
        volume REAL NOT NULL,
        price REAL NOT NULL,
        phone TEXT NOT NULL,
        type TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Ro'yxatdan o'tish
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Majburiy maydonlarni tekshirish
        required = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required):
            return jsonify({"error": "Barcha maydonlar to'ldirilishi kerak"}), 400
        
        # Parolni hash qilish
        hashed_pw = generate_password_hash(data['password'])
        
        conn = sqlite3.connect('yuktashish.db')
        c = conn.cursor()
        
        # Foydalanuvchini bazaga qo'shish
        c.execute('''
        INSERT INTO users (name, email, password, role, phone, company_name, vehicle_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['email'],
            hashed_pw,
            data['role'],
            data.get('phone', ''),
            data.get('company_name', ''),
            data.get('vehicle_type', '')
        ))
        
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        return jsonify({
            "message": "Ro'yxatdan o'tish muvaffaqiyatli",
            "user_id": user_id
        }), 201
        
    except sqlite3.IntegrityError:
        return jsonify({"error": "Bu email allaqachon ro'yxatdan o'tgan"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Tizimga kirish
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email va parol kiritilishi shart"}), 400
        
        conn = sqlite3.connect('yuktashish.db')
        c = conn.cursor()
        
        # Foydalanuvchini email bo'yicha qidirish
        c.execute('''
        SELECT id, name, email, password, role FROM users WHERE email = ?
        ''', (data['email'],))
        
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"error": "Foydalanuvchi topilmadi"}), 404
        
        # Parolni tekshirish
        if not check_password_hash(user[3], data['password']):
            return jsonify({"error": "Noto'g'ri parol"}), 401
        
        # Sessiyaga saqlash
        session['user_id'] = user[0]
        session['user_email'] = user[2]
        session['user_role'] = user[4]
        
        return jsonify({
            "message": "Kirish muvaffaqiyatli",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "role": user[4]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Foydalanuvchi ma'lumotlari
@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return jsonify({"error": "Kirish talab qilinadi"}), 401
    
    try:
        conn = sqlite3.connect('yuktashish.db')
        c = conn.cursor()
        
        c.execute('''
        SELECT id, name, email, role, phone, company_name, vehicle_type 
        FROM users WHERE id = ?
        ''', (session['user_id'],))
        
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"error": "Foydalanuvchi topilmadi"}), 404
        
        return jsonify({
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "phone": user[4],
            "company_name": user[5],
            "vehicle_type": user[6]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Tizimdan chiqish
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Chiqish muvaffaqiyatli"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 10000))

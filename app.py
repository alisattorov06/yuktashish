import sqlite3
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Bazani aniq yo'lini olish
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'yuktashish.db')

# Flask ilovasini yaratish
app = Flask(__name__)
app.secret_key = os.environ.get('ali_sattorov', 'yuk_tashish')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True

# CORS sozlamasi
CORS(app,
     supports_credentials=True,
     resources={
         r"/*": {
             "origins": ["*"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"]
         }
     }
)

# 🛠 Bazani yaratish (har safar ishga tushganda tekshiradi)
def init_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
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
            vehicle_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# ✅ DASTUR ISHGA TUSHISHIDAN OLDIN BAZANI YARATISH
init_db()

# 📥 Ro'yxatdan o'tish
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        required_fields = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Barcha maydonlarni to'ldiring"}), 400

        if len(data['password']) < 6:
            return jsonify({"error": "Parol kamida 6 belgidan iborat bo'lishi kerak"}), 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT id FROM users WHERE email = ?", (data['email'],))
        if c.fetchone():
            conn.close()
            return jsonify({"error": "Bu email allaqachon ro'yxatdan o'tgan"}), 400

        hashed_pw = generate_password_hash(data['password'])

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
            "success": True,
            "message": "Ro'yxatdan o'tish muvaffaqiyatli",
            "user_id": user_id
        }), 201

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Server xatosi"}), 500

# 🔐 Kirish
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email va parol kiritishingiz kerak"}), 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute('''
        SELECT id, name, email, password, role FROM users WHERE email = ?
        ''', (data['email'],))

        user = c.fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "Foydalanuvchi topilmadi"}), 404

        if not check_password_hash(user[3], data['password']):
            return jsonify({"error": "Noto'g'ri parol"}), 401

        session['user_id'] = user[0]
        session['user_email'] = user[2]
        session['user_role'] = user[4]

        return jsonify({
            "success": True,
            "message": "Kirish muvaffaqiyatli",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "role": user[4]
            }
        }), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Server xatosi"}), 500

# 👤 Profil
@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return jsonify({"error": "Kirish talab qilinadi"}), 401

    try:
        conn = sqlite3.connect(DB_PATH)
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
        print(f"Profile error: {e}")
        return jsonify({"error": "Server xatosi"}), 500

# 🚪 Chiqish
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Chiqish muvaffaqiyatli"}), 200

# 🚀 Flask ishga tushirish
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

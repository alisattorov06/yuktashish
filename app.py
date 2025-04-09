import sqlite3
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
CORS(app, supports_credentials=True)

# Yangilangan ma'lumotlar bazasi initsializatsiyasi
def init_db():
    # Yangi foydalanuvchilar jadvali
    users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        tin TEXT,
        phone TEXT,
        address TEXT,
        cargo_type TEXT,
        max_weight REAL,
        max_volume REAL,
        plate_number TEXT
    )
    """
    
    # Yangi yuklar jadvali
    cargos_table_sql = """
    CREATE TABLE IF NOT EXISTS cargos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        direction TEXT NOT NULL,
        weight REAL NOT NULL,
        volume REAL NOT NULL,
        price REAL NOT NULL,
        phone TEXT NOT NULL,
        type TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """
    
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    
    # Jadval mavjud bo'lsa, yangi ustunlarni qo'shish
    try:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # Agar ustun allaqachon mavjud bo'lsa
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN password TEXT")
    except sqlite3.OperationalError:
        pass
        
    c.execute(users_table_sql)
    c.execute(cargos_table_sql)
    conn.commit()
    conn.close()

# Ro'yxatdan o'tish endpointi (yangilangan versiya)
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Ma'lumotlar yo'q"}), 400
            
        required_fields = ['name', 'role', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Barcha maydonlar to'ldirilishi shart"}), 400
            
        hashed_password = generate_password_hash(data['password'])
        
        conn = sqlite3.connect('yuktashish.db')
        c = conn.cursor()
        
        # Qo'shimcha maydonlar uchun standart qiymatlar
        tin = data.get('tin', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        cargo_type = data.get('cargo_type', '')
        max_weight = data.get('max_weight', 0)
        max_volume = data.get('max_volume', 0)
        plate_number = data.get('plate_number', '')
        
        c.execute("""
            INSERT INTO users (name, role, email, password, tin, phone, address, cargo_type, max_weight, max_volume, plate_number) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['name'],
            data['role'],
            data['email'],
            hashed_password,
            tin,
            phone,
            address,
            cargo_type,
            max_weight,
            max_volume,
            plate_number
        ))
        
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
        
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Bu email allaqachon ro'yxatdan o'tgan"}), 400
    except Exception as e:
        print("Xatolik:", str(e))
        return jsonify({"error": "Server xatosi: " + str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

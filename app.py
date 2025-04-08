from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cargos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, direction TEXT, weight REAL, volume REAL, price REAL, phone TEXT, type TEXT)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, role) VALUES (?, ?)", (data['name'], data['role']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Foydalanuvchi ro'yxatdan o'tdi"}), 201

@app.route('/add-cargo', methods=['POST'])
def add_cargo():
    data = request.get_json()
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("INSERT INTO cargos (direction, weight, volume, price, phone, type) VALUES (?, ?, ?, ?, ?, ?)", 
              (data['direction'], data['weight'], data['volume'], data['price'], data['phone'], data['type']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Yuk qo'shildi"}), 201

@app.route('/cargos', methods=['GET'])
def get_cargos():
    conn = sqlite3.connect('yuktashish.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cargos")
    cargos = [{"id": row[0], "direction": row[1], "weight": row[2], "volume": row[3], "price": row[4], "phone": row[5], "type": row[6]} for row in c.fetchall()]
    conn.close()
    return jsonify(cargos), 200

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 10000))  # Render PORTni oladi, aks holda 10000
    app.run(host='0.0.0.0', port=port, debug=True)  # 0.0.0.0 ga bog‘lash

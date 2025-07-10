# file: app.py

from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import pooling

# Memuat variabel dari file .env
load_dotenv()

# --- INISIALISASI APLIKASI ---
app = Flask(__name__)

# --- KONFIGURASI JWT ---
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET')
jwt = JWTManager(app)

# --- KONFIGURASI DATABASE CONNECTION POOL ---
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="ftth_pool",
        pool_size=5,
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
    )
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating database connection pool: {err}")
    exit()

# --- RUTE LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "Request JSON tidak valid"}), 400

    email_from_app = data['username']
    password = data['password']

    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Ubah query untuk mencari berdasarkan kolom 'email'
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email_from_app,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            identity = {"username": user['username'], "role": user['role'], "email": user['email']}
            access_token = create_access_token(identity=identity)
            return jsonify(access_token=access_token)
        else:
            return jsonify({"msg": "Email atau password salah"}), 401

    except mysql.connector.Error as err:
        return jsonify({"msg": "Error pada database", "error": str(err)}), 500
    except Exception as e:
        return jsonify({"msg": "Terjadi kesalahan pada server", "error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
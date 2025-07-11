# file: app.py

from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import pooling
from functiondb import cek_berdasarkan_email, registerpengguna
from database import db_pool

# Memuat variabel dari file .env
load_dotenv()

# --- INISIALISASI APLIKASI ---
app = Flask(__name__)

# --- KONFIGURASI JWT ---
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET')
jwt = JWTManager(app)


# --- RUTE LOGIN ---
@app.route('/api/login', methods=['POST'])
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

# --- RUTE REGISTER ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'nama' not in data or 'email' not in data:
        return jsonify({"msg": "Request JSON tidak valid"}), 400

    nama = data['nama']
    email = data['email']


    cek_user_ada = cek_berdasarkan_email(email)
    if cek_user_ada:
        return jsonify({"msg": "Email sudah terdaftar"}), 409

    cek_tambahkan_user = registerpengguna(nama, email)
    if cek_tambahkan_user:
        return jsonify({"msg": "Pendaftaran berhasil"}), 201
    
    else:
         return jsonify({"msg": "Gagal Daftar"}), 400
    

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
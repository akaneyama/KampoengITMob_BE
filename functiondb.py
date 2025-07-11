
from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import pooling, Error
from database import db_pool
import secrets
import string

load_dotenv()

def cek_berdasarkan_email(email):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result
    except Error as e:
        print("DB error:", str(e))
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def generate_password(length=8):
    allowed = 'abcdefghjkmnpqrstuvwxy123456789'
    return ''.join(secrets.choice(allowed) for _ in range(length))

def registerpengguna(nama, email):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        password = generate_password()
        passwordhashed = generate_password_hash(password)
        query = "INSERT INTO users(email, username, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (nama,email,passwordhashed,))
        conn.commit()
        return cursor.rowcount
    except Error as e:
        print("DB error:", str(e))
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
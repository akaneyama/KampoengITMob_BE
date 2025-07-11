
from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os
import smtplib
import mysql.connector
from mysql.connector import pooling, Error
from database import db_pool
import secrets
import string
from email.message import EmailMessage

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
        cursor.execute(query, (email,nama,passwordhashed,))
        conn.commit()
        try:
            kirim_kode_verifikasi(email,password)
        except Exception as email_err:
            return("Gagal mengirim email:", str(email_err))
            
        return cursor.rowcount
    except Error as e:
        print("DB error:", str(e))
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            
def kirim_kode_verifikasi(email_penerima, password):
    EMAIL_PENGIRIM = os.environ.get('EMAIL_PENGIRIM')
    PASSWORD_EMAIL = os.environ.get('PASSWORD_EMAIL')

    msg = EmailMessage()
    msg['Subject'] = 'Kode Verifikasi Email - Ftth Admin'
    msg['From'] = 'admin@smartcube.biz.id'
    msg['To'] = email_penerima
     # Konten HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
                background-color: #f8f9fa;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
            }}
            .content {{
                padding: 30px;
                text-align: left;
                font-size: 16px;
                line-height: 1.6;
                color: #495057;
            }}
            .code-box {{
                background-color: #f1f3f5;
                border: 1px solid #dee2e6;
                padding: 15px 20px;
                margin: 25px 0;
                text-align: center;
                border-radius: 8px;
            }}
            .code {{
                font-size: 28px;
                font-weight: 700;
                color: #d6336c;
                font-family: 'Courier New', Courier, monospace;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #868e96;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h1 style="color: #343a40; font-size: 24px;">Password Sementara Anda</h1>
                <p>Halo,</p>
                <p>Berikut adalah password sementara Anda yang dapat digunakan untuk masuk ke akun:</p>
                
                <div class="code-box">
                    <span class="code">{password}</span>
                </div>
                
                <p>Kami menyarankan Anda untuk segera mengganti password ini setelah berhasil masuk demi keamanan akun Anda.</p>
                <p>Jika Anda tidak meminta akun atau tidak mengenali email ini, mohon abaikan pesan ini.</p>
                
                <p style="margin-top: 30px;">Terima kasih</p>
            </div>
            <div class="footer">
                <hr style="border: none; border-top: 1px solid #e9ecef; margin-bottom: 20px;">
                <p>Jika Anda memiliki pertanyaan, silakan hubungi <a href="mailto:admin@smartcube.biz.id" style="color: #4f46e5;">dukungan kami</a>.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.set_content(f"password sementara Anda adalah: {password}")  # fallback plain text
    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_PENGIRIM, PASSWORD_EMAIL)
        smtp.send_message(msg)

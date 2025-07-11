from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import pooling
load_dotenv()

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
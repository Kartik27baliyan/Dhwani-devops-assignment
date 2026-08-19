import os
import time
import mariadb
from flask import Flask, jsonify

app = Flask(__name__)

def get_db_connection():
    for i in range(10):
        try:
            conn = mariadb.connect(
                user="root",
                password=os.getenv("DB_PASSWORD"),
                host="db",
                port=3306,
                database="appdb"
            )
            return conn
        except mariadb.Error as e:
            print(f"Waiting for DB... {e}")
            time.sleep(2)
    return None

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS hits (id INT AUTO_INCREMENT PRIMARY KEY, time DATETIME)")
        cur.execute("INSERT INTO hits (time) VALUES (NOW())")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM hits")
        count = cur.fetchone()[0]
        conn.close()
        return f"<h1>Success!</h1><p>Dhwani RIS Assignment - Page hits: {count}</p>"
    return "Database connection failed.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
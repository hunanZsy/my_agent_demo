"""
这是一个用于测试 Code Reviewer 功能的示例代码。
包含安全漏洞、代码异味和逻辑错误。
"""

import sqlite3
import jwt
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# 硬编码的密钥（应该从环境变量读取）
SECRET_KEY = "my-super-secret-key-12345"
DB_PATH = "/tmp/users.db"

# 使用不安全的哈希算法
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# SQL 注入漏洞
def get_user_by_name(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

# 硬编码密码（明文）
def create_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 直接存储明文密码，未加盐
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# 使用弱 JWT 算法，且过期时间过长
def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": 9999999999  # 过期时间设得极其遥远
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# 没有异常处理，可能导致崩溃
def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# 未使用的导入和变量（代码异味）
import os
import sys

unused_var = 42

# 函数复杂度高，嵌套过深
def process_data(data):
    if data:
        if "type" in data:
            if data["type"] == "A":
                for item in data.get("items", []):
                    if item.get("valid"):
                        if item["value"] > 10:
                            print("Processing A")
                        else:
                            print("Skipping low value")
                    else:
                        print("Invalid item")
            else:
                print("Other type")
        else:
            print("No type")
    else:
        print("No data")

# 可能造成资源泄漏（未关闭文件）
def read_file(filename):
    f = open(filename, "r")
    content = f.read()
    return content

# 硬编码的 API 端点（敏感信息泄露）
@app.route("/admin")
def admin_panel():
    return "Admin panel – secret stuff: admin:password123"

# 允许任意 HTTP 方法，可能导致 CSRF
@app.route("/user/<int:user_id>", methods=["GET", "POST", "PUT", "DELETE"])
def user_endpoint(user_id):
    if request.method == "GET":
        return jsonify({"user": f"User {user_id}"})
    elif request.method == "DELETE":
        delete_user(user_id)
        return jsonify({"status": "deleted"})
    return "Method not allowed", 405

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")  # debug=True 且监听所有接口，生产环境危险
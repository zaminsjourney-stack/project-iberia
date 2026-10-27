from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app)

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auth_events.log')

auth_logger = logging.getLogger('auth_events')
auth_logger.setLevel(logging.INFO)
auth_logger.propagate = False

file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | IP: %(ip)s | User: %(user)s | Status: %(status)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
auth_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(file_handler.formatter)
auth_logger.addHandler(console_handler)

USERS = {"admin": "1234", "alice": "sec2026", "bob": "cyber456"}


def get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr


@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ok", "log_file": LOG_FILE})


@app.route('/api/login', methods=['POST'])
def handle_login():
    client_ip = get_client_ip()
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if username in USERS and USERS[username] == password:
        auth_logger.info("Login Successful", extra={'ip': client_ip, 'user': username, 'status': 'SUCCESS'})
        return jsonify({"success": True, "message": "Login successful!"})

    auth_logger.warning("Login Failed", extra={'ip': client_ip, 'user': username or '-', 'status': 'FAILED'})
    return jsonify({"success": False, "message": "Invalid username or password"}), 401


if __name__ == '__main__':
    print(f"Writing auth logs to: {LOG_FILE}")
    app.run(host='0.0.0.0', port=5000, debug=False)

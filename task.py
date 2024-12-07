import http.server
import socketserver
import socket
import os
from datetime import datetime
import json
import threading
from pymongo import MongoClient

HOST_NAME = "localhost"
HTTP_PORT = 3000
SOCKET_PORT = 5000
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "messages_db"
COLLECTION_NAME = "messages"

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# HTTP Request Handler
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            self.path = "index.html"
        elif self.path == "/message.html":
            self.path = "message.html"
        elif self.path == "/style.css":
            self.path = "style.css"
        elif self.path == "/logo.png":
            self.path = "logo.png"
        else:
            self.path = "error.html"
        return super().do_GET()

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode("utf-8")
            fields = dict(field.split("=") for field in post_data.split("&"))
            
            username = fields.get("username", "Unknown")
            message = fields.get("message", "")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST_NAME, SOCKET_PORT))
                data = json.dumps({"username": username, "message": message, "date": str(datetime.now())})
                sock.sendall(data.encode("utf-8"))

            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()

# Socket Server Functionality
def socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_NAME, SOCKET_PORT))
    server.listen(5)
    print(f"Socket server listening on {SOCKET_PORT}")

    while True:
        client_socket, _ = server.accept()
        with client_socket:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                continue
            message_data = json.loads(data)
            collection.insert_one(message_data)
            print(f"Message saved: {message_data}")

if __name__ == "__main__":
    # Start socket server in a separate thread
    socket_thread = threading.Thread(target=socket_server, daemon=True)
    socket_thread.start()

    # Start HTTP server
    with socketserver.TCPServer((HOST_NAME, HTTP_PORT), CustomHTTPRequestHandler) as httpd:
        print(f"HTTP server running on port {HTTP_PORT}")
        httpd.serve_forever()
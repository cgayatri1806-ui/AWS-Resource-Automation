from wsgiref.simple_server import make_server
from src.app import app

print("Starting AWS Resource Automation API...")
print("API: http://127.0.0.1:5000")

server = make_server("127.0.0.1", 5000, app)

print("SERVER RUNNING")
server.serve_forever()
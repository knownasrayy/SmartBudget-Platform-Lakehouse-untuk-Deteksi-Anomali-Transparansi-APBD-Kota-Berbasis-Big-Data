import http.server
import socketserver
import os
import socket

PORT = 8080

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Base directory is the project root
        base_dir = os.getcwd()
        
        # Route root to the dashboard index
        if path == '/' or path == '/index.html':
            return os.path.join(base_dir, 'src', 'dashboard', 'index.html')
            
        # Route dashboard assets directly
        if path.startswith('/assets/'):
            return os.path.join(base_dir, 'src', 'dashboard', path.lstrip('/'))
            
        # Everything else falls back to the default handler
        # which correctly maps to the project root (e.g. /data/gold/...)
        return super().translate_path(path)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Allow reusing the port if restarting quickly
socketserver.TCPServer.allow_reuse_address = True

with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), DashboardHandler) as httpd:
    ip = get_local_ip()
    print("==================================================")
    print(f"SmartBudget Dashboard is now LIVE!")
    print(f"   Akses melalui Localhost : http://localhost:{PORT}")
    print(f"   Akses melalui Jaringan  : http://{ip}:{PORT}")
    print("==================================================")
    print("Tekan Ctrl+C untuk menghentikan server.")
    httpd.serve_forever()

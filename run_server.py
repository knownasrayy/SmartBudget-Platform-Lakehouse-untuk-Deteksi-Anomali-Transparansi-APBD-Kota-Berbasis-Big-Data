import uvicorn
import socket

PORT = 8080

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    ip = get_local_ip()
    print("==================================================")
    print(f"SmartBudget Dashboard & FastAPI is now LIVE!")
    print(f"   Akses melalui Localhost : http://localhost:{PORT}")
    print(f"   Akses melalui Jaringan  : http://{ip}:{PORT}")
    print("==================================================")
    print("Menjalankan Uvicorn server...")
    
    # Run the FastAPI app via Uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=PORT, reload=True)

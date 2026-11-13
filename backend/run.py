import os
from app import create_app
from app.extensions import db
from seed_data import seed_database

env_mode = os.environ.get("FLASK_ENV", "development")
app = create_app(env_mode)

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))
    host_ip = app.config.get("HOST_IP", "127.0.0.1")
    
    print("\n" + "="*65)
    print("      MEDICARE CLOUD - HEALTHCARE MONITORING & REMINDER SYSTEM")
    print("="*65)
    print(f"[*] Local Machine Access:  http://127.0.0.1:{port}")
    print(f"[*] Phone / Wi-Fi Access:   http://{host_ip}:{port}")
    print(f"[*] Consultant Login:      http://127.0.0.1:{port}/login")
    print(f"[*] Patient Web Dashboard: http://127.0.0.1:{port}/login (Role: Patient)")
    print("="*65 + "\n")
    
    app.run(host=host, port=port, debug=False)

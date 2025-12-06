# check_google_auth.py
from app import app, db
from sqlalchemy import text

def check_and_create_tables():
    with app.app_context():
        try:
            # Kiểm tra bảng GoogleAuth
            result = db.session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='GoogleAuth'
            """)).fetchone()
            
            if result:
                print("✅ Bảng GoogleAuth đã tồn tại")
                
                # Kiểm tra cấu trúc bảng
                columns = db.session.execute(text("PRAGMA table_info(GoogleAuth)")).fetchall()
                print("📊 Cấu trúc bảng GoogleAuth:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                    
                # Đếm số bản ghi
                count = db.session.execute(text("SELECT COUNT(*) FROM GoogleAuth")).fetchone()[0]
                print(f"📈 Số bản ghi: {count}")
                
            else:
                print("❌ Bảng GoogleAuth chưa tồn tại. Đang tạo...")
                
                # Tạo bảng GoogleAuth
                create_table = text('''
                    CREATE TABLE GoogleAuth (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        google_id VARCHAR(255) NOT NULL UNIQUE,
                        email VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
                    )
                ''')
                
                create_index1 = text('''
                    CREATE INDEX idx_google_auth_user_id ON GoogleAuth(user_id)
                ''')
                
                create_index2 = text('''
                    CREATE INDEX idx_google_auth_google_id ON GoogleAuth(google_id)
                ''')
                
                db.session.execute(create_table)
                db.session.execute(create_index1)
                db.session.execute(create_index2)
                db.session.commit()
                
                print("✅ Đã tạo bảng GoogleAuth thành công!")
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    check_and_create_tables()
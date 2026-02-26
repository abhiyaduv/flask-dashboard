import sqlite3

conn = sqlite3.connect("database.db")

conn.execute(
    "INSERT INTO users(username,password) VALUES('admin','123')"
)

conn.commit()
conn.close()

print("✅ Admin user created successfully!")
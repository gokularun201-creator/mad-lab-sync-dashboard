import os
import sqlite3
import datetime
import webbrowser
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mad_records.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            salary TEXT NOT NULL,
            device_source TEXT DEFAULT 'Android Mobile',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Pre-populate with known lab records if empty
    cursor.execute("SELECT COUNT(*) FROM records")
    count = cursor.fetchone()[0]
    if count == 0:
        samples = [
            ("231121101164", "gokul", "10000", "Android Phone", "2026-11-17 14:15:00"),
            ("231121101137", "Aditya", "50000", "Android Phone", "2026-11-17 14:18:22"),
            ("231121100", "Gokul NS", "100000", "Android Phone", "2026-11-17 14:20:10"),
            ("101", "Arun", "50000", "Android Phone", "2026-11-17 14:26:45")
        ]
        cursor.executemany("""
            INSERT OR REPLACE INTO records (id, name, salary, device_source, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, samples)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/records", methods=["GET"])
def get_records():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, salary, device_source, created_at FROM records ORDER BY created_at DESC")
    rows = cursor.fetchall()
    records = []
    total_salary = 0.0
    for r in rows:
        try:
            sal_num = float(r["salary"].replace(",", "").strip())
        except Exception:
            sal_num = 0.0
        total_salary += sal_num
        records.append({
            "id": r["id"],
            "name": r["name"],
            "salary": r["salary"],
            "device_source": r["device_source"] or "Android Mobile",
            "created_at": r["created_at"]
        })
    conn.close()

    avg_salary = (total_salary / len(records)) if records else 0.0
    return jsonify({
        "success": True,
        "count": len(records),
        "total_salary": f"{total_salary:,.2f}",
        "avg_salary": f"{avg_salary:,.2f}",
        "records": records
    })

@app.route("/api/records", methods=["POST"])
def add_record():
    data = request.get_json(silent=True) or request.form.to_dict()
    emp_id = (data.get("id") or data.get("employee_id") or "").strip()
    name = (data.get("name") or data.get("employee_name") or "").strip()
    salary = (data.get("salary") or data.get("employee_salary") or "").strip()
    source = data.get("device_source") or data.get("source") or "Android Mobile"

    if not emp_id or not name or not salary:
        return jsonify({"success": False, "error": "ID, Name, and Salary are required."}), 400

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO records (id, name, salary, device_source, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            salary=excluded.salary,
            device_source=excluded.device_source,
            created_at=excluded.created_at
    """, (emp_id, name, salary, source, now_str))
    conn.commit()
    conn.close()

    print(f"[*] SYNC RECEIVED from {source}: ID={emp_id}, Name={name}, Salary={salary}")

    return jsonify({
        "success": True,
        "message": f"Record for {name} (ID: {emp_id}) saved successfully to SQL database!",
        "record": {
            "id": emp_id,
            "name": name,
            "salary": salary,
            "device_source": source,
            "created_at": now_str
        }
    })

@app.route("/api/records/<emp_id>", methods=["DELETE"])
def delete_record(emp_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Record {emp_id} deleted."})

@app.route("/api/clear", methods=["POST"])
def clear_records():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records")
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "All database records cleared."})

@app.route("/api/export/csv")
def export_csv():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, salary, device_source, created_at FROM records ORDER BY created_at ASC")
    rows = cursor.fetchall()
    conn.close()

    output = "ID,Name,Salary,DeviceSource,Timestamp\n"
    for r in rows:
        output += f'"{r["id"]}","{r["name"]}","{r["salary"]}","{r["device_source"]}","{r["created_at"]}"\n'

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=mad_lab_sql_database_records.csv"}
    )

@app.route("/health")
def health():
    return jsonify({"status": "online", "time": datetime.datetime.now().isoformat()})

if __name__ == "__main__":
    print("=" * 65)
    print("  MAD LAB SQL DATABASE - LOCALHOST REAL-TIME SYNC SERVER")
    print("=" * 65)
    print("  * Local URL:    http://localhost:5000")
    print("  * Network URL:  http://0.0.0.0:5000")
    print("  * SQLite File:  " + DB_PATH)
    print("=" * 65)
    app.run(host="0.0.0.0", port=5000, debug=False)

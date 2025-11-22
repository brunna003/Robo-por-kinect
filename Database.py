# banco_gestos.py
import sqlite3
from datetime import datetime

DB_NAME = "gestos.db"

def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS historico_gestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gesto TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def salvar_gesto(gesto):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO historico_gestos (gesto, timestamp) VALUES (?, ?)", (gesto, agora))
    conn.commit()

    # Limitar aos 100 últimos gestos
    c.execute("SELECT COUNT(*) FROM historico_gestos")
    total = c.fetchone()[0]
    if total > 100:
        excesso = total - 100
        c.execute("DELETE FROM historico_gestos WHERE id IN (SELECT id FROM historico_gestos ORDER BY id ASC LIMIT ?)", (excesso,))
        conn.commit()

    conn.close()

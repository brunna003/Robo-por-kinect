# ler_gestos.py
import sqlite3

DB_NAME = "gestos.db"

def ler_ultimos_gestos(qtd=100):
    """Lê os últimos gestos salvos no banco."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT gesto, timestamp FROM historico_gestos ORDER BY id DESC LIMIT ?", (qtd,))
    gestos = c.fetchall()
    conn.close()
    return gestos

def main():
    gestos = ler_ultimos_gestos()
    if not gestos:
        print("Nenhum gesto registrado ainda.")
    else:
        print(f"Últimos {len(gestos)} gestos detectados:\n")
        for i, (gesto, tempo) in enumerate(gestos, 1):
            print(f"{i:03d}. {gesto} — {tempo}")

if __name__ == "__main__":
    main()

from flask import Flask
import sqlite3

app = Flask(__name__)

@app.route("/")
def painel():
    conn = sqlite3.connect("/tmp/vip.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green'")
    green = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red'")
    red = c.fetchone()[0]
    total = green + red
    winrate = (green / total * 100) if total > 0 else 0

    return f"""
    <h1>VIP DASHBOARD INSTITUCIONAL</h1>
    <h2>Green: {green}</h2>
    <h2>Red: {red}</h2>
    <h2>Winrate: {winrate:.2f}%</h2>
    """

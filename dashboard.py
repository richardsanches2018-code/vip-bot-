from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_stats():
    conn = sqlite3.connect("/tmp/stats.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green'")
    green = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red'")
    red = c.fetchone()[0]
    return green, red

@app.route("/")
def index():
    green, red = get_stats()
    total = green + red
    winrate = (green / total * 100) if total > 0 else 0
    return f"""
    <h1>VIP DASHBOARD</h1>
    <h2>Green: {green}</h2>
    <h2>Red: {red}</h2>
    <h2>Winrate: {winrate:.2f}%</h2>
    """

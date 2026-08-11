import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
DB_FILE = "dados.db"

# Função para conectar ao banco de dados
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transacoes 
                      (id INTEGER PRIMARY KEY, tipo TEXT, descricao TEXT, valor REAL, 
                       categoria TEXT, metodo TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- INTERFACE (Mesma de antes) ---
HTML_FINANCAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AOS Soluções - Seu Agente Financeiro</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: sans-serif; background: #f4f4f9; padding: 10px; margin: 0; }
        .container { max-width: 400px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .logo-container { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 5px; }
        .logo-icone { background: #2c3e50; color: white; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold; font-size: 16px; }
        h1 { font-size: 18px; color: #2c3e50; margin: 0; }
        .subtitulo { font-size: 12px; text-align: center; color: #7f8c8d; margin-bottom: 15px; }
        .resumo-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; margin-bottom: 15px; }
        .btn-resumo { padding: 10px 5px; border-radius: 8px; color: white; font-size: 11px; text-align: center; font-weight: bold; }
        .bg-credito { background: #e74c3c; }
        .bg-debito { background: #3498db; }
        .bg-pix { background: #27ae60; }
        form { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }
        input, select, button { padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        .extrato { font-size: 13px; margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px; }
        .item-gasto { color: #c0392b; }
        .item-ganho { color: #27ae60; font-weight: bold; }
        .btn-remover { background: #e74c3c; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-container">
            <div class="logo-icone">AOS</div>
            <h1>AOS Soluções</h1>
        </div>
        <div class="subtitulo">Seu Agente Financeiro</div>

        <div class="resumo-grid">
            <div class="btn-resumo bg-credito">CRÉD<br>R$ {{ "%.2f"|format(totais.Credito) }}</div>
            <div class="btn-resumo bg-debito">DÉB<br>R$ {{ "%.2f"|format(totais.Debito) }}</div>
            <div class="btn-resumo bg-pix">PIX<br>R$ {{ "%.2f"|format(totais.Pix) }}</div>
        </div>

        <form action="/adicionar" method="POST">
            <select name="tipo" required>
                <option value="Gasto">📉 Gasto</option>
                <option value="Ganho">📈 Ganho</option>
            </select>
            <input type="date" name="data" required>
            <input type="text" name="descricao" placeholder="Descrição" required>
            <input type="number" step="0.01" name="valor" placeholder="Valor R$" required>
            <select name="categoria">
                <option value="Academia">Academia</option>
                <option value="Alimentação">Alimentação</option>
                <option value="Salário">Salário</option>
                <option value="Outros">Outros</option>
            </select>
            <select name="metodo">
                <option value="Pix">Pix</option>
                <option value="Debito">Débito</option>
                <option value="Credito">Crédito</option>
            </select>
            <button type="submit" style="background:#2c3e50; color:white; font-weight:bold; cursor:pointer;">REGISTRAR</button>
        </form>

        <div class="extrato">
            <h4>Histórico:</h4>
            {% for t in transacoes %}
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding: 6px 0;">
                    <div><small>{{ t[6] }}</small><br><strong>{{ t[2] }}</strong></div>
                    <div style="text-align: right;">
                        <span class="{{ 'item-ganho' if t[1] == 'Ganho' else 'item-gasto' }}">
                            {{ '+' if t[1] == 'Ganho' else '-' }} R$ {{ "%.2f"|format(t[3]) }}
                        </span>
                    </div>
                    <form action="/remover/{{ t[0] }}" method="POST"><button type="submit" class="btn-remover">X</button></form>
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transacoes ORDER BY data DESC")
    transacoes = cursor.fetchall()
    
    # Calcular totais (simplificado para o exemplo)
    totais = {'Credito': 0, 'Debito': 0, 'Pix': 0}
    for t in transacoes:
        if t[1] == 'Gasto' and t[5] in totais:
            totais[t[5]] += t[3]
    conn.close()
    
    return render_template_string(HTML_FINANCAS, transacoes=transacoes, totais=totais)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transacoes (tipo, descricao, valor, categoria, metodo, data) VALUES (?,?,?,?,?,?)",
                   (request.form['tipo'], request.form['descricao'], float(request.form['valor']), 
                    request.form['categoria'], request.form['metodo'], request.form['data']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/remover/<int:id>', methods=['POST'])
def remover(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
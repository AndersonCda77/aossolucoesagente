from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
transacoes = []

# --- INTERFACE DO AGENTE FINANCEIRO (AOS SOLUÇÕES) ---
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
            <div class="btn-resumo bg-credito">CRÉD (Hoje)<br>R$ {{ "%.2f"|format(totais_hoje.Credito) }}</div>
            <div class="btn-resumo bg-debito">DÉB (Hoje)<br>R$ {{ "%.2f"|format(totais_hoje.Debito) }}</div>
            <div class="btn-resumo bg-pix">PIX (Hoje)<br>R$ {{ "%.2f"|format(totais_hoje.Pix) }}</div>
        </div>

        <div style="background: #eef2f7; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-size: 13px;">
            <span style="color: #27ae60;">Ganhos: R$ {{ "%.2f"|format(total_ganhos) }}</span> | 
            <span style="color: #c0392b;">Gastos: R$ {{ "%.2f"|format(total_gastos) }}</span><br>
            <span style="color: #2980b9; font-weight: bold;">Total deste Mês: R$ {{ "%.2f"|format(total_mes) }}</span><br>
            <strong>Saldo Geral: R$ {{ "%.2f"|format(saldo) }}</strong>
        </div>

        <form action="/adicionar" method="POST">
            <select name="tipo" required>
                <option value="Gasto">📉 Gasto (Saída)</option>
                <option value="Ganho">📈 Ganho (Entrada)</option>
            </select>
            <input type="date" name="data" required>
            <input type="text" name="descricao" placeholder="Descrição (ex: Uber, Academia...)" required>
            <input type="number" step="0.01" name="valor" placeholder="Valor R$" required>
            <select name="categoria">
                <option value="Academia">Academia</option>
                <option value="Locomoção (App)">Locomoção (App)</option>
                <option value="Futebol">Futebol</option>
                <option value="Salário">Salário</option>
                <option value="Prestação de Serviço">Prestação de Serviço</option>
                <option value="Alimentação">Alimentação</option>
                <option value="Lazer">Lazer</option>
                <option value="Contas">Contas</option>
                <option value="Outros">Outros</option>
            </select>
            <select name="metodo">
                <option value="Pix">Pix</option>
                <option value="Debito">Débito</option>
                <option value="Credito">Crédito</option>
                <option value="Dinheiro">Dinheiro</option>
            </select>
            <button type="submit" style="background:#2c3e50; color:white; font-weight:bold; cursor:pointer;">REGISTRAR</button>
        </form>

        <h4 style="text-align:center; margin-bottom:5px;">Gastos por Categoria (Este Mês)</h4>
        <canvas id="meuGrafico"></canvas>

        <div class="extrato">
            <h4>Histórico Recente:</h4>
            {% for indice, t in transacoes %}
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #f0f0f0; padding-bottom: 6px;">
                    <div>
                        <small>{{ t.data }}</small><br>
                        <strong>{{ t.descricao }}</strong> <small>({{ t.categoria }})</small>
                    </div>
                    <div style="text-align: right;">
                        <span class="{{ 'item-ganho' if t.tipo == 'Ganho' else 'item-gasto' }}">
                            {{ '+' if t.tipo == 'Ganho' else '-' }} R$ {{ "%.2f"|format(t.valor) }}
                        </span><br>
                        <small>{{ t.metodo }}</small>
                    </div>
                    <div>
                        <form action="/remover/{{ indice }}" method="POST" style="margin: 0;">
                            <button type="submit" class="btn-remover">X</button>
                        </form>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>

    <script>
        const ctx = document.getElementById('meuGrafico').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: [{% for cat, val in categorias.items() %}'{{ cat }}',{% endfor %}],
                datasets: [{
                    data: [{% for cat, val in categorias.items() %}{{ val }},{% endfor %}],
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
                }]
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    hoje = datetime.now().strftime('%Y-%m-%d')
    mes_atual = datetime.now().strftime('%Y-%m')
    
    gastos_hoje = [t for t in transacoes if t['tipo'] == 'Gasto' and t['data'] == hoje]
    totais_hoje = {'Credito': 0, 'Debito': 0, 'Pix': 0}
    for item in gastos_hoje:
        metodo = item['metodo']
        if metodo in totais_hoje:
            totais_hoje[metodo] += item['valor']
            
    total_gastos = sum(t['valor'] for t in transacoes if t['tipo'] == 'Gasto')
    total_ganhos = sum(t['valor'] for t in transacoes if t['tipo'] == 'Ganho')
    saldo = total_ganhos - total_gastos
    total_mes = sum(t['valor'] for t in transacoes if t['tipo'] == 'Gasto' and t['data'].startswith(mes_atual))
    
    categorias_mes = {}
    for item in transacoes:
        if item['tipo'] == 'Gasto' and item['data'].startswith(mes_atual):
            cat = item['categoria']
            categorias_mes[cat] = categorias_mes.get(cat, 0) + item['valor']
            
    transacoes_ordenadas = sorted(enumerate(transacoes), key=lambda x: x[1]['data'], reverse=True)
    
    return render_template_string(HTML_FINANCAS, 
                                  transacoes=transacoes_ordenadas, 
                                  totais_hoje=totais_hoje, 
                                  total_gastos=total_gastos,
                                  total_ganhos=total_ganhos,
                                  total_mes=total_mes,
                                  saldo=saldo,
                                  categorias=categorias_mes)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    transacoes.append({
        'tipo': request.form.get('tipo'),
        'descricao': request.form.get('descricao'),
        'valor': float(request.form.get('valor')),
        'categoria': request.form.get('categoria'),
        'metodo': request.form.get('metodo'),
        'data': request.form.get('data') or datetime.now().strftime('%Y-%m-%d')
    })
    return redirect(url_for('index'))

@app.route('/remover/<int:indice>', methods=['POST'])
def remover(indice):
    if 0 <= indice < len(transacoes):
        transacoes.pop(indice)
    return redirect(url_for('index'))

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
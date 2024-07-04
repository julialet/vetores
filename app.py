from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import json
import time
import seaborn as sns
import matplotlib.pyplot as plt
import random
import io
import base64

# MANIPULAÇÃO DO VETOR
def generate_random_data():
    return [random.randint(0, 50) for _ in range(10)], [random.randint(0, 50) for _ in range(10)]

# EMBARALHAR VETOR !!!!!!
def embaralhar_strip(vetor):
    tamanho = len(vetor)
    meio = tamanho // 2
    parte_impar = vetor[:meio]
    parte_par = vetor[meio:]
    vetor_embaralhado = []
    for i in range(meio):
        vetor_embaralhado.append(parte_impar[i]) #itera sobre a primeira parte do vetor original, aq ele adiciona os vetores impares
        vetor_embaralhado.append(parte_par[i]) # adiciona o vetor correspondente da parte par ao vetor embaralhado
        
    if tamanho % 2 == 1:
        vetor_embaralhado.append(vetor[-1]) # se o tamanho original do vetor for impar, adiciona o último elemento ao vetor embaralhado
    
    return vetor_embaralhado

# ALGORITMO DE SORT
def quicksort(vetor): 
    if len(vetor) <= 1:
        return vetor
    
    stack = [(0, len(vetor) - 1)] #inicializa uma pilha pra armazenar os limites dos subvetores a serem ordenados
    while stack: #loop principal
        low, high = stack.pop() #remove os limites do próximo subvetor a ser ordenado da pilha
        if low < high:
            pivot = vetor[high] #seleciona um pivo pra dividir o subvetor
            i = low - 1
            for j in range(low, high): #particiona o subvetor em elementos menores e maiores que o pivo
                if vetor[j] < pivot:
                    i += 1
                    vetor[i], vetor[j] = vetor[j], vetor[i] #Troca os elementos para colocar os menores que o pivô à esquerda e os maiores à direita
            vetor[i + 1], vetor[high] = vetor[high], vetor[i + 1] #coloca o pivo na posicao correta
            p = i + 1
            
            stack.append((low, p - 1)) #Adiciona os limites dos subvetores menores e maiores que o pivô na pilha
            stack.append((p + 1, high))
            
    return vetor

# INTERAÇÃO COM O BANCO
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ju2109@localhost/db1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #integracao com a database 
db = SQLAlchemy(app)

class Vetor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numeros = db.Column(db.Text)
    tempo_ordenacao = db.Column(db.Float) #integracao com a database 
    tempo_embaralho = db.Column(db.Float)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/gerar_vetor', methods=['GET', 'POST'])
def gerar_vetor():
    vetor = None
    if request.method == 'POST':
        numeros = list(range(1, 5001))
        vetor = Vetor(numeros=json.dumps(numeros))
        db.session.add(vetor)
        db.session.commit()
        return redirect(url_for('gerar_vetor'))
    else:
        vetor = list(range(1, 5001))
    return render_template('gerar_vetor.html', vetor=vetor)

@app.route('/embaralhar', methods=['POST'])
def embaralhar():
    vetor_json = request.form.get('vetor')
    if vetor_json:
        vetor = json.loads(vetor_json)
        start_time = time.time()
        vetor_embaralhado = embaralhar_strip(vetor)
        end_time = time.time()
        execution_time = end_time - start_time
        vetor_embaralhado_db = Vetor(numeros=json.dumps(vetor_embaralhado), tempo_embaralho=execution_time)
        db.session.add(vetor_embaralhado_db)
        db.session.commit()
        return render_template('embaralhar.html', vetor=vetor_embaralhado, tempo_embaralho=execution_time)
    else:
        return redirect(url_for('gerar_vetor'))

@app.route('/ordenado', methods=['POST'])
def ordenar():
    vetor_json = request.form.get('vetor')
    if vetor_json:
        vetor = json.loads(vetor_json)
        start_time = time.time()
        sorted_vetor = quicksort(vetor)
        end_time = time.time()
        execution_time = end_time - start_time
        
        vetor_ordenado = Vetor(numeros=json.dumps(sorted_vetor), tempo_ordenacao=execution_time)
        db.session.add(vetor_ordenado)
        db.session.commit()
        
        return render_template('ordenado.html', vetor=sorted_vetor, tempo_ordenacao=execution_time)
    else:
        return redirect(url_for('gerar_vetor'))

@app.route('/download_json', methods=['POST'])
def download_json():
    vetor_json = request.form.get('vetor_ordenado')
    if vetor_json:
        vetor = json.loads(vetor_json)
        response = jsonify(vetor)
        response.headers['Content-Disposition'] = 'attachment; filename=vetor_ordenado.json'
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return redirect(url_for('gerar_vetor'))

scatter_img = None
line_img = None
bar_img = None

# GERAÇÃO DE GRÁFICOS
@app.route('/graficos')
def graficos():
    global scatter_img, line_img, bar_img
    
    x, y = generate_random_data()

    sns.set(style="whitegrid")  
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=x, y=y)
    scatter_img = io.BytesIO()
    plt.savefig(scatter_img, format='png')
    scatter_img.seek(0)
    scatter_plot_url = base64.b64encode(scatter_img.getvalue()).decode()

    plt.figure(figsize=(8, 6))
    sns.lineplot(x=x, y=y)
    line_img = io.BytesIO()
    plt.savefig(line_img, format='png')
    line_img.seek(0)
    line_chart_url = base64.b64encode(line_img.getvalue()).decode()

    plt.figure(figsize=(8, 6))
    sns.barplot(x=x, y=y)
    bar_img = io.BytesIO()
    plt.savefig(bar_img, format='png')
    bar_img.seek(0)
    bar_chart_url = base64.b64encode(bar_img.getvalue()).decode()

    return render_template('graficos.html', scatter_plot_url=scatter_plot_url, line_chart_url=line_chart_url, bar_chart_url=bar_chart_url)

@app.route('/download_scatter_plot', methods=['POST'])
def download_scatter_plot():
    global scatter_img
    if scatter_img:
        scatter_img.seek(0)
        return send_file(
            scatter_img,
            mimetype='image/png',
            as_attachment=True,
            download_name='scatter_plot.png' 
        )
    else:
        return "Scatter plot não encontrado."

@app.route('/download_line_chart', methods=['POST'])
def download_line_chart():
    global line_img
    if line_img:
        line_img.seek(0)
        return send_file(
            line_img,
            mimetype='image/png',
            as_attachment=True,
            download_name='line_chart.png' 
        )
    else:
        return "Line chart não encontrado."

@app.route('/download_bar_chart', methods=['POST'])
def download_bar_chart():
    global bar_img
    if bar_img:
        bar_img.seek(0)
        return send_file(
            bar_img,
            mimetype='image/png',
            as_attachment=True,
            download_name='bar_chart.png'  
        )
    else:
        return "Bar chart não encontrado."

# MAIN
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#app


from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para sessões

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    configuracoes = [
        {"nome": "Configuração 1", "descricao": "Explica configuração 1", "valor": "Sim"},
        {"nome": "Configuração 2", "descricao": "Explica configuração 2", "valor": "Não"},
        {"nome": "Configuração 3", "descricao": "Explica configuração 3", "valor": "URL"},
        {"nome": "Configuração 4", "descricao": "Explica configuração 4", "valor": "SSH"}
    ]

    
    return render_template('settings.html', configuracao=configuracoes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Verificação básica (substitua por verificação real)
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciais inválidas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/faleconosco', methods=['GET', 'POST'])
def faleconosco():
    if request.method == 'POST':
        nome = request.form.get('name')
        email = request.form.get('email')
        assunto = request.form.get('subject')
        mensagem = request.form.get('message')
        
        # Aqui você pode adicionar lógica para enviar email ou salvar no banco de dados
        print(f"Mensagem recebida de {nome} ({email}): {assunto} - {mensagem}")
        
        flash('Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('faleconosco'))
    
    return render_template('faleconosco.html')

@app.route('/preco')
def preco():
    return render_template('preco.html')

if __name__ == '__main__':
    app.run(debug=True)
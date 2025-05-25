#app/routes
from flask import render_template, request, redirect, url_for, flash
from app import app, db
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            nome_usuario=form.username.data,
            nome_empresa='Minha Empresa',
            email=form.email.data
        )
        user.set_senha(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('cadastro.html', title='Cadastro', form=form)


@app.route('/settings')
@login_required
def settings():
    configuracoes = [
        {"nome": "Configuração 1", "descricao": "Explica configuração 1", "valor": "Sim"},
        {"nome": "Configuração 2", "descricao": "Explica configuração 2", "valor": "Não"},
        {"nome": "Configuração 3", "descricao": "Explica configuração 3", "valor": "URL"},
        {"nome": "Configuração 4", "descricao": "Explica configuração 4", "valor": "SSH"}
    ]
    return render_template('settings.html', configuracao=configuracoes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_senha(form.password.data):
            flash('Credenciais inválidas. Tente novamente.', 'danger')
            return render_template('login.html', form=form)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') or url_for('dashboard')
        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
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

        print(f"Mensagem recebida de {nome} ({email}): {assunto} - {mensagem}")
        flash('Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('faleconosco'))

    return render_template('faleconosco.html')


@app.route('/preco')
def preco():
    return render_template('preco.html')

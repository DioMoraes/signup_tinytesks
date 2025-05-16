from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os


from parameters import countries, languages


app = Flask(__name__)
app.secret_key = '***************'

# Configurações do banco de dados (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscribers.db'
db = SQLAlchemy(app)

# Configurações do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'diogomoraes53@gmail.com'
app.config['MAIL_PASSWORD'] = 'aort pmob mkee jqeq'
mail = Mail(app)

# Modelo de banco de dados
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    telephone  = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    country = db.Column(db.String(10), nullable=False)
    languages  = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(30), nullable=False)

# Rota principal: inscrição
@app.route('/', methods=['GET', 'POST'])
def index():
    selected_languages = []
    other_language_text = ''
    if request.method == 'POST':
        
        name = request.form['full_name']
        telephone = request.form['phone']
        email = request.form['email']
        country = request.form['country']
        gender = request.form['gender']
        selected_languages = request.form.getlist('languages')# IMPORTANTE: getlist para múltiplos valores
        other_language = request.form.get('other_language_text', '').strip()
        if other_language:
            selected_languages = [lang for lang in selected_languages if lang != 'Other']
            selected_languages.append(other_language)

        # Verifica se o email já está cadastrado
        if Subscriber.query.filter_by(email=email).first():
            flash('Este e-mail já está inscrito.', 'warning')
            return redirect(url_for('index'))

        novo_subscriber = Subscriber(
            name=name,
            telephone=telephone,
            email=email,
            country=country,
            languages = ', '.join(selected_languages),
            gender=gender
        )
        db.session.add(novo_subscriber)
        db.session.commit()

        flash('Inscrição realizada com sucesso!', 'success')
        return redirect(url_for('index'))
    
    return render_template('index.html', countries=countries, languages = languages,selected_languages=selected_languages,
                           other_language_text=other_language_text)


# Rota para envio de newsletter
@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        subject = request.form['subject']
        body = request.form['body']
        subscribers = Subscriber.query.all()
        for subscriber in subscribers:
            msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[subscriber.email])
            msg.body = body
            mail.send(msg)
        flash('Mensagem a ser enviada para todos os inscritos!', 'info')
        return redirect('/send')
    return render_template('send.html')

if __name__ == '__main__':
    

    
    with app.app_context():
        db.create_all()
    app.run(debug=True)

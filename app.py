from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import Form, SelectField, BooleanField
from wtforms.validators import DataRequired

app = Flask(__name__, static_url_path='/static')  # Agregamos static_url_path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))
    nivel_mercadolibre = db.Column(db.Boolean, default=False)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service = db.Column(db.String(80))
    plan = db.Column(db.String(80))
    cost = db.Column(db.Float)


class SubscriptionForm(Form):
    service = SelectField('Service', choices=[('Netflix', 'Netflix'), ('HBO', 'HBO'), ('Star+', 'Star+'),
                                             ('Disney+', 'Disney+'), ('Prime Video', 'Prime Video'), ('Paramount', 'Paramount')],
                          validators=[DataRequired()])
    plan = SelectField('Plan', choices=[('No tengo esta suscripción', 'No tengo esta suscripción')],
                      validators=[DataRequired()])
    level_6 = BooleanField('¿Tiene Mercado Libre nivel 6?')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def home():
    form = SubscriptionForm(request.form)
    return render_template('home.html', form=form)


@app.route('/select_subscriptions', methods=['POST'])
@login_required
def select_subscriptions():
    form = SubscriptionForm(request.form)
    if form.validate():
        subscription = Subscription(user_id=current_user.id, service=form.service.data, plan=form.plan.data,
                                    cost=calculate_cost(form.service.data, form.plan.data))
        db.session.add(subscription)
        db.session.commit()
        flash('Subscription added successfully', 'success')
    else:
        flash('Invalid input. Please try again.', 'danger')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/calculate')
@login_required
def calculate_subscriptions():
    # Asegúrate de que 'servicios' contiene tus datos, por ejemplo, tus servicios disponibles y planes
    servicios = {
        "Netflix": {"Estándar": 2990.24, "Premium": 5170.13},
        "HBO": {"Mensual": 1216},
        "Star+": {"Anual": 1749},
        "Disney+": {"Mensual": 800},
        "Prime Video": {"Mensual": 344.25},
        "Paramount": {"Anual": 3097.70, "Mensual": 344.25}
    }

    return render_template('calculate.html', servicios=servicios)


def calculate_cost(service, plan):
    # Implementa tu lógica de cálculo de costos aquí
    # Puedes utilizar un diccionario o búsqueda en la base de datos como en tu código original
    # Devuelve el costo calculado como un número de punto flotante
    pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Profile, FoodEntry, Workout
from app import app

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует.')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Создаём профиль по умолчанию
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Неверные данные для входа.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    food_entries = FoodEntry.query.filter_by(user_id=current_user.id).order_by(FoodEntry.date.desc()).limit(5).all()
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).limit(5).all()
    return render_template('dashboard.html', profile=profile, food_entries=food_entries, workouts=workouts)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        profile.weight = float(request.form['weight'])
        profile.height = float(request.form['height'])
        profile.target_weight = float(request.form['target_weight'])
        db.session.commit()
        flash('Профиль обновлён!')
    return render_template('profile.html', profile=profile)

@app.route('/add_food', methods=['POST'])
@login_required
def add_food():
    food_name = request.form['food_name']
    calories = int(request.form['calories'])
    food = FoodEntry(user_id=current_user.id, food_name=food_name, calories=calories)
    db.session.add(food)
    db.session.commit()
    flash('Запись о питании добавлена!')
    return redirect(url_for('dashboard'))

@app.route('/add_workout', methods=['POST'])
@login_required
def add_workout():
    exercise_name = request.form['exercise_name']
    weight = float(request.form['weight']) if request.form['weight'] else None
    reps = int(request.form['reps']) if request.form['reps'] else None
    workout = Workout(user_id=current_user.id, exercise_name=exercise_name, weight=weight, reps=reps)
    db.session.add(workout)
    db.session.commit()
    flash('Тренировка добавлена!')
    return redirect(url_for('dashboard'))
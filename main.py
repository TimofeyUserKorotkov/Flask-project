import os
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from data import db_session
# from data.news import News
from data.users import User
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from forms.login import LoginForm
# from forms.new import NewsForm
from forms.user import RegisterForm
from data.recipes import Recipes
from forms.recipe import RecipesForm
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678900987654321'
app.config['UPLOADED_IMAGES_FOLDER'] = 'static'
login_manager = LoginManager()
login_manager.init_app(app)

def main():
    db_session.global_init("db/blogs.sqlite")
    app.run()


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        recipes = db_sess.query(Recipes).filter((Recipes.user == current_user) | (Recipes.is_private != True))
    else:
        recipes = db_sess.query(Recipes).filter(Recipes.is_private != True)
    return render_template("index.html", recipes=recipes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            # about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile',  methods=['GET'])
@login_required
def profile():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        recipes = db_sess.query(Recipes).filter(Recipes.user == current_user)
    else:
        redirect('/')
    return render_template("profile.html", recipes=recipes)


@app.route('/recipes',  methods=['GET', 'POST'])
@login_required
def add_recipes():
    form = RecipesForm()
    # if form.validate_on_submit():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        recipes = Recipes()
        recipes.title = form.title.data
        recipes.content = form.content.data
        recipes.category = form.category.data
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
        if file:
            filename = secure_filename(file.filename)
            src = '../' + '/'.join([app.config['UPLOADED_IMAGES_FOLDER'], filename])
            print(src)
            recipes.image = src
            print(recipes.image)
            file.save(os.path.join(app.config['UPLOADED_IMAGES_FOLDER'], filename))
        recipes.is_private = form.is_private.data
        current_user.recipes.append(recipes)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('recipes.html', title='Добавление рецепта', form=form)


@app.route('/view/<int:id>', methods=['GET'])
def view_recipe(id):
    if request.method == "GET":
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipes).filter(Recipes.id == id
                                          ).first()
        if not recipe:
            abort(404)
    return render_template('view_recipe.html',
                           title='Просмотр рецепта',
                           recipe=recipe)


@app.route('/recipes/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(id):
    form = RecipesForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipes).filter(Recipes.id == id,
                                          Recipes.user == current_user
                                          ).first()
        if recipe:
            form.title.data = recipe.title
            form.content.data = recipe.content
            form.category.data = recipe.category
            form.is_private.data = recipe.is_private
        else:
            abort(404)
    if request.method == 'POST':
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipes).filter(Recipes.id == id,
                                          Recipes.user == current_user
                                          ).first()
        if recipe:
            recipe.title = form.title.data
            recipe.content = form.content.data
            recipe.category = form.category.data
            if 'file' not in request.files:
                flash('No file part')
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
            if file:
                filename = secure_filename(file.filename)
                src = '../' + '/'.join([app.config['UPLOADED_IMAGES_FOLDER'], filename])
                print(src)
                recipe.image = src
                print(recipe.image)
                file.save(os.path.join(app.config['UPLOADED_IMAGES_FOLDER'], filename))
            recipe.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('recipes.html',
                           title='Редактирование рецепта',
                           form=form)


@app.route('/recipes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def recipe_delete(id):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipes).filter(Recipes.id == id,
                                      Recipes.user == current_user
                                      ).first()
    if recipe:
        db_sess.delete(recipe)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/profile')


@app.route("/breakfast", methods=['GET'])
def breakfast():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        recipes = db_sess.query(Recipes).filter(
            ((Recipes.user == current_user) | (Recipes.is_private != True)), Recipes.category == 'Завтрак')
    else:
        recipes = db_sess.query(Recipes).filter(Recipes.is_private != True, Recipes.category == 'Завтрак')
    return render_template("index.html", recipes=recipes)


@app.route("/lunch", methods=['GET'])
def lunch():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        recipes = db_sess.query(Recipes).filter(
            ((Recipes.user == current_user) | (Recipes.is_private != True)), Recipes.category == 'Обед')
    else:
        recipes = db_sess.query(Recipes).filter(Recipes.is_private != True, Recipes.category == 'Обед')
    return render_template("index.html", recipes=recipes)


@app.route("/dinner", methods=['GET'])
def dinner():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        recipes = db_sess.query(Recipes).filter(
            ((Recipes.user == current_user) | (Recipes.is_private != True)), Recipes.category == 'Ужин')
    else:
        recipes = db_sess.query(Recipes).filter(Recipes.is_private != True, Recipes.category == 'Ужин')
    return render_template("index.html", recipes=recipes)


@app.route("/snack", methods=['GET'])
def snack():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        recipes = db_sess.query(Recipes).filter(
            ((Recipes.user == current_user) | (Recipes.is_private != True)), Recipes.category == 'Перекус')
    else:
        recipes = db_sess.query(Recipes).filter(Recipes.is_private != True, Recipes.category == 'Перекус')
    return render_template("index.html", recipes=recipes)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
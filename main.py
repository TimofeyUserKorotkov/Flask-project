from flask import Flask, abort, redirect, render_template, request
from data import db_session
from data.news import News
from data.users import User
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from forms.login import LoginForm
from forms.new import NewsForm
from forms.user import RegisterForm
from data.recipes import Recipes
from forms.recipe import RecipesForm

# from flask_uploads import UploadSet, IMAGES, configure_uploads


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678900987654321'
# app.config['UPLOADED_IMAGES_DEST'] = 'uploads'
login_manager = LoginManager()
login_manager.init_app(app)

# imgs = UploadSet('imgs', IMAGES)
# configure_uploads(app, imgs)


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
    return redirect("/")


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
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# def get_file(filename):
    # return send_from_directory()

@app.route('/recipes',  methods=['GET', 'POST'])
@login_required
def add_recipes():
    form = RecipesForm()
    if form.validate_on_submit():
    # if request.method == 'POST':
        db_sess = db_session.create_session()
        recipes = Recipes()
        recipes.title = form.title.data
        recipes.image = form.image.data
        
        file = request.files['file']
        recipes.image_data = file.read()

        print(f'OK -------------------> {recipes.image_data}')
        recipes.content = form.content.data
        recipes.is_private = form.is_private.data
        current_user.recipes.append(recipes)
        db_sess.merge(current_user)
        db_sess.commit()
        # return redirect('/')
        return f'{recipes.title, recipes.content, recipes.is_private, recipes.image_data}'
    return render_template('recipes.html', title='Добавление рецепта', form=form)

# # @app.route('/recipes',  methods=['GET', 'POST'])
# @login_required
# def add_recipes():
#     form = RecipesForm()
#     # if request.method == 'post':
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         recipes = Recipes()
#         recipes.title = form.title.data
#         recipes.image = form.image.data
#         print(form.image, form.image.data, form.image)
        
#         # file = request.files['file']
#         # recipes.image_data = file.read()

#         print(f'OK -------------------> {recipes.image_data}')
#         # recipes.image_data = 
#         # recipes.image_url = url_for(
#         #     'send_from_directory', directory=app.config['UPLOADED_IMAGES_DEST'], path=recipes.image)
#         recipes.content = form.content.data
#         recipes.is_private = form.is_private.data
#         current_user.recipes.append(recipes)
#         db_sess.merge(current_user)
#         db_sess.commit()
#         return redirect('/')
#     return render_template('recipes.html', title='Добавление рецепта', form=form)








# @app.route('/',  methods=['GET', 'POST'])
# @login_required
# def add_recipes():
#     form = RecipesForm()
#     if request.method == 'POST':
#     # if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         recipes = Recipes()
#         # recipes.title = form.title.data
#         # recipes.image = form.image.data
#         # print(form.image, form.image.data, form.image)
        
#         file = request.files['file']
#         recipes.image_data = file.read()

#         print(f'OK -------------------> {recipes.image_data}')
#         # # recipes.image_data = 
#         # # recipes.image_url = url_for(
#         # #     'send_from_directory', directory=app.config['UPLOADED_IMAGES_DEST'], path=recipes.image)
#         # recipes.content = form.content.data
#         # recipes.is_private = form.is_private.data
#         # current_user.recipes.append(recipes)
#         # db_sess.merge(current_user)
#         # db_sess.commit()
#         # return redirect('/')
#         return f'=================={recipes.image_data}'
#     return render_template('recipes.html', title='Добавление рецепта', form=form)








@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости', 
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
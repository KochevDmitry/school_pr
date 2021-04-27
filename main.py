import base64
from flask import Flask, render_template, redirect, request, abort

from School_and_Yandex_project.data.castings import Casting
from School_and_Yandex_project.forms.edit_person import EditPerson
from School_and_Yandex_project.forms.loginform import LoginForm
from School_and_Yandex_project.forms.news import NewsForm
from School_and_Yandex_project.forms.search_person import SearchPerson
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from School_and_Yandex_project.data.users import User
from School_and_Yandex_project.forms.user import RegisterForm
from School_and_Yandex_project.data.news import News

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

def main():
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/all_castings')
def all_castings():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        casts = db_sess.query(Casting).filter(
            (Casting.user == current_user))
        if casts.first() == None:
            casts = None
    else:
        casts = None
    return render_template("all_castings.html", news=casts)

@app.route('/casting/<int:id>/<sort>', methods=['GET', 'POST'])
def casting(id, sort):
    db_sess = db_session.create_session()
    form = SearchPerson()
    if current_user.is_authenticated:
        if sort == 'none':
            news = db_sess.query(News).filter(
                News.user == current_user, News.cast_id == id)
        elif sort == 'main':
            news = db_sess.query(News).filter(
                News.user == current_user, News.cast_id == id, News.is_private == True)
        elif sort == 'name':
            news = db_sess.query(News).filter(
                News.user == current_user, News.cast_id == id).order_by(News.name_person)
        elif sort == 'age':
            news = db_sess.query(News).filter(
                News.user == current_user, News.cast_id == id).order_by(News.age)
        cast = db_sess.query(Casting).filter(
            Casting.id == id).first()

        if form.is_submitted():
            info = form.search_info.data
            print(info)
            news = db_sess.query(News).filter(
                News.user == current_user, News.name_person.like('%{}%'.format(info)))
    else:
        news = None
        cast = None
    return render_template("casting.html", news=news, cast=cast, sort=sort, form=form)

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

@app.route('/register', methods=['GET', 'POST'])
def register():
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

@app.route('/logout')
#@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/add_casting', methods=['GET', 'POST'])
@login_required
def add_casting():
    form = NewsForm()
    if form.validate_on_submit():
        if form.content.data == '':
            return render_template('add_casting.html', title='Добавление новости',
                                   form=form)
        db_sess = db_session.create_session()
        casting = Casting()
        casting.name_cast = form.name.data
        casting.user_id = current_user.id
        db_sess.add(casting)
        db_sess.commit()
        cast = list(db_sess.query(Casting).filter(
            Casting.user_id == current_user.id))[-1]
        print(cast.name_cast, cast.user_id)
        text = form.content.data
        grand_array = make(text, form.name.data)
        if grand_array == None:
            return render_template('add_casting.html', title='Добавление новости',
                                   form=form)
        for array in grand_array:
            db_sess = db_session.create_session()
            news = News()
            news.cast_id = cast.id
            print(array)
            if array[4] == 'ОСНОВНОЙ СОСТАВ':
                news.is_private = True
                del array[4]
            else:
                news.is_private = False
            print(news.is_private, array[4][:-1])
            news.name_person = array[1]
            news.age = str(array[2])
            news.city = array[3]
            news.networks = array[4]
            news.photo = None
            news.content= array[5]
            current_user.news.append(news)
            db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_casting.html', title='Добавление новости',
                           form=form)

def make(text, name):#создать кастинг или добавить человека
    grand_list = []
    if text.count('\n') < 3 or text.count('$') < 2:#проверяем правильность текста
        abort(404)
        return None
    name_cast = name
    a = []
    allname = text.split('%')#делим на разных людей
    print(allname)
    for i in range(len(allname)):
        d = allname[i].split('$')#делим людей на до соц.сетей/соц.сети/информация
        a.append(d)
    print(a)
    for i in range(len(a)):
        b = a[i][0].split('\r\n')  # оставляем в "в" все что до соц.сетей
        del a[i][0]
        j = 0
        while b[j] == '':  # убираем лишние переводы строки в начале карточки
            del b[j]
        print(b)
        del b[-1]
        b.extend(a[i])  # добавляем в "в" всю инфу о пользователе
        print(b)
        surname = b[0].split()  # разбираемся с номером,именем,возрастом
        del b[0]
        name = ' '.join(surname[1:3])
        del surname[1:3]
        surname.insert(1, name)
        surname[1] = surname[1][:-1]  # закончили разбираться, сделав из одного элем три нужных
        surname.extend(b)
        b = surname[:]
        print(b)
        grand_list.append(b)
    print(grand_list)
    return grand_list

@app.route('/add_several_person/<int:cast_id>', methods=['GET', 'POST'])
@login_required
def add_several_person(cast_id):
    form = NewsForm()
    db_sess = db_session.create_session()
    cast = db_sess.query(Casting).filter(Casting.id == cast_id).first()
    print(cast)
    print(cast.name_cast)
    if form.is_submitted():
        print(cast.name_cast, cast.user_id)
        text = form.content.data
        grand_array = make(text, form.name.data)
        for array in grand_array:
            db_sess = db_session.create_session()
            news = News()
            news.cast_id = cast.id
            print(array)
            if array[4] == 'ОСНОВНОЙ СОСТАВ':
                news.is_private = True
                del array[4]
            else:
                news.is_private = False
            print(news.is_private, array[4][:-1])
            news.name_person = array[1]
            news.age = str(array[2])
            news.city = array[3]
            news.networks = array[4]
            news.photo = None
            news.content= array[5]
            current_user.news.append(news)
            db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/casting/{}/none'.format(cast_id))
    return render_template('add_several_person.html', title='Добавление новости',
                           form=form, cast = cast)

@app.route('/edit_person/<int:cast_id>/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(cast_id, id):
    form = EditPerson()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.name.data = news.name_person
            form.age.data = news.age
            form.city.data = news.city
            form.networks.data = news.networks
            form.is_main.data = news.is_private
            form.content.data = news.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.name_person = form.name.data
            news.age = form.age.data
            news.city = form.city.data
            news.networks = form.networks.data
            news.is_private = form.is_main.data
            news.content = form.content.data
            f=form.photo.data
            with open('static/img/{}.png'.format(id), 'wb') as fil:
                fil.write(f.read())
            #news.photo = base64.b64encode(f.read()[2:-1])
            db_sess.commit()
            return redirect('/casting/{}/none'.format(cast_id))
        else:
            abort(404)
    return render_template('edit_person.html',
                           title='Редактирование новости',
                           form=form
                           )

@app.route('/add_person/<int:cast_id>', methods=['GET', 'POST'])
@login_required
def add_person(cast_id):
    form = EditPerson()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        if news:
            news.name_person = form.name.data
            news.age = form.age.data
            news.city = form.city.data
            news.networks = form.networks.data
            news.is_private = form.is_main.data
            news.content = form.content.data
            news.cast_id = cast_id
            news_test = db_sess.query(News).all()
            print(news_test[-1].id)
            f=form.photo.data
            with open('static/img/{}.png'.format(news_test[-1].id + 1), 'wb') as fil:
                fil.write(f.read())
            #news.photo = base64.b64encode(f.read()[2:-1])
            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/casting/{}/none'.format(cast_id))
        else:
            abort(404)
    return render_template('edit_person.html',
                           title='Редактирование новости',
                           form=form
                           )

@app.route('/news_delete/<int:cast_id>/<int:id>/<sort>', methods=['GET', 'POST'])
@login_required
def news_delete(id, cast_id, sort):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/casting/{}/{}'.format(cast_id, sort))

@app.route('/cast_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def cast_delete(id):
    db_sess = db_session.create_session()
    cast = db_sess.query(Casting).filter(Casting.id == id).first()
    news = db_sess.query(News).filter(News.cast_id == id,
                                      News.user == current_user
                                      ).all()
    if cast:
        for x in news:
            db_sess.delete(x)
        db_sess.delete(cast)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/all_castings')

@app.route('/test')
#@login_required
def test():
    return render_template('test.html')



if __name__ == '__main__':
    main()
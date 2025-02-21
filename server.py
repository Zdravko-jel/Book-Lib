import base64
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, TEXT, LargeBinary, Date, ForeignKey, Boolean
from datetime import datetime


app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booklib.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'booklibbest'

db = SQLAlchemy()
bcrypt = Bcrypt(app)


def get_image_as_base64(image):
    if image:
        return base64.b64encode(image).decode('utf-8')
    return None


feeling = {
    1: "BEST BOOK I'VE EVER RED",
    2: "READ BETTER ONES",
    3: "MUST READ",
    4: "WISH I HADN'T READ THIS",
    5: "I DID NOT LIKE IT AT ALL",
    6: "THIS BOOK MADE ME CRY",
    7: "I COULD NOT FINISH",
    8: "SO BORING",
}


class User(db.Model):  # Inherit from Base
    id = Column(Integer, primary_key=True)
    first_name = Column(TEXT, nullable=False)
    last_name = Column(TEXT, nullable=False)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)
    email = Column(TEXT, unique=True, nullable=False)
    profile_pic = Column(LargeBinary)

    def __init__(self, first_name, last_name, username, password, email, profile_pic):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.email = email
        self.profile_pic = profile_pic

    def serialize(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email
        }


class Book(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(TEXT, nullable=False, unique=True)
    author = Column(TEXT, nullable=False)
    genre = Column(TEXT, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    pages = Column(Integer, nullable=False)
    format = Column(TEXT, nullable=False)
    stars = Column(Integer, nullable=True, default=1)
    feeling = Column(Integer, nullable=False)
    summary = Column(TEXT, nullable=False)
    fav_quote = Column(TEXT, nullable=False)
    recommend = Column(Boolean, nullable=False)
    thoughts_impressions = Column(TEXT, nullable=True)
    book_cover = Column(LargeBinary)
    spice = Column(Integer, nullable=True, default=1)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __init__(self, title, author, genre, start_date, end_date, pages, format_curr, feeling_curr, summary,
                 fav_quote, recommend, book_cover, user_id, stars=None, thoughts_impressions=None, spice=None):
        self.title = title
        self.author = author
        self.genre = genre
        self.start_date = start_date
        self.end_date = end_date
        self.pages = pages
        self.format = format_curr
        self.stars = stars
        self.feeling = feeling_curr
        self.summary = summary
        self.fav_quote = fav_quote
        self.recommend = recommend
        self.thoughts_impressions = thoughts_impressions
        self.book_cover = book_cover
        self.spice = spice
        self.user_id = user_id


db.init_app(app)


@app.route("/")
def home():
    if session.get("user_id", None):
        user_id = session["user_id"]
        user: User = User.query.filter_by(id=user_id).first()
        profile_pic = get_image_as_base64(user.profile_pic)
        books: list = Book.query.filter_by(user_id=user.id).all()
        if not books:
            books = []
        else:
            books = [(book, get_image_as_base64(book.book_cover)) for book in books]
        return render_template("home.html", user=user, profile_pic=profile_pic, books=books)
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user: User = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", 'success')
            return redirect(url_for("home"))
        else:
            flash("Login failed. Check your email and/or password.", 'danger')
            return redirect(url_for("login"))
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        profile_pic = request.files['profile_pic'].read()

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=hashed_password,
            email=email,
            profile_pic=profile_pic
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Register successful! Now log in!", 'success')
        return redirect(url_for("login"))
    else:
        return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if session.get("user_id", None):
        user_id = session["user_id"]
        user: User = User.query.filter_by(id=user_id).first()
        if request.method == "POST":
            old_password = request.form.get("old_password")
            if user and bcrypt.check_password_hash(user.password, old_password):
                user.first_name = request.form.get("first_name")
                user.last_name = request.form.get("last_name")
                user.username = request.form.get("username")
                user.email = request.form.get("email")
                user.password = user.password if not request.form.get("new_password", None) \
                    else bcrypt.generate_password_hash(request.form.get("new_password")).decode("utf-8")
                user.profile_pic = user.profile_pic if not request.files.get("profile_pic", None) \
                    else request.files["profile_pic"].read()
                db.session.commit()
                return redirect(url_for('logout'))
            else:
                flash("To change something you need to provide your password in section 'Old Password'.", 'danger')
                return redirect(url_for("settings"))
        else:
            profile_pic = get_image_as_base64(user.profile_pic)
            return render_template("settings.html", user=user, profile_pic=profile_pic)


@app.route("/new_book", methods=["GET", "POST"])
def new_book():
    if session.get("user_id", None):
        user_id = session["user_id"]
        user: User = User.query.filter_by(id=user_id).first()
        profile_pic = get_image_as_base64(user.profile_pic)

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        pages = int(request.form.get("pages"))
        start_date = datetime.strptime(request.form.get("start_date"), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get("end_date"), '%Y-%m-%d').date()
        formats = request.form.get("format")
        stars = int(request.form.get("star_rating", 1))
        spices = int(request.form.get("spice_rating", 1))
        summary = request.form.get("summary")
        fav_quote = request.form.get("fav_quote")
        thoughts = request.form.get("thoughts", None)
        recommend = True if request.form.get("recommend") == "true" else False
        feelings = feeling[int(request.form.get("feeling"))]
        file = request.files["book_cover"].read()
        user_id = int(session["user_id"])

        new_book: Book = Book(
            title=title,
            author=author,
            genre=genre,
            pages=pages,
            start_date=start_date,
            end_date=end_date,
            format_curr=formats,
            stars=stars,
            spice=spices,
            summary=summary,
            fav_quote=fav_quote,
            thoughts_impressions=thoughts,
            recommend=recommend,
            book_cover=file,
            user_id=user_id,
            feeling_curr=feelings
        )
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))
    else:
        return render_template("edit_book.html", type="new", profile_pic=profile_pic, user=user)


@app.route("/view_book/<int:idx>")
def view_book(idx):
    if session.get("user_id", None):
        user_id = session["user_id"]
        user: User = User.query.filter_by(id=user_id).first()
        profile_pic = get_image_as_base64(user.profile_pic)
        book: Book = Book.query.filter_by(id=idx, user_id=user_id).first()
        cover = get_image_as_base64(book.book_cover)
        feelings = book.feeling
        start_date = book.start_date.strftime('%Y-%m-%d')
        end_date = book.end_date.strftime('%Y-%m-%d')
        return render_template("read_book.html", user=user, profile_pic=profile_pic, book=book,
                               cover=cover, start_date=start_date, end_date=end_date, feeling=feelings)


@app.route("/edit_book/<int:idx>", methods=["GET", "POST"])
def edit_book(idx):
    if session.get("user_id", None):
        user_id = session["user_id"]
        user: User = User.query.filter_by(id=user_id).first()
        profile_pic = get_image_as_base64(user.profile_pic)

    if request.method == "POST":
        user_id = session.get("user_id", None)
        book: Book = Book.query.filter_by(id=idx, user_id=user_id).first()
        book.title = request.form.get("title")
        book.author = request.form.get("author")
        book.genre = request.form.get("genre")
        book.pages = int(request.form.get("pages"))
        book.start_date = datetime.strptime(request.form.get("start_date"), '%Y-%m-%d').date()
        book.end_date = datetime.strptime(request.form.get("end_date"), '%Y-%m-%d').date()
        book.format = request.form.get("format")
        book.stars = int(request.form.get("star_rating", 1))
        book.spice = int(request.form.get("spice_rating", 1))
        book.summary = request.form.get("summary")
        book.fav_quote = request.form.get("fav_quote")
        book.thoughts_impressions = request.form.get("thoughts", None)
        book.recommend = True if request.form.get("recommend") == "true" else False
        book.feeling = feeling[int(request.form.get("feeling"))]
        book.book_cover = book.book_cover if not request.files.get("book_cover", None) \
            else request.files["book_cover"].read()
        book.user_id = int(session["user_id"])
        db.session.commit()
        return redirect(url_for('home'))
    else:
        user_id = session.get("user_id", None)
        book: Book = Book.query.filter_by(id=idx, user_id=user_id).first()
        if user_id and book:
            return render_template("edit_book.html", type="edit", profile_pic=profile_pic, user=user,
                                   book=book, cover=get_image_as_base64(book.book_cover),
                                   start_date=book.start_date.strftime('%Y-%m-%d'),
                                   end_date=book.end_date.strftime('%Y-%m-%d'))
        return redirect(url_for("home"))


@app.route("/delete/<int:idx>")
def delete_book(idx):
    if session.get("user_id", None):
        user_id = session["user_id"]
        book: Book = Book.query.filter_by(id=idx, user_id=user_id).first()
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/logout")
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash("You have been logged out.", "info")  # Flash a message
    return redirect(url_for('login'))  # Redirect to login page


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

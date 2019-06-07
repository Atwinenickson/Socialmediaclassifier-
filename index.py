from collections import Counter
import matplotlib.pyplot as plt
from update import update_model
import pandas as pd
from werkzeug.utils import secure_filename
from flask import flash
from modell import final_transformer
import pickle
import pickle as pi
from flask import session
import sqlite3 as sql
import sqlite3
from flask_mail import Mail
from flask_security import (
    Security, SQLAlchemyUserDatastore, UserMixin)
from change_email import change_email, confirm_change_email
from send_mail import send_mail
import os
from flask import url_for, redirect
from wtforms import form, fields
import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose

from wtforms import StringField
from wtforms import validators
from wtforms.validators import InputRequired, Email, regexp
import json
import datetime
import time
import io
import csv
from flask import Flask
from flask import render_template
from flask import stream_with_context
from flask import Response
from flask import request
from flask import jsonify
from werkzeug.datastructures import Headers
from validation import get_post_id
from validation import get_page_name
from get_fb_comments_from_fb import scrapeFacebookPageFeedComments
from get_fb_comments_from_fb import request_once
import config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "hamza  ''\\"


@app.route('/')
def login_page():
    return render_template('loginpage.html')


@app.route('/user_login', methods=['GET', 'POST'])
def login1(dbUser=None, dbPass=None, dbusertype=None):
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = sql.connect("sample_db.sqlite")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select username,password,user_type from user")

        rows = cur.fetchall();
        for row in rows:
            dbUser = row["username"]
            dbPass = row["password"]
            dbusertype = row["user_type"]

            if username == dbUser and check_password_hash(dbPass, request.form['password']):
                if dbusertype is None:
                    return redirect(url_for('main'))
                elif dbusertype == 'user':
                    return redirect(url_for('main'))
                elif dbusertype == 'admin':
                    return redirect(url_for('admin_panel'))
                else:
                    error = 'invalid user type, uername or password!!'
                    return render_template('userlogin.html', error=error)

            elif username == dbUser and password == dbPass:
                if dbusertype is None:
                    return redirect(url_for('main'))
                elif dbusertype == 'user':
                    return redirect(url_for('main'))
                elif dbusertype == 'admin':
                    return redirect(url_for('admin_panel'))
                else:
                    error = 'invalid user type, uername or password!!'
                    return render_template('userlogin.html', error=error)

    return render_template('userlogin.html', error=error)


# this
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    msg = None
    if request.method == 'POST':
        try:

            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            tell = request.form['no']
            username = request.form['username']
            # passs = request.form['pass']
            hash_password = generate_password_hash(request.form['pass'], method='sha256')

            with sql.connect("sample_db.sqlite") as con:
                cur = con.cursor()

                cur.execute(
                    "INSERT INTO user (fname,lname,email,tellnumber,username,password) VALUES(?, ?, ?, ?, ?, ?)",
                    (fname, lname, email, tell, username, hash_password))

                con.commit()
                msg = "User added successfully"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:

            return render_template('adminlogin.html', msg=msg)
            con.close()
    else:

        return render_template('adminlogin.html')


# this

cur_dir = os.path.dirname(__file__)

clf = pickle.load(open(os.path.join(cur_dir, 'finall_modell.sav'), 'rb'))

db = os.path.join(cur_dir, 'sample_db.sqlite')


def train(df, y):
    X = final_transformer.transform(df)
    clf.fit(X, y, sample_weight=None)


def sqlite_entry(path, Post, Comment, y):
    conn = sqlite3.connect('sample_db.sqlite')
    c = conn.cursor()
    c.execute("INSERT INTO sent (Post, Comment, Sentiment)" \
              " VALUES (?, ?, ?)", (Post, Comment, y))
    conn.commit()
    conn.close()


@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('main.html')

    if request.method == 'POST':
        Post = request.form['Post']
        Comment = request.form['Comment']

        df = pd.DataFrame([[Post, Comment]], columns=['Post', 'Comment'], dtype=str, index=['input'])

        vec = final_transformer.transform(df)
        my_prediction = clf.predict(vec)
    return render_template('main.html', original_input={'Post': Post, 'Comment': Comment}, prediction=my_prediction,
                           post=Post, comment=Comment)


@app.route('/thanks', methods=['POST'])
def feedback():
    feedback = request.form['feedback_button']
    Post = request.form['Post']
    Comment = request.form['Comment']
    Sentiment = request.form['prediction']

    df = pd.DataFrame([[Post, Comment, Sentiment]], columns=['Post', 'Comment', 'Sentiment'], dtype=str)
    y = df['Sentiment']
    # print(y)
    df = df.drop('Sentiment', axis=1)
    prediction = request.form['prediction']
    '''
    prediction = request.form['prediction']

    inv_label = {'negative': 'negative', 'positive': 'positive', 'neutral':'neutral'}
    y = inv_label[prediction]
    '''
    if feedback == 'Incorrect':
        if request.method == 'POST':
            result = request.form
            y = result
    elif feedback == 'Correct':
        y = prediction
    # train(df, y)
    sqlite_entry(db, Post, Comment, y)
    return render_template('main.html')


image_folder = os.path.join('static', 'image')
ALLOWED_EXTENSIONS = set(['CSV', 'csv'])

# app.config['UPLOAD_FOLDER'] = image_folder

# UPLOAD_FOLDER = 'C:/Users/hamza/PycharmProjects/exercise/try'
# ALLOWED_EXTENSIONS = set(['CSV', 'csv'])


'''
@app.route('/adminlogin', methods=['GET', 'POST'])
def login(dbUser=None,dbPass=None):
    error = None


    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password']  = request.form['password']


        con = sql.connect("database.db")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select * from admin ")

        rows = cur.fetchall();
        for row in rows:
            dbUser = row["username"]
            dbPass = row["password"]
        if session['username']==dbUser and session['password']==dbPass:
            return redirect(url_for('admin_panel'))

        else:
            error = 'Invalid Credentials. Please try again.'


    return render_template('adminlogin.html', error=error)'''


@app.route('/admin_panel')
def admin_panel():
    return render_template('admin_panel.html')


@app.route('/user_logout')
def user_logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login1'))


@app.route('/admin_logout')
def admin_logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login1'))

UPLOAD_FOLDER = 'C:/Users/atwiine/PycharmProjects/finalyearproject'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



UPLOAD_FOLDER = 'C:/Users/atwiine/PycharmProjects/finalyearproject'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin_upload', methods=['GET', 'POST'])
def admin_upload(filename=None):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            message = None

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            missing_values = ["no info", ".", "n/a", "na", "--", "N/A", "NA", "??", "?"]
            df = pd.read_csv(file_path, encoding='latin', sep=',', delimiter=None, header=0, index_col=None,
                             squeeze=False, engine='python', usecols=range(0, 3), na_values=missing_values)

            df['Post'].fillna(method="ffill", inplace=True)
            df['Comment'].fillna(method="ffill", inplace=True)
            df['Sentiment'].fillna(method="ffill", inplace=True)

            y = df['Sentiment']
            # print(y)
            df = df.drop('Sentiment', axis=1)
            # print(df)
            X_train = final_transformer.transform(df)
            log_model = clf.fit(X_train, y, sample_weight=None)
            # Save the model
            filename = 'finall_modell.sav'
            pi.dump(log_model, open(filename, 'wb'))
            if filename:
                message = 'model updated successfully!!'
                return render_template('adminupdate.html', message=message)
            else:
                message = 'model not updated!!'
                return render_template('adminupdate.html', message=message)
        else:
            message = 'file not allowed,choose a csv file. model not updated'
            return render_template('adminupdate.html', message=message)
    return render_template('adminupdate.html', filename=filename)


plt.style.use('ggplot')

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


@app.route('/graph', methods=['GET', 'POST'])
def upload_file(filename=None, column=None, data=None, my_prediction=None, df=None):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            missing_values = ["no info", ".", "n/a", "na", "--", "N/A", "NA", "??", "?"]
            df = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',', delimiter=None, header=0, index_col=None,
                             squeeze=False, engine='python', usecols=range(0, 3), na_values=missing_values)
            df.columns = ['Post', 'Comment', 'Sentiment']
            df['Post'].fillna(method="ffill", inplace=True)
            df['Comment'].fillna(method="ffill", inplace=True)
            df['Sentiment'].fillna(method="ffill", inplace=True)

            vec = final_transformer.transform(df)
            my_prediction = clf.predict(vec)
            df['Sentiment'] = my_prediction
            df['Sentiment'].value_counts().plot(kind='bar', title='Sentiment of classification')
            plt.savefig("image.png")
            line_labels, line_values = creategraph(df['Sentiment'])
            desc = df.describe(include='all')
            return render_template('line_chart.html', title='line graph showing Sentiment Analysis',
                                   max=1000, labels=line_labels, values=line_values, df=df.to_html(),
                                   stat=desc.to_html(),
                                   csv=df.to_csv())

    return render_template('upload.html', filename=filename, data=data, column=column, predict=my_prediction, df=df)


@app.route('/graph1', methods=['GET', 'POST'])
def upload_file1(filename=None, column=None, data=None, my_prediction=None, df=None):
    UPLOAD_FOLDER = 'C:/Users/atwiine/PycharmProjects/finalyearproject'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            missing_values = ["no info", ".", "n/a", "na", "--", "N/A", "NA", "??", "?"]
            df = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',', delimiter=None, header=0, index_col=None,
                             squeeze=False, engine='python', usecols=range(0, 3), na_values=missing_values)
            df.columns = ['Post', 'Comment', 'Sentiment']
            df['Post'].fillna(method="ffill", inplace=True)
            df['Comment'].fillna(method="ffill", inplace=True)
            df['Sentiment'].fillna(method="ffill", inplace=True)
            vec = final_transformer.transform(df)
            my_prediction = clf.predict(vec)
            df['Sentiment'] = my_prediction
            df['Sentiment'].value_counts().plot(kind='bar', title='Sentiment of classification')
            plt.savefig("image.png")
            line_labels, line_values = creategraph(df['Sentiment'])
            desc = df.describe(include='all')
            return render_template('bar_chart.html', title='Bar graph showing Sentiment Analysis',
                                   max=1000, labels=line_labels, values=line_values, df=df.to_html(),
                                   stat=desc.to_html(),
                                   csv=df.to_csv())

    return render_template('upload1.html', filename=filename, data=data, column=column, predict=my_prediction, df=df)


@app.route('/bar')
def creategraph(prediction):
    counter = Counter(prediction)
    labels = counter.keys()
    values = counter.values()
    bar_labels = labels
    bar_values = values

    return bar_labels, bar_values


# add user

@app.route("/adduser")
def add():
    return render_template("add_user.html")


@app.route("/savedetails", methods=["POST", "GET"])
def saveDetails():
    msg = None
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            tell = request.form['no']
            username = request.form['username']
            # passs = request.form['pass']
            hash_password = generate_password_hash(request.form['pass'], method='sha256')

            user_type = request.form['user']

            with sql.connect("sample_db.sqlite") as con:
                cur = con.cursor()

                cur.execute(
                    "INSERT INTO user (fname,lname,email,tellnumber,username,password,user_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (fname, lname, email, tell, username, hash_password, user_type))

                con.commit()
                msg = "User added successfully"
        except:
            con.rollback()
            msg = "User not added!, use the right credentials. "

        finally:
            return render_template('add_user.html', msg=msg)
            con.close()


    else:
        return render_template('add_user.html')


@app.route("/view")
def view():
    con = sqlite3.connect("sample_db.sqlite")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from user")
    rows = cur.fetchall()
    return render_template("view.html", rows=rows)


@app.route("/delete")
def delete():
    return render_template("delete.html")


@app.route("/deleteuser", methods=["POST"])
def deleteuser():
    msg = None
    id = request.form["id"]
    with sqlite3.connect("sample_db.sqlite") as con:
        try:
            cur = con.cursor()
            cur.execute("delete  from user where id = ?", id)
            msg = "user successfully deleted"
        except:
            msg = "can't be deleted"
        finally:
            return render_template("delete.html", msg=msg)


# end add user


'''
flask admin
'''

# Create Flask application
# app = Flask(__name__)

# Create dummy secrey key so we can use sessions
# app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Create user model.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, )
    fname = db.Column(db.String, NOT_NULL=True)
    lname = db.Column(db.String, NOT_NULL=True)
    email = db.Column(db.String(50), NOT_NULL=True, unique=True)
    tellnumber = db.Column(db.Integer, NOT_NULL=True)
    username = db.Column(db.String, not_null=True, unique=True)
    password = db.Column(db.String)
    user_type = db.Column(db.String(225))

    # Flask-Login integration
    # NOTE: is_authenticated, is_active, and is_anonymous
    # are methods in Flask-Login < 0.3.0
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    username = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(username=self.username.data).first()


class RegistrationForm(form.Form):
    firstname = StringField(validators=[validators.DataRequired("Please enter your  first name.")])
    lastname = StringField(validators=[validators.DataRequired("Please enter your last name."),
                                       validators.Length(max=255)])

    # email = fields.StringField()
    email = StringField("Email", validators=[InputRequired("Please enter your email address."),
                                             Email("This field requires a valid email address"),
                                             validators.Length(min=6, max=225),
                                             regexp("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")])
    username = fields.StringField(validators=[validators.DataRequired("Please enter your  username.")])

    password = fields.PasswordField(validators=[validators.DataRequired("Enter a valid password"),
                                                validators.Length(min=6, max=225)])


    def validate_login(self, field):
        if db.session.query(User).filter_by(username=self.username.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return True


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Flask views
@app.route('/')
def index():
    return render_template('index.html')


# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, 'Social Media Post Sentiment Admin panel', index_view=MyAdminIndexView(),
                    base_template='my_master.html')

# Add view
admin.add_view(MyModelView(User, db.session))


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()
    # passwords are hashed, to use plaintext passwords instead:
    # test_user = User(login="test", password="test")
    test_user = User(username="test", password=generate_password_hash("test"))
    db.session.add(test_user)

    first_names = [
        'Nickson', 'Hamza', 'Henry', 'Happiness', 'Robert', 'John'
    ]
    last_names = [
        'Atwine', 'Mugabo', 'Mulindwa', 'Turyahiirwa', 'Musinguzi', 'Kayise'
    ]

    for i in range(len(first_names)):
        user = User()
        user.first_name = first_names[i]
        user.last_name = last_names[i]
        user.username = user.first_name.lower()
        user.email = user.username + "@example.com"
        user.password = generate_password_hash(
            ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10)))
        db.session.add(user)

    db.session.commit()
    return

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()


'''end of flask admin'''

# change /forgot password

"""Confirm change of email' functionality"""

app.config.update(
    DEBUG=True,
    SQLALCHEMY_DATABASE_URI='sqlite:///sample_db.sqlite',
    SECRET_KEY='1a2b3c4d5e6f',
    SECURITY_CONFIRMABLE=True,
    SECURITY_REGISTERABLE=True,
    SECURITY_RECOVERABLE=True,
    SECURITY_CHANGEABLE=True,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECURITY_PASSWORD_HASH='bcrypt',
    SECURITY_PASSWORD_SALT='a1b2c3d4e5f6',
)

Mail(app)
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, )
    fname = db.Column(db.String, NOT_NULL=True)
    lname = db.Column(db.String, NOT_NULL=True)
    email = db.Column(db.String(50), NOT_NULL=True, unique=True)
    tellnumber = db.Column(db.Integer, NOT_NULL=True)
    username = db.Column(db.String, not_null=True, unique=True)
    password = db.Column(db.String)
    user_type = db.Column(db.String(225))
    confirmed_at = db.Column(db.DateTime())

    roles = []


user_datastore = SQLAlchemyUserDatastore(db, User, None)
security_ctx = Security(app, user_datastore)


@security_ctx.send_mail_task
def security_send_mail(msg):
    """Send Flask-Security emails via custom function."""
    send_mail(
        sender=msg.sender, recipients=msg.recipients,
        subject=msg.subject, body=msg.body)


@app.before_first_request
def setup_db():
    db.create_all()


@app.route('/reset')
def home():
    return render_template('home.html')


app.add_url_rule(
    '/confirm-change-email/<token>',
    endpoint=None,
    view_func=confirm_change_email)

app.add_url_rule(
    '/change-email',
    endpoint=None,
    view_func=change_email,
    methods=['GET', 'POST'])

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib3 import urlopen, Request


@app.route('/get_data')
def my_form():
    return render_template('publicpost.html')


@app.route('/get_data', methods=['POST'])
def public_post():
    app_id = request.form['app_id']
    app_secret = request.form['app_secret']
    page_id = request.form['page_id']
    since_date = request.form['since_date']
    until_date = request.form['until_date']
    access_token = app_id + "|" + app_secret

    def request_until_succeed(url):
        req = Request(url)
        success = False
        while success is False:
            try:
                response = urlopen(req)
                if response.getcode() == 200:
                    success = True
            except Exception as e:
                print(e)
                time.sleep(5)

                print("Error for URL {}: {}".format(url, datetime.datetime.now()))
                print("Retrying.")

        return response.read()

    # Needed to write tricky unicode correctly to csv
    def unicode_decode(text):
        try:
            return text.encode('utf-8').decode('utf-8')
        except UnicodeDecodeError:
            return text.encode('utf-8')

    def getFacebookPageFeedUrl(base_url):
        fields = "&fields=message,link,created_time,permalink_url,type,name,id" + "comments.limit(0).summary(true),shares,reactions" + ".limit(0).summary(true)"

        return base_url + fields

    def getReactionsForStatuses(base_url):

        reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
        reactions_dict = {}  # dict of {status_id: tuple<6>}

        for reaction_type in reaction_types:
            fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
                reaction_type.upper())

            url = base_url + fields

            data = json.loads(request_until_succeed(url))['data']

            data_processed = set()  # set() removes rare duplicates in statuses
            for status in data:
                id = status['id']
                count = status['reactions']['summary']['total_count']
                data_processed.add((id, count))

            for id, count in data_processed:
                if id in reactions_dict:
                    reactions_dict[id] = reactions_dict[id] + (count,)
                else:
                    reactions_dict[id] = (count,)

        return reactions_dict

    def processFacebookPageFeedStatus(status):

        # The status is now a Python dictionary, so for top-level items,
        # we can simply call the key.

        # Additionally, some items may not always exist,
        # so must check for existence first

        status_id = status['id']
        status_type = status['type']

        status_message = '' if 'message' not in status else \
            unicode_decode(status['message'])
        link_name = '' if 'name' not in status else \
            unicode_decode(status['name'])
        status_link = '' if 'link' not in status else \
            unicode_decode(status['link'])
        status_permalink_url = '' if 'permalink_url' not in status.keys() else \
            unicode_decode(status['permalink_url'])

        # Time needs special care since a) it's in UTC and
        # b) it's not easy to use in statistical programs.

        status_published = datetime.datetime.strptime(
            status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
        status_published = status_published + \
                           datetime.timedelta(hours=-5)  # EST
        status_published = status_published.strftime(
            '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

        # Nested items require chaining dictionary keys.

        num_reactions = 0 if 'reactions' not in status else status['reactions']['summary']['total_count']
        num_comments = 0 if 'comments' not in status else status['comments']['summary']['total_count']
        num_shares = 0 if 'shares' not in status else status['shares']['count']

        return (status_id, status_message, link_name, status_type, status_link, status_permalink_url,
                status_published, num_reactions, num_comments, num_shares)

    def scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date):
        with open('{}_facebook_statuses.csv'.format(page_id), 'w', encoding='utf-8') as file:
            w = csv.writer(file)
            w.writerow(["status_id", "status_message", "link_name", "status_type",
                        "status_link", "permalink_url", "status_published", "num_reactions",
                        "num_comments", "num_shares", "num_likes", "num_loves",
                        "num_wows", "num_hahas", "num_sads", "num_angrys",
                        "num_special"])

            has_next_page = True
            num_processed = 0
            scrape_starttime = datetime.datetime.now()
            after = ''
            base = "https://graph.facebook.com/v2.9"
            node = "/{}/posts".format(page_id)
            parameters = "/?limit={}&access_token={}".format(100, access_token)
            since = "&since={}".format(since_date) if since_date \
                                                      is not '' else ''
            until = "&until={}".format(until_date) if until_date \
                                                      is not '' else ''

            print("Scraping {} Facebook Page: {}\n".format(page_id, scrape_starttime))

            while has_next_page:
                after = '' if after is '' else "&after={}".format(after)
                base_url = base + node + parameters + after + since + until

                url = getFacebookPageFeedUrl(base_url)
                statuses = json.loads(request_until_succeed(url))
                reactions = getReactionsForStatuses(base_url)

                for status in statuses['data']:

                    # Ensure it is a status with the expected metadata
                    if 'reactions' in status:
                        status_data = processFacebookPageFeedStatus(status)
                        reactions_data = reactions[status_data[0]]

                        # calculate thankful/pride through algebra
                        num_special = status_data[7] - sum(reactions_data)
                        w.writerow(status_data + reactions_data + (num_special,))

                    num_processed += 1
                    if num_processed % 100 == 0:
                        print("{} Statuses Processed: {}".format
                              (num_processed, datetime.datetime.now()))

                # if there is no next page, we're done.
                if 'paging' in statuses:
                    after = statuses['paging']['cursors']['after']
                else:
                    has_next_page = False

            print("\nDone!\n{} Statuses Processed in {}".format(
                num_processed, datetime.datetime.now() - scrape_starttime))

    scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date)

    return page_id


@app.route('/comment')
def my_form1():
    return render_template('publiccomment.html')


@app.route('/comment', methods=['POST'])
def public_comment():
    app_id = request.form['app_id']
    app_secret = request.form['app_secret']
    file_id = request.form['page_id']
    access_token = app_id + "|" + app_secret

    def request_until_succeed(url):
        req = Request(url)
        success = False
        while success is False:
            try:
                response = urlopen(req)
                if response.getcode() == 200:
                    success = True
            except Exception as e:
                print(e)
                time.sleep(5)

                print("Error for URL {}: {}".format(url, datetime.datetime.now()))
                print("Retrying.")

        return response.read()

    # Needed to write tricky unicode correctly to csv

    def unicode_decode(text):
        try:
            return text.encode('utf-8').decode()
        except UnicodeDecodeError:
            return text.encode('utf-8')

    def getFacebookCommentFeedUrl(base_url):
        # Construct the URL string
        fields = "&fields=id,message" + \
                 ",created_time,comments,from,attachment"
        url = base_url + fields

        return url

    def getReactionsForComments(base_url):
        reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
        reactions_dict = {}  # dict of {status_id: tuple<6>}

        for reaction_type in reaction_types:
            fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
                reaction_type.upper())
            # fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
            #   reaction_type.upper())

            url = base_url + fields

            data = json.loads(request_until_succeed(url))['data']

            data_processed = set()  # set() removes rare duplicates in statuses
            for status in data:
                id = status['id']
                count = status['reactions']['summary']['total_count']
                data_processed.add((id, count))

            for id, count in data_processed:
                if id in reactions_dict:
                    reactions_dict[id] = reactions_dict[id] + (count,)
                else:
                    reactions_dict[id] = (count,)

        return reactions_dict

    def processFacebookComment(comment, status_id, parent_id=''):
        # The status is now a Python dictionary, so for top-level items,
        # we can simply call the key.

        # Additionally, some items may not always exist,
        # so must check for existence first

        comment_id = comment['id']
        comment_message = '' if 'message' not in comment or comment['message'] \
                                is '' else unicode_decode(comment['message'])
        # comment_author = unicode_decode(comment['from']['name'])
        num_reactions = 0 if 'reactions' not in comment else \
            comment['reactions']['summary']['total_count']

        if 'attachment' in comment:
            attachment_type = comment['attachment']['type']
            attachment_type = 'gif' if attachment_type == 'animated_image_share' \
                else attachment_type
            attach_tag = "[[{}]]".format(attachment_type.upper())
            comment_message = attach_tag if comment_message is '' else \
                comment_message + " " + attach_tag

        # Time needs special care since a) it's in UTC and
        # b) it's not easy to use in statistical programs.

        comment_published = datetime.datetime.strptime(
            comment['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
        comment_published = comment_published + datetime.timedelta(hours=-5)  # EST
        comment_published = comment_published.strftime(
            '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

        # Return a tuple of all processed data

        return (comment_id, status_id, parent_id, comment_message,
                comment_published, num_reactions)

    def scrapeFacebookPageFeedComments(page_id, access_token):
        with open('{}_facebook_comments.csv'.format(file_id), 'w', encoding="utf-8") as file:
            w = csv.writer(file)
            w.writerow(["comment_id", "status_id", "parent_id", "comment_message",
                        "comment_published", "num_reactions",
                        "num_likes", "num_loves", "num_wows", "num_hahas",
                        "num_sads", "num_angrys", "num_special"])

            num_processed = 0
            scrape_starttime = datetime.datetime.now()
            after = ''
            base = "https://graph.facebook.com/v2.9"
            parameters = "/?limit={}&access_token={}".format(
                100, access_token)

            print("Scraping {} Comments From Posts: {}\n".format(
                file_id, scrape_starttime))

            with open('{}_facebook_statuses.csv'.format(file_id), 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Uncomment below line to scrape comments for a specific status_id
                # reader = [dict(status_id='5550296508_10154352768246509')]

                for status in reader:
                    has_next_page = True

                    while has_next_page:

                        node = "/{}/comments".format(status['status_id'])
                        after = '' if after is '' else "&after={}".format(after)
                        base_url = base + node + parameters + after

                        url = getFacebookCommentFeedUrl(base_url)
                        # print(url)
                        comments = json.loads(request_until_succeed(url))
                        reactions = getReactionsForComments(base_url)

                        for comment in comments['data']:
                            comment_data = processFacebookComment(
                                comment, status['status_id'])
                            reactions_data = reactions[comment_data[0]]

                            # calculate thankful/pride through algebra
                            num_special = comment_data[5] - sum(reactions_data)
                            w.writerow(comment_data + reactions_data +
                                       (num_special,))

                            if 'comments' in comment:
                                has_next_subpage = True
                                sub_after = ''

                                while has_next_subpage:
                                    sub_node = "/{}/comments".format(comment['id'])
                                    sub_after = '' if sub_after is '' else "&after={}".format(
                                        sub_after)
                                    sub_base_url = base + sub_node + parameters + sub_after

                                    sub_url = getFacebookCommentFeedUrl(
                                        sub_base_url)
                                    sub_comments = json.loads(
                                        request_until_succeed(sub_url))
                                    sub_reactions = getReactionsForComments(
                                        sub_base_url)

                                    for sub_comment in sub_comments['data']:
                                        sub_comment_data = processFacebookComment(
                                            sub_comment, status['status_id'], comment['id'])
                                        sub_reactions_data = sub_reactions[
                                            sub_comment_data[0]]

                                        num_sub_special = sub_comment_data[
                                                              5] - sum(sub_reactions_data)

                                        w.writerow(sub_comment_data +
                                                   sub_reactions_data + (num_sub_special,))

                                        num_processed += 1
                                        if num_processed % 100 == 0:
                                            print("{} Comments Processed: {}".format(
                                                num_processed,
                                                datetime.datetime.now()))

                                    if 'paging' in sub_comments:
                                        if 'next' in sub_comments['paging']:
                                            sub_after = sub_comments[
                                                'paging']['cursors']['after']
                                        else:
                                            has_next_subpage = False
                                    else:
                                        has_next_subpage = False

                            # output progress occasionally to make sure code is not
                            # stalling
                            num_processed += 1
                            if num_processed % 100 == 0:
                                print("{} Comments Processed: {}".format(
                                    num_processed, datetime.datetime.now()))

                        if 'paging' in comments:
                            if 'next' in comments['paging']:
                                after = comments['paging']['cursors']['after']
                            else:
                                has_next_page = False
                        else:
                            has_next_page = False

            print("\nDone!\n{} Comments Processed in {}".format(
                num_processed, datetime.datetime.now() - scrape_starttime))

    scrapeFacebookPageFeedComments(file_id, access_token)
    return file_id


@app.route('/private_data')
def index1():
    return render_template('indexprivate.html', page_name=config.page_name)


@app.route('/private_data', methods=['POST'])
def index_post():
    error = None
    url = request.form['text']

    if request_once(url) == None:
        message = "Please make sure you entered a vaild url"
        return jsonify({"error": message})

    if get_page_name(url) != config.page_name:
        message = "Please enter a post url for the {0} page".format(config.page_name)
        return jsonify({"error": message})

    post_id = get_post_id(url)

    status_id = "{0}_{1}".format(config.page_id, post_id)

    if status_id == None:
        message = "Please make sure you entered a vaild Facebook url"
        return jsonify({"error": message})

    si = io.StringIO()
    cw = csv.writer(si)

    # add a filename
    headers = Headers()
    headers.set('Content-Disposition', 'attachment', filename='fb_comments.csv')

    # stream the response as the data is generated
    return Response(
        stream_with_context(scrapeFacebookPageFeedComments(
            si,
            cw,
            config.page_id,
            config.access_token,
            status_id)),
        mimetype='application/download', headers=headers
    )


if __name__ == '__main__':
    update_model(db_path=db, model=clf, batch_size=100)
    app.run(debug=False)

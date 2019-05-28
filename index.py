from collections import Counter
import matplotlib.pyplot as plt
from update import update_model
import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask import redirect, flash
from hello import final_transformer
import pickle
import pickle as pi
from flask import Flask, render_template, redirect, url_for, request,session
import sqlite3 as sql
import sqlite3


app = Flask(__name__)
app.secret_key = "any string"

@app.route('/')
def login_page():
    return render_template('loginpage.html')
@app.route('/user_login', methods=['GET', 'POST'])
def login1(dbUser=None,dbPass=None,dbusertype=None):
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usertype = request.form['usertype']

        if usertype == 'user':

            con = sql.connect("database.db")
            con.row_factory = sql.Row

            cur = con.cursor()
            cur.execute("select * from userss where user_type = ('user') ")

            rows = cur.fetchall();
            for row in rows:
                dbUser = row["username"]
                dbPass = row["password"]
                dbusertype = row["user_type"]
            if username == dbUser and password == dbPass and usertype == dbusertype:
                return redirect(url_for('main'))

        elif usertype == 'admin':
            con = sql.connect("database.db")
            con.row_factory = sql.Row

            cur = con.cursor()
            cur.execute("select * from userss where user_type = ('admin') ")

            rows = cur.fetchall();
            for row in rows:
                dbUser = row["username"]
                dbPass = row["password"]
                dbusertype = row["user_type"]
            if username == dbUser and password == dbPass and usertype == dbusertype:
                return redirect(url_for('admin_panel'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('userlogin.html', error=error)


#this
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            tell = request.form['no']
            username = request.form['username']
            passs = request.form['pass']
            user_type = request.form['user']


            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("INSERT INTO userss (fname,lname,email,tellnumber,username,password,user_type) VALUES(?, ?, ?, ?, ?, ?, ?)",(fname, lname, email, tell, username, passs,user_type))

                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return redirect(url_for('login1'))
            con.close()
    else:
        return render_template('userlogin.html')

#this

cur_dir = os.path.dirname(__file__)

clf = pickle.load(open(os.path.join(cur_dir, 'finall_modell.sav'), 'rb'))

db = os.path.join(cur_dir, 'sent.sqlite')

def train(df, y):
	X = final_transformer.transform(df)
	clf.fit(X, y, sample_weight=None)


def sqlite_entry(path, Post,Comment,y):
	conn = sqlite3.connect(path)
	c = conn.cursor()
	c.execute("INSERT INTO sent (Post, Comment, Sentiment)"\
			" VALUES (?, ?, ?)", (Post,Comment, y))
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
    #train(df, y)
    sqlite_entry(db, Post, Comment,  y)
    return render_template('main.html')



image_folder = os.path.join('static', 'image')
ALLOWED_EXTENSIONS = set(['CSV', 'csv'])


app.config['UPLOAD_FOLDER'] = image_folder

#UPLOAD_FOLDER = 'C:/Users/hamza/PycharmProjects/exercise/try'
#ALLOWED_EXTENSIONS = set(['CSV', 'csv'])

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


    return render_template('adminlogin.html', error=error)

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







def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin_upload', methods=['GET', 'POST'])
def admin_upload(filename=None):
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
            #print(y)
            df = df.drop('Sentiment', axis=1)
            #print(df)
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
    return render_template('adminupdate.html', filename=filename)


plt.style.use('ggplot')

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route('/graph', methods=['GET', 'POST'])
def upload_file(filename=None, column=None, data=None, my_prediction=None, df=None):
    image_folder = os.path.join('static', 'image')
    app.config['UPLOAD_FOLDER'] = image_folder
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
            file_path = os.path.join(app.config['image_folder'], filename)
            # file.save(file_path)
            missing_values = ["no info", ".", "n/a", "na", "--", "N/A", "NA", "??", "?"]
            df = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',', delimiter=None, header=0, index_col=None,
                             squeeze=False, engine='python', usecols=range(0, 3), na_values=missing_values)
            df['Post'].fillna(method="ffill", inplace=True)
            df['Comment'].fillna(method="ffill", inplace=True)
            vec = final_transformer.transform(df)
            my_prediction = clf.predict(vec)
            df['Sentiment'] = my_prediction
            df['Sentiment'].value_counts().plot(kind='bar', title='Sentiment of classification')
            save_image_to = 'C:/Users/atwiine/PycharmProjects/finalyearproject/static/image/'
            plt.savefig(save_image_to + "image.png")
            images = os.path.join(app.config['UPLOAD_FOLDER'], 'image.png')
            line_labels, line_values = creategraph(df['Sentiment'])
            desc = df.describe(include='all')
            return render_template('line_chart.html', title='Line graph showing Sentiment Analysis',
                                   max=50, labels=line_labels, values=line_values, df=df.to_html(), stat=desc.to_html(),
                                   csv=df.to_csv(), use=images)

    return render_template('upload.html', filename=filename, data=data, column=column, predict=my_prediction, df=df)


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

@app.route("/savedetails",methods = ["POST","GET"])
def saveDetails():
    msg = None
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            tell = request.form['no']
            username = request.form['username']
            passs = request.form['pass']
            user_type = request.form['user']

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute(
                    "INSERT INTO userss (fname,lname,email,tellnumber,username,password,user_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (fname, lname, email, tell, username, passs, user_type))

                con.commit()
                msg = "User added successfully"
        except:
            con.rollback()
            msg = "User not added!, use the right credentials. "

        finally:
            return render_template('add_user.html', msg=msg)
            con.close()


    else:
        return render_template('add_user.html', msg=msg)

@app.route("/view")
def view():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from userss")
    rows = cur.fetchall()
    return render_template("view.html",rows = rows)


@app.route("/delete")
def delete():
    return render_template("delete.html")

@app.route("/deleteuser",methods = ["POST"])
def deleteuser():
    msg=None
    id = request.form["id"]
    with sqlite3.connect("database.db") as con:
        try:
            cur = con.cursor()
            cur.execute("delete  from userss where id = ?", id)
            msg = "user successfully deleted"
        except:
            msg = "can't be deleted"
        finally:
            return render_template("delete.html", msg=msg)

# end add user

if __name__ == '__main__':
    update_model(db_path=db, model=clf, batch_size=100)
    app.run(debug=True)

















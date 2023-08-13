from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'To-Do-App'
app.config['MONGO_URI'] = 'mongodb+srv://Nithish:nit53101@cluster0.lzn3c.mongodb.net/To-Do-App'

mongo = PyMongo(app)
users = mongo.db.users
todos = mongo.db.todos
tododel = mongo.db.deltodo

@app.route('/')
def index():
    if 'username' in session:
       session.pop('username', None)
       return render_template('index.html')
    return render_template('index.html')

@app.route('/login', methods=['POST' , 'GET'])
def login():
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            username = request.form['username']
            session['username']= username
            return redirect(url_for('list'))
    else:
       flash('INCORRECT USERNAME OR PASSWORD .', category='1')
       return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        username = request.form.get('username')
        if len(username) < 5:
                flash('First name must be greater than 4 character.', category='1')
                return redirect(url_for('register'))
        existing_user = users.find_one({'name' : username})

        if existing_user is None:
            email = request.form.get('email')
            if len(email) < 7:
                flash('Email must be greater than 6 characters.', category='1')
                return redirect(url_for('register'))
            password=request.form['password']
            if len(password) < 8:
                flash('Password must be at least 8 characters.', category='1')
                return redirect(url_for('register'))
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
           # dob = request.form('date')
            users.insert_one({'name' : username, 'password' : hashpass , 'email' : email})

            #users.insert_one({'name' : request.form['username'], 'password' : hashpass , 'email' : request.form['email'] , 'DOB' : request.form['DOB']})
            username = request.form['username']
            session['username']= username
            flash('ACCOUNT SUCCESSFULLY CREATED .', category='2')
            return redirect(url_for('index'))
        
        else:
            flash('USER NAME ALREADY EXISTS .', category='1')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/list')
def list():
    if "username" in session:
        saved_todos = todos.find()
        return render_template('list.html', todos=saved_todos)
    else:
        return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_todo():
    new_todo = request.form.get('new-todo')
    todos.insert_one({'text' : new_todo, 'complete' : False})
    return redirect(url_for('list'))

@app.route('/complete/<oid>')
def complete(oid):
    todos.update_one({'_id': ObjectId(oid) , 'complete' : False} ,
                        {'$set': {'complete' : True}})
    return redirect(url_for('list'))

@app.route('/delete_completed')
def delete_completed():
    while( todos.find_one({'complete' : True}) != None):
        a=todos.find_one({'complete' : True})
        mongo.db.deltodo.insert_one((a))
        todos.delete_one({'complete' : True})
    return redirect(url_for('list'))

@app.route('/delete_all')
def delete_all():
    todos.delete_many({})
    return redirect(url_for('list'))

@app.route('/logout' , methods=['POST', 'GET'])
def logout():
   # session.pop('users_id', None)
    return redirect(url_for('index'))

@app.route('/trash')
def trash():
    if "username" in session:
        delto=tododel.find()
        return render_template('trash.html', tasks = delto )
    else:
        return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.secret_key = 'secke1'
    app.run(debug=True)
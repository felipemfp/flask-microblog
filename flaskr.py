# all the imports
import os, sys
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy

ENV = os.environ.get('ENV', default='Development')

# configuration
if ENV == 'Production':
    DEBUG = False
else:
    DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY', default='development key')
USERNAME = os.environ.get('USERNAME', default='admin')
PASSWORD = os.environ.get('PASSWORD', default='admin')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', default='sqlite:////tmp/flaskr.db')

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    text = db.Column(db.Text)

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return '<Entry {}>'.format(self.title)


def init_db():
    db.create_all()

# views, my lord

@app.route('/')
def show_entries():
    entries = Entry.query.all()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    newone = Entry(request.form['title'], request.form['text'])
    db.session.add(newone)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if command == 'run':
        app.run()
    elif command == 'migrate':
        init_db()

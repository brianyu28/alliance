from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain

home = Blueprint('home', __name__,
                        template_folder='../templates/home')

@home.route('/')
def homepage():
    if 'id' in session:
        # user is logged in, go to the portal
        return redirect(url_for('portal.portal_page'))
    else:
        return render_template('homepage.html')

@home.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        authenticated = dbmain.authenticate(request.form['username'], request.form['password'])
        if authenticated:
            user_id = str(dbmain.userByUsername(request.form['username'])['_id'])
            session['id'] = user_id
            return redirect(url_for('home.homepage'))
        else:
            return render_template('login.html', error='Your login credentials were incorrect.')

@home.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        # submitted register form, so register the user
        req_fields = ['first', 'last', 'email', 'username', 'password', 'password_confirm', 'acct_type', 'school']
        for field in req_fields:
            if request.form[field] == '':
                return render_template('register.html', error='All fields must be complete in order to register.')
        if request.form['password'] != request.form['password_confirm']:
            return render_template('register.html', error='Your passwords did not match.')
        if (request.form['acct_type'] == "None"):
            return render_template('register.html', error='You must select an account type.')
        # need to add username checking to see if username already exists
        if (not dbmain.usernameAvailable(request.form['username'])):
            return render_template('register.html', error='Your requested username is already taken.')
        user_id = dbmain.addUser(request.form['username'], helpers.get_hashed_password(request.form['password']), request.form['first'], request.form['last'], request.form['email'], request.form['acct_type'], request.form['school'])
        session['id'] = str(user_id)
        return redirect(url_for('home.homepage'))

@home.route('/about/')
def about():
    return render_template('about.html')

@home.route('/contact/')
def contact():
    return render_template('contact.html')

@home.route('/getstarted/')
def getstarted():
    return render_template('getstarted.html')

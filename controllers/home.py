from flask import Blueprint, render_template

home = Blueprint('home', __name__,
                        template_folder='../templates/home')

@home.route('/')
def homepage():
   return render_template('homepage.html')

@home.route('/login/')
def login():
    return render_template('login.html')

@home.route('/register/')
def register():
    return render_template('register.html')

@home.route('/about/')
def about():
    return render_template('about.html')

@home.route('/contact/')
def contact():
    return render_template('contact.html')

@home.route('/getstarted/')
def getstarted():
    return render_template('getstarted.html')


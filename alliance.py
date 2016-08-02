from flask import Flask, render_template
from controllers import home, portal, fair, ajax, project, participants, messenger, progress, settings
from model import dbmain
import secrets

app = Flask(__name__)
app.debug = True
app.secret_key = secrets.secret_key

app.register_blueprint(home.home)
app.register_blueprint(portal.portal)
app.register_blueprint(fair.fair, url_prefix='/fair')
app.register_blueprint(project.project, url_prefix='/project')
app.register_blueprint(participants.participants, url_prefix='/roster')
app.register_blueprint(messenger.messenger, url_prefix='/messenger')
app.register_blueprint(progress.progress, url_prefix='/progress')
app.register_blueprint(settings.settings, url_prefix='/settings')
app.register_blueprint(ajax.ajax, url_prefix='/ajax')

@app.errorhandler(404)
def handle_404(e):
    return render_template('errors/errorcode.html', user=dbmain.currentUser(), code=404, message="The page you were looking for could not be found."), 404

@app.errorhandler(500)
def handle_500(e):
    return render_template('errors/errorcode.html', user=dbmain.currentUser(), code=500, message="There was an error in the server processing your request. If this problem persists, please contact Science Alliance Network support."), 500

if __name__ == "__main__":
    app.run()

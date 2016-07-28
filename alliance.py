from flask import Flask
from controllers import home, portal, fair, ajax, project, participants, messenger, progress
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
app.register_blueprint(ajax.ajax, url_prefix='/ajax')


if __name__ == "__main__":
    app.run()

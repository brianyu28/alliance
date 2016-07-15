from flask import Flask
from controllers import home, portal, fair, ajax

app = Flask(__name__)
app.debug = True
app.secret_key = 'bycrsj28\G#slf382?,/2CXt9VE28'

app.register_blueprint(home.home)
app.register_blueprint(portal.portal)
app.register_blueprint(fair.fair, url_prefix='/fair')
app.register_blueprint(ajax.ajax, url_prefix='/ajax')

if __name__ == "__main__":
    app.run()

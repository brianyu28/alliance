from flask import Flask
from controllers.home import home
from controllers.portal import portal

app = Flask(__name__)
app.secret_key = 'bycrsj28\G#slf382?,/2CXt9VE28'

app.register_blueprint(home)
app.register_blueprint(portal)
 
if __name__ == "__main__":
    app.run()

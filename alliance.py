from flask import Flask
from controllers import home, portal, fair

app = Flask(__name__)
app.secret_key = 'bycrsj28\G#slf382?,/2CXt9VE28'

app.register_blueprint(home.home)
app.register_blueprint(portal.portal)
app.register_blueprint(fair.fair)
 
if __name__ == "__main__":
    app.run()

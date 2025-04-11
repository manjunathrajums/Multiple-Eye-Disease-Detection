from flask import Flask
from lib.routes.route import api_bp
from lib.extensions import mongo  
from flask_cors import CORS
app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://localhost:27017/Eyedisease"
CORS(app)
mongo.init_app(app)  
app.register_blueprint(api_bp, url_prefix="/")

if __name__ == '__main__':
    app.run(debug=True)

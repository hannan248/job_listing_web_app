from flask import Flask
from flask_cors import CORS
from config import Config
from db import db
from routes.job_routes import job_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    db.init_app(app)
    
    app.register_blueprint(job_routes, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
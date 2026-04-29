# backend/app.py
import os
from flask import Flask, redirect, url_for
from backend.models import db
from backend.auth import auth_bp, login_manager
from backend.routes import routes as routes_bp 

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Konfigürasyon
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///pgm_system.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Eklentiler
    db.init_app(app)
    login_manager.init_app(app)

    # Blueprintler
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    # Ana yönlendirme
    @app.route("/")
    def index():
        from flask_login import current_user
        if getattr(current_user, "is_authenticated", False):
            return redirect(url_for("routes.dashboard"))  
        return redirect(url_for("auth.login"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

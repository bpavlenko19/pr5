from flask import Flask, jsonify, request
from flask_smorest import Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from db import db
from resources.item import blp as ItemBlueprint
from resources.user import blp as UserBlueprint
from models import UserModel  # Імпортуємо модель користувача
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Конфігурація
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Items REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_JSON_PATH"] = "openapi.json"
app.config["JWT_SECRET_KEY"] = "jose"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Ініціалізація
db.init_app(app)
api = Api(app)
jwt = JWTManager(app)

# Кореневий маршрут для перевірки
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Items REST API!"}), 200

# Реєстрація ресурсів
api.register_blueprint(ItemBlueprint)
api.register_blueprint(UserBlueprint)

if __name__ == "__main__":
    app.run(debug=True)

# Обробка помилок JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Request does not contain an access token.", "error": "authorization_required"}), 401

# Реєстрація користувача
@app.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")

    if UserModel.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    user = UserModel(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)

    return jsonify({"message": "User created successfully", "access_token": access_token}), 201

# Логін користувача
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = UserModel.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid credentials"}), 401

# Перевірка користувача
@app.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = UserModel.query.get_or_404(user_id)

    return jsonify({"username": user.username, "id": user.id}), 200

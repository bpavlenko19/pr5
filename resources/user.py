from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from models import UserModel
from flask_smorest import Blueprint

# Ініціалізація Blueprint для користувачів
blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")

    # Перевірка чи існує користувач
    if UserModel.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    # Хешування пароля перед збереженням
    hashed_password = generate_password_hash(password)
    user = UserModel(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    # Генерація токену після реєстрації
    access_token = create_access_token(identity=user.id)

    return jsonify({"message": "User created successfully", "access_token": access_token}), 201

@blp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = UserModel.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid credentials"}), 401

@blp.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = UserModel.query.get_or_404(user_id)

    return jsonify({"username": user.username, "id": user.id}), 200

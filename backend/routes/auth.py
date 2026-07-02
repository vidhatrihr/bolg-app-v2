from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=['POST'])
def login():
  data = request.get_json()
  user = User.query.filter_by(email=data['email']).first()

  if not user or not check_password_hash(user.password, data['password']):
    return jsonify({'message': "Invalid credentials"}), 401

  login_user(user)
  return jsonify({'message': 'Logged in', 'data': {'name': user.name, 'email': user.email}})


@auth_bp.route("/register", methods=['POST'])
def register():
  data = request.get_json()

  if User.query.filter_by(email=data['email']).first():
    return jsonify({'message': "Email already registered"})

  user = User(
      name=data['name'],
      email=data['email'],
      password=generate_password_hash(data['password']),
  )

  db.session.add(user)
  db.session.commit()

  login_user(user)
  return jsonify({'message': 'Account created', 'data': {
      'name': user.name, 'email': user.email
  }})


@auth_bp.route("/logout")
@login_required
def logout():
  logout_user()
  return jsonify({'message': "Logged out"})


@auth_bp.route("/me")
@login_required
def me():
  return jsonify({"message": "login ok", 'data': {
      "name": current_user.name, 'email': current_user.email
  }})

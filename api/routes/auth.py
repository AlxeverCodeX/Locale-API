import uuid
from flask_restx import Namespace, Resource, fields
from ..model.db import connect_to_db
from http import HTTPStatus
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity


auth_ns = Namespace('auth', description='Namesake for Authentication')

#   User model
user_model = auth_ns.model('User', {
    'first_name': fields.String(required=True, description='User first name'),
    'last_name': fields.String(required=True, description='User last name'),
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password')
})

#   Login model
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password')
})

#   Database connection
database = connect_to_db()

@auth_ns.route('/register')
class SignUp(Resource):
    @auth_ns.expect(user_model)
    @auth_ns.doc(description='Register a new user')
    def post(self):
        """
            Register a new user
        """

        data = request.get_json()

        #   Check if user already exists
        user = database.users.find_one({'email': data['email']})

        if user:
            return {'message': 'User already exists'}, HTTPStatus.BAD_REQUEST

        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        password = data['password']

        user = {
            'first_name': first_name,
            'last_name' : last_name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow()
        }

        #   Insert user into database
        database.users.insert_one(user)

        return {'message': 'User created successfully'}, HTTPStatus.CREATED
    
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc(description='Login a user', 
                 params={'email': 'User email address', 
                        'password': 'User password'})
    def post(self):
        """
            Login a user
        """

        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        #   Check if email and password are provided
        if not email or not password:
            return {'message': 'Email and password required'}, HTTPStatus.BAD_REQUEST
        
        #   Check if user exists
        user = database.users.find_one({'email': email})

        #   Check if user exists and password is correct
        if user and check_password_hash(user['password_hash'], password):

            api_key = str(uuid.uuid4())

            #   Update user's api key
            database.users.update_one({'email': email}, {'$set': {'api_key': api_key}})
            
            #   Generate access and refresh tokens
            access_token = create_access_token(identity=str(ObjectId(user['_id'])))
            refresh_token = create_refresh_token(identity=str(ObjectId(user['_id'])))

            return {
                'message': 'User logged in',
                'access_token': access_token,
                'refresh_token': refresh_token
            }, HTTPStatus.OK



@auth_ns.route('/refresh')
class Refresh(Resource):
    def post(self):
        """
            Refresh a user's token
        """

        return {'message': 'Token refreshed'}
    
@auth_ns.route('/logout')
class Logout(Resource):
    def post(self):
        """
            Logout a user
        """

        return {'message': 'User logged out'}
    
@auth_ns.route('/reset-password')
class ResetPassword(Resource):
    def post(self):
        """
            Reset a user's password
        """

        return {'message': 'Password reset'}
    
@auth_ns.route('/forgot-password')
class ForgotPassword(Resource):
    def post(self):
        """
            Forgot a user's password
        """

        return {'message': 'Password reset'}
    
@auth_ns.route('/confirm-email')
class ConfirmEmail(Resource):
    def post(self):
        """
            Confirm a user's email
        """

        return {'message': 'Email confirmed'}
    
@auth_ns.route('/resend-confirmation-email')
class ResendConfirmationEmail(Resource):
    def post(self):
        """
            Resend a user's confirmation email
        """

        return {'message': 'Email resent'}


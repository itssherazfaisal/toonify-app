import os
from flask import Flask, request, jsonify, send_file, make_response, render_template
import requests
from PIL import Image
from io import BytesIO
import torch
from torchvision.transforms import ToPILImage
from utils import transform, Transformer
from flask_sqlalchemy import SQLAlchemy
import uuid # for public id
from werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS

# creates Flask object
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'
# configuration
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# INSTEAD CREATE A .env FILE AND STORE IN IT
app.config['SECRET_KEY'] = 'TOONIFYAPPSECRETS'
app.config['SIGNUP_SECRET_KEY'] = 'TOONIFYAPPSECRETS'
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)

# Database ORMs
class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	public_id = db.Column(db.String(50), unique = True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(70), unique = True)
	password = db.Column(db.String(80))

# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query\
                .filter_by(public_id = data['public_id'])\
                .first()
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 500
        # returns the current logged in users context to the routes
        return f(current_user, *args, **kwargs)

    return decorated

# route for logging user in
@app.route('/login', methods =['POST'])
def login():
	# creates dictionary of form data
	auth = request.form

	if not auth or not auth.get('email') or not auth.get('password'):
		# returns 401 if any email or / and password is missing
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
		)

	user = User.query\
		.filter_by(email = auth.get('email'))\
		.first()

	if not user:
		# returns 401 if user does not exist
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
		)

	if check_password_hash(user.password, auth.get('password')):
		# generates the JWT Token
		token = jwt.encode({
			'public_id': user.public_id,
			'exp' : datetime.utcnow() + timedelta(minutes = 30)
		}, app.config['SECRET_KEY'])

		return make_response(jsonify({'token' : token}), 200)
	# returns 403 if password is wrong
	return make_response(
		'Could not verify',
		403,
		{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
	)

# signup route
@app.route('/signup', methods =['POST'])
def signup():
    # creates a dictionary of the form data
    data = request.form

    # gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')
    secret = data.get('secret')
    if secret == app.config['SIGNUP_SECRET_KEY']:
        # checking for existing user
        user = User.query\
            .filter_by(email = email)\
            .first()
        if not user:
            # database ORM object
            user = User(
                public_id = str(uuid.uuid4()),
                name = name,
                email = email,
                password = generate_password_hash(password)
            )
            # insert user
            db.session.add(user)
            db.session.commit()

            return make_response('Successfully registered.', 200)
        else:
            # returns 202 if user already exists
            return make_response('User already exists. Please Log in.', 202)
    else:
        return make_response('Not Authenticated to SignUp', 202)



# Function to download models
def download_model(style):
    model_url = f"http://vllab1.ucmerced.edu/~yli62/CartoonGAN/pytorch_pth/{style}_net_G_float.pth"
    print(f"The pytorch model {model_url} is getting downloaded...")
    response = requests.get(model_url)
    if response.status_code == 200:
        with open(f"models/{style}_net_G_float.pth", 'wb') as f:
            f.write(response.content)
        return True
    return False

# Models
def load_models():
    styles = ["Hosoda", "Hayao", "Shinkai", "Paprika"]
    models = {}
    os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)
    for style in styles:
        model = Transformer()
        path = f"{app.config['MODEL_FOLDER']}/{style}_net_G_float.pth"
        if not os.path.exists(f"{app.config['MODEL_FOLDER']}/{style}_net_G_float.pth"):
            download_model(style)
        model.load_state_dict(torch.load(f"{app.config['MODEL_FOLDER']}/{style}_net_G_float.pth"))
        model.eval()
        models[style] = model
    return models 

# Endpoint for uploading an image and getting a cartoon-style image
@app.route('/cartoonify', methods=['POST'])
@token_required
def cartoonify(current_user):
    if 'image' not in request.files:
        return jsonify(error="No image provided."), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify(error="No image selected."), 400
    params = request.form
    style = params.get("style", "Hasoda")
    image_size = params.get("image_size", 500)
    img = transform(models, style, image, int(image_size))

    # Save the cartoon-style image
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], 'cartoon_output.jpg'))

    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'cartoon_output.jpg'), as_attachment=True)

@app.route('/')
def render_index():
    return render_template('index.html')

if __name__ == '__main__':
    models = load_models()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=False)

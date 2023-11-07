# Toonify App

Toonify App is a web application that allows you to convert images to cartoons using pre-trained deep learning models.

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/your-username/toonify-app.git
   ```

2. Navigate to the project directory:
   ```bash
   cd toonify-app
   ```

3. Install the required dependencies using requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## Database Initialization

Before running the app, you need to initialize the database and create a dummy user for testing.

Initialize the db and create a dummy user (for testing purposes):
   ```bash
   python initialize_db.py
   ```

## Starting the Server

To start the Toonify App server, run the following command:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`.

## API Endpoints

### Authentication

To access the API endpoints, you need to authenticate and obtain an access token.

- **Login**: `POST /login`

  - Provides an access token for a registered user. (for dummy user, we can test it out for email "test@gmail.com" and password "test123")

- **Signup**: `POST /signup`

  - Allows users to create an account. (to create a new account, we would name, email, password, secret. The secret would allow special privilege to create a new account.)

### Image to Cartoon Conversion

- **Cartoonify**: `POST /cartoonify`

  - Upload an image and receive a cartoon-style image.

  - Requires an access token obtained through the login endpoint.

  - Parameters:
    - `image`: Image file (Multipart form-data)
    - `style` (Optional): Cartoon style (Default: "Hasoda")
    - `image_size` (Optional): Image size (Default: 500)

## User Interface

1. To access the user interface, open a web browser and go to `http://localhost:5000`.

2. Log in with your user credentials.

3. After logging in, you can upload an image, select the cartoon style, and set the image size to convert images to cartoons.

## Authentication

- The API endpoints require an access token obtained through the login endpoint.

- Ensure you include the `x-access-token` header in your requests with the access token.

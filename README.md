# Anime Recommendation System

Overview
The Anime Recommendation System is a FastAPI-based application designed to allow users to register, log in, and receive personalized anime recommendations based on their preferences. The backend system leverages JWT for secure user authentication, bcrypt for password hashing, and an SQL database to store user data and preferences. This document provides a detailed explanation of the structure, setup, and functionality of the project.

Project Structure
The project follows a modular structure with separate directories for routers, utilities, database management, and models.

app/
routers/: Contains FastAPI route definitions.
anime.py: API routes related to anime recommendations.
auth.py: API routes for user authentication (register and login).
user.py: API routes for managing user data and preferences.
models/: Contains the database models for SQLAlchemy.
schemas/: Contains Pydantic models for data validation.
utils/: Contains utility functions like database connection and security (password hashing, token creation).
templates/: Contains HTML templates for rendering views (if needed for frontend integration).
main.py: The entry point for the FastAPI application, where routers and configurations are initialized.
Installation
To run the Anime Recommendation System, follow these steps:

Clone the repository:



git clone <repository-url>
cd Anime-Recommendation-System
Create a virtual environment:



python3 -m venv venv
source venv/bin/activate   # For macOS/Linux
venv\Scripts\activate      # For Windows
Install dependencies:



pip install -r requirements.txt
Set up environment variables: Create a .env file in the root directory and add the following variables:

plaintext

SECRET_KEY=<your-secret-key>
DATABASE_URL=postgresql://<username>:<password>@localhost/<dbname>
Set up the database: The application uses SQLAlchemy to interact with a PostgreSQL database. Ensure that your PostgreSQL server is running and the database URL is correctly set in the .env file.

Run the following command to create the necessary database tables:



alembic upgrade head
Run the application: To start the server, use Uvicorn:



uvicorn app.main:app --reload
Access the API: Open your browser and go to http://127.0.0.1:8000 to access the application. The API documentation can be accessed at http://127.0.0.1:8000/docs.

API Endpoints
The system exposes the following key API endpoints:

Authentication Endpoints
Register User

URL: /auth/register
Method: POST
Request Body:
json

{
  "username": "string",
  "password": "string"
}
Response:
json

{
  "username": "string"
}
Description: Registers a new user by hashing the password and saving the user information in the database. Returns the created user's username.
Login User

URL: /auth/login
Method: POST
Request Body:
json

{
  "username": "string",
  "password": "string"
}
Response:
json

{
  "access_token": "string",
  "token_type": "bearer"
}
Description: Authenticates the user by verifying the username and password. Returns a JWT access token if credentials are correct.
User Endpoints
Get Current User
URL: /user/me
Method: GET
Headers: Authorization: Bearer <JWT_TOKEN>
Response:
json

{
  "username": "string"
}
Description: Retrieves the current authenticated user's information based on the provided JWT token.
Anime Endpoints
Get Anime Recommendations
URL: /anime/recommendations
Method: GET
Headers: Authorization: Bearer <JWT_TOKEN>
Response:
json

{
  "recommendations": [
    {
      "anime_name": "string",
      "genre": "string",
      "description": "string"
    },
    ...
  ]
}
Description: Returns a list of anime recommendations tailored to the user's preferences. The recommendations can be personalized based on user data or a set algorithm.
Security
Password Hashing: The system uses the bcrypt hashing algorithm for securely storing user passwords. This ensures that passwords are never stored in plain text in the database.

JWT Authentication: JWT (JSON Web Token) is used to authenticate users. When a user logs in, a token is generated and returned to the client. This token must be included in the Authorization header for protected routes (e.g., /user/me, /anime/recommendations).

Database Schema
The application uses SQLAlchemy for interacting with a PostgreSQL database. The primary models include:

User Model:
id: Primary key
username: Unique username
hashed_password: The hashed password stored securely
created_at: Timestamp of user creation
Utils
Password Hashing: The utility function hash_password is used to hash passwords before storing them in the database. The verify_password function is used to compare the entered password with the stored hash during login.

Token Generation: The create_access_token function generates a JWT token with a configurable expiration time (default: 30 minutes).

Example Request & Response
Register User
Request:



POST /auth/register
{
   "username": "john_doe",
   "password": "password123"
}
Response:

json

{
   "username": "john_doe"
}
Login User
Request:



POST /auth/login
{
   "username": "john_doe",
   "password": "password123"
}
Response:

json

{
   "access_token": "<jwt_token>",
   "token_type": "bearer"
}
Get Recommendations
Request:



GET /anime/recommendations
Authorization: Bearer <jwt_token>
Response:

json

{
   "recommendations": [
     {
       "anime_name": "Naruto",
       "genre": "Action",
       "description": "A young ninja embarks on a quest to become the strongest ninja in his village."
     },
     {
       "anime_name": "One Piece",
       "genre": "Adventure",
       "description": "A group of pirates seek the ultimate treasure, the One Piece."
     }
   ]
}
Conclusion
This Anime Recommendation System allows users to securely register, log in, and receive personalized anime recommendations. The backend utilizes modern web development practices such as JWT for authentication, bcrypt for password hashing, and SQLAlchemy for database interaction. With FastAPI as the core framework, the application ensures high performance and scalability.

For any issues or improvements, feel free to open an issue or contribute to the repository.

# Anime Recommendation System

The Anime Recommendation System is a FastAPI-based project designed to provide personalized anime recommendations. It uses a PostgreSQL database to store data and leverages machine learning models for recommendation. This project is containerized using Docker for easier deployment and scalability.

---

## Features

- **Anime Recommendations**: Personalized suggestions based on user preferences.
- **RESTful API**: Exposes endpoints for interacting with the recommendation system.
- **Database Support**: Uses PostgreSQL for data persistence.
- **Session Management**: Supports secure session management with `SessionMiddleware`.
- **Containerized Deployment**: Easy to deploy using Docker and Docker Compose.

---

## Directory Structure

```
Anime-Recommendation-System/
|
├── app/
│   ├──      # Package initialization
│   ├── main.py           # Application entry point
│   ├── models.py         # Database models
│   ├── database.py       # Database connection setup       
│   ├── 
│  
|
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose configuration
├── README.md             # Project documentation
├── venv/                 # Virtual environment (ignored in production)
└── .env                  # Environment variables (ignored in version control)
```

---

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- PostgreSQL database

---

## Installation

### Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/cayanide/Anime-Recommendation-System.git
   cd Anime-Recommendation-System
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/yourdatabase
   SECRET_KEY=your_secret_key
   ```

5. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**:
   Open your browser and navigate to `http://127.0.0.1:8000/docs` to view the API documentation.

---

### Docker Setup

1. **Build the Docker Image**:
   ```bash
   docker-compose build
   ```

2. **Start the Containers**:
   ```bash
   docker-compose up
   ```

3. **Access the API**:
   Open your browser and navigate to `http://127.0.0.1:8000/docs`.

---

## Key Dependencies

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for interacting with the PostgreSQL database.
- **Pydantic**: Data validation and serialization.
- **Uvicorn**: ASGI server for running the FastAPI application.
- **itsdangerous**: For secure session management.
- **psycopg2**: PostgreSQL database adapter.

---

## API Endpoints

### Base URL: `/api/v1`

#### User Routes
- `POST /users/`: Create a new user.
- `GET /users/{user_id}`: Get user details.

#### Recommendation Routes
- `GET /recommendations/`: Get anime recommendations for a user.

---

## Development Notes

- Ensure the `.env` file is configured correctly for both local and Docker setups.
- Use `docker-compose down` to stop containers and clean up resources.
- Use the `requirements.txt` file to manage dependencies for consistent builds.

---

## Troubleshooting

1. **ModuleNotFoundError**:
   Ensure all dependencies in `requirements.txt` are installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Connection Issues**:
   Verify your `DATABASE_URL` in the `.env` file is correct and PostgreSQL is running.

3. **Docker Issues**:
   Force a clean rebuild of the containers:
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

---


![image](https://github.com/user-attachments/assets/2399dd09-eb51-42bb-b6b9-4079318d8d3d)

Login page 

![image](https://github.com/user-attachments/assets/f05de0db-33bc-4c46-bfde-e422abef9f76)

Registration Page

![image](https://github.com/user-attachments/assets/dcc76b34-fae6-4380-96d4-8a7b885d9dfc)


Token Generated Page JWT Token (Only For Debugging Disable in Production)

![image](https://github.com/user-attachments/assets/1943b9ec-218d-4788-8849-210cc9dac32e)

Search Page 

![image](https://github.com/user-attachments/assets/c412e663-a8f1-4c0c-94d2-15302575e44b)

Recommendation Page 

![image](https://github.com/user-attachments/assets/a55b4e79-ec3c-425d-a535-14755d828d46)

Set Prefrences 

## Contribution

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Open a pull request.

---

## License

This project is licensed under the MIT License.


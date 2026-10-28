from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from database import get_connection, create_users_table
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import EmailStr

import os

from schema.user_input import UserInput
from model.predict import predict_output, model, MODEL_VERSION
from schema.prediction_response import PredictionResponse

import time
from google.genai import errors
from fastapi import HTTPException
# LOAD ENVIRONMENT VARIABLES

load_dotenv()

# GEMINI

from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )
else:
    gemini_client = None

# FASTAPI APP

app = FastAPI()

# Authentication configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is missing from .env")

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)



# AUTHENTICATION REQUEST MODELS

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Create the users table when the API starts.
@app.on_event("startup")
def startup_create_users_table():
    create_users_table()


# SIGN UP
@app.post("/auth/register")
def register_user(data: RegisterRequest):
    username = data.username.strip()
    email = str(data.email).strip().lower()

    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")

    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long."
        )

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,)
                )
                if cur.fetchone():
                    raise HTTPException(
                        status_code=409,
                        detail="An account with this email already exists."
                    )

                cur.execute(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, username, email
                    """,
                    (username, email, hash_password(data.password))
                )
                user = cur.fetchone()

        user_id, saved_username, saved_email = user
        token = create_access_token(user_id)

        return {
            "message": "Account created successfully.",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "username": saved_username,
                "email": saved_email
            }
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not create account. Check the database connection."
        )


# LOGIN
@app.post("/auth/login")
def login_user(data: LoginRequest):
    email = str(data.email).strip().lower()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, email, password_hash
                    FROM users
                    WHERE email = %s
                    """,
                    (email,)
                )
                user = cur.fetchone()

        if not user or not verify_password(data.password, user[3]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

        user_id, username, saved_email, _password_hash = user
        token = create_access_token(user_id)

        return {
            "message": "Login successful.",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "username": username,
                "email": saved_email
            }
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not log in. Check the database connection."
        )


# HOME

@app.get("/")
def home():
    return {
        "message": "Insurance Premium Prediction API"
    }

# HEALTH CHECK

@app.get("/health")
def health_check():

    return {
        "status": "OK",
        "version": MODEL_VERSION,
        "model_loaded": model is not None
    }

# PREDICTION

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict_premium(data: UserInput):

    user_input = {
        "age": data.age,
        "smoker": data.smoker,
        "region": data.region,
        "children": data.children,
        "sex": data.sex,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "bmi": data.bmi
    }

    # Feature engineering
    user_input["age_squared"] = (
        user_input["age"] ** 2
    )

    user_input["bmi_age"] = (
        user_input["bmi"] *
        user_input["age"]
    )

    try:

        prediction = predict_output(user_input)

        return JSONResponse(
            status_code=200,
            content={
                "response": prediction
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# AI ASSISTANT REQUEST MODEL

class AssistantRequest(BaseModel):

    question: str

    predicted_premium: float

    age: int
    bmi: float
    smoker: str
    region: str
    children: int
    sex: str

    # These are generated by your UserInput schema
    age_group: str | None = None
    lifestyle_risk: str | None = None

# AI ASSISTANT


@app.post("/assistant")
def insurance_assistant(data: AssistantRequest):

    # 1. Check API key
    if gemini_client is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "GEMINI_API_KEY is not configured. "
                "Please check your .env file."
            )
        )

    # 2. Create prompt
    prompt = f"""
You are an AI Insurance Assistant inside a
Medical Insurance Premium Prediction application.

Your job is to explain the machine learning model's
prediction to the user in simple and understandable language.

CUSTOMER INFORMATION:

Age: {data.age}
BMI: {data.bmi}
Smoker: {data.smoker}
Gender: {data.sex}
Children: {data.children}
Region: {data.region}
Age Group: {data.age_group}
Lifestyle Risk: {data.lifestyle_risk}

MODEL PREDICTION:

Predicted Insurance Premium:
₹ {data.predicted_premium:,.2f}

USER QUESTION:

{data.question}

IMPORTANT RULES:

1. Explain the ML prediction, not medical conditions.
2. Do not diagnose diseases.
3. Do not prescribe medicines or treatments.
4. Do not claim that the predicted premium is guaranteed.
5. Do not invent information that is not provided.
6. Explain relevant customer factors when asked why a premium is high.
7. Explain BMI simply when asked.
8. Explain the possible relationship between customer features
   and the model prediction.
9. Clearly mention that this is an ML-based estimate.
10. Keep answers concise and easy to understand.
11. Politely redirect unrelated questions to insurance topics.

Answer the user's question now.
"""

    # 3. Try Gemini with retry and fallback
    models_to_try = [
        "gemini-3.6-flash",
        "gemini-2.5-flash",
    ]

    for model_name in models_to_try:

        for attempt in range(2):

            try:
                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                # Return successful response
                if response.text:
                    return {
                        "answer": response.text
                    }

                # Empty response: try the next model
                break

            except errors.ServerError as e:

                error_message = str(e)

                # Retry temporary server errors once
                if (
                    ("503" in error_message
                     or "UNAVAILABLE" in error_message)
                    and attempt == 0
                ):
                    time.sleep(2)
                    continue

                # Try fallback model
                break

            except Exception as e:

                raise HTTPException(
                    status_code=500,
                    detail=f"AI Assistant Error: {str(e)}"
                )

    # 4. Both models failed
    raise HTTPException(
        status_code=503,
        detail=(
            "The AI assistant is temporarily unavailable. "
            "Please try again in a moment."
        )
    )


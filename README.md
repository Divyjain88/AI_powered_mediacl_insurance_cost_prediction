💰 AI-Powered Medical Insurance Cost Prediction

📌 Project Overview

AI-Powered Medical Insurance Cost Prediction is a machine learning application that estimates medical insurance costs based on user-provided information, such as age, BMI, gender, smoking status, number of children, and region.

The project uses machine learning techniques to predict insurance charges and provides an interactive interface for users to enter their details and view estimated costs. It integrates a Streamlit frontend, a FastAPI backend, Neon PostgreSQL for user account storage, and a Gemini-powered AI assistant to help users understand their predictions.

 🎯 Objectives

- Predict estimated medical insurance costs using machine learning.
- Analyze how customer characteristics relate to insurance charges.
- Provide a simple and interactive user interface.
- Integrate a backend API for prediction requests.
- Store user account information using Neon PostgreSQL.
- Provide AI-powered explanations through a Gemini-based assistant.

 ✨ Features

- **Insurance Cost Prediction:** Estimates insurance charges using a trained machine learning model.
- **Interactive Dashboard:** Allows users to enter personal and demographic information.
- **REST API:** Uses FastAPI to handle prediction requests.
- **AI Assistant:** Integrates the Gemini API to answer questions about predictions.
- **User Accounts:** Uses Neon PostgreSQL for account storage.
- **Model Optimization:** Applies machine learning techniques and hyperparameter tuning to improve predictive performance.
- **Containerization Support:** Includes a Dockerfile for container-based deployment.

 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas and NumPy | Data processing |
| Scikit-learn | Data preprocessing and machine learning |
| CatBoost and other ML libraries | Model development and experimentation |
| FastAPI | Backend API |
| Streamlit | Frontend and interactive dashboard |
| Neon PostgreSQL | Database for user accounts |
| Google Gemini API | AI-powered assistant |
| Joblib/Pickle | Model serialization |
| Docker | Containerization |
| Git and GitHub | Version control and source code hosting |

📊 Dataset

The project uses a medical insurance dataset containing customer information and corresponding insurance charges.

The input features include:

- Age
- BMI (Body Mass Index)
- Gender
- Smoking status
- Number of children
- Region

The target variable is `charges`, representing the insurance cost recorded in the dataset.

The dataset is used to train and evaluate machine learning models for estimating insurance charges.

 ⚙️ Machine Learning Workflow

1. Data collection and exploration.
2. Data cleaning and preprocessing.
3. Feature engineering.
4. Categorical feature encoding and numerical feature scaling.
5. Training and evaluating multiple machine learning models.
6. Hyperparameter tuning.
7. Selecting the final trained model.
8. Integrating the model into the FastAPI backend.
9. Displaying predictions through the Streamlit frontend.

 🏗️ System Architecture

The application follows a frontend-backend architecture:

1. **Streamlit Frontend:** Collects user inputs and displays the predicted insurance cost.
2. **FastAPI Backend:** Receives prediction requests and processes the input data.
3. **Machine Learning Model:** Generates an estimated insurance cost.
4. **Neon PostgreSQL:** Stores user account information.
5. **Gemini AI Assistant:** Provides explanations and answers questions related to the prediction.

 🚀 Installation and Setup

 Prerequisites

- Python 3.10 or another Python version compatible with your project dependencies
- Git
- A Google Gemini API key
- A Neon PostgreSQL database, if using the account features

 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Medical_Insurance_Cost_Prediction
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

 3. Install Dependencies

```bash
pip install -r requirements.txt
```

 4. Configure Environment Variables

Configure the required API keys and database connection settings using environment variables.

For local development, you may create a `.env` file if your application supports it.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_neon_postgresql_connection_string
```

Replace the example values with your actual credentials. Never commit your `.env` file or publish your secrets on GitHub.

 5. Run the FastAPI Backend

Use the actual filename containing your FastAPI application.

For example, if the file is `main.py` and the FastAPI instance is named `app`, run:

```bash
uvicorn main:app --reload
```

The API will typically be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

 6. Run the Streamlit Frontend

Open another terminal, activate your virtual environment, and run:

```bash
streamlit run frontend_redesigned.py
```

Streamlit will display a local URL where you can access the application.

**Note:** The backend startup command depends on your actual FastAPI filename and application variable. Update the command if your project uses different names.

 🔐 Security

- Keep API keys and database credentials private.
- Store production secrets in your hosting platform's environment settings.
- Never upload `.env` files.
- Use secure password handling and appropriate database access controls.
- Avoid storing sensitive personal information unnecessarily.

 📈 Model Evaluation

Machine learning models are evaluated using regression metrics such as:

- **R² Score:** Measures how well the model explains variation in insurance charges.
- **Mean Absolute Error (MAE):** Measures the average absolute prediction error.
- **Root Mean Squared Error (RMSE):** Measures prediction error while penalizing larger errors more heavily.

Actual model performance depends on the trained model and evaluation dataset.

 ☁️ Deployment

The application can be deployed using separate hosting services:

- **Frontend:** Streamlit Community Cloud or another compatible hosting platform.
- **Backend:** Render or another platform supporting FastAPI.
- **Database:** Neon PostgreSQL.
- **AI Assistant:** Google Gemini API.

For successful deployment, configure environment variables, dependencies, model files, and the frontend's backend API URL appropriately.

 ⚠️ Disclaimer

This application provides machine learning-based estimates using patterns learned from historical data. Predictions are illustrative estimates and may differ from actual insurance premiums. They should not be considered official insurance quotations, financial guarantees, or medical advice.

👨‍💻 Author

**Divy Jain**

AI/ML Project — Medical Insurance Cost Prediction

Linkdin - www.linkedin.com/in/divyjain24

📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

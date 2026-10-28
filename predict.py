import pickle
import pandas as pd

#import the ml model
with open('model/model.pkl','rb') as f:
    model = pickle.load(f)

# here we have generated model_version manually but in reality we have to extract it with the help of MLflow.
MODEL_VERSION = '2.1.2'


def predict_output(user_input: dict):

    df = pd.DataFrame([user_input])

    prediction = model.predict(df)[0]

    return {
        "predicted_premium": round(float(prediction), 2)
    }
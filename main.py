import joblib
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import datetime
import uvicorn

model = joblib.load("model.pkl")
ml_columns = joblib.load("columns.pkl")

app = FastAPI(title="jmodel")

class PredictionRequest(BaseModel):
    date: str
    productName: str
    priceInr: float
    marketingSpendInr: float
    eventType: str

# 3. Product Lookup Dictionary (To automatically find Brand and Category)
product_database = {
    "Clinic Plus Strong & Long (650ml)": {"brand": "Clinic Plus", "category": "General"},
    "Clinic Plus Strong & Long (340ml)": {"brand": "Clinic Plus", "category": "General"},
    "Clinic Plus Egg Protein (340ml)": {"brand": "Clinic Plus", "category": "General"},
    "Clinic Plus Ayurveda (340ml)": {"brand": "Clinic Plus", "category": "Herbal"},
    "Clinic Plus Almond Gold (175ml)": {"brand": "Clinic Plus", "category": "General"},
    "H&S Cool Menthol (650ml)": {"brand": "Head & Shoulders", "category": "Summer"},
    "H&S Smooth & Silky (340ml)": {"brand": "Head & Shoulders", "category": "Beauty"},
    "H&S Anti-Hairfall (340ml)": {"brand": "Head & Shoulders", "category": "Monsoon"},
    "H&S Lemon Fresh (180ml)": {"brand": "Head & Shoulders", "category": "Summer"},
    "H&S Neem (180ml)": {"brand": "Head & Shoulders", "category": "Herbal"}
}

@app.get("/")
def root():
    return {
        "status": "Backend running 🚀",
        "docs": "/docs",
        "predict": "/predict"
    }

@app.post("/predict")
def predict_demand(data: PredictionRequest):
    # A. Create an empty row with all 29 encoded columns set to 0
    input_data = {col: 0 for col in ml_columns}
    
    # B. Fill in the raw numbers
    input_data['Price_INR'] = data.priceInr
    input_data['Marketing_Spend_INR'] = data.marketingSpendInr
    
    # C. Extract Date Integers
    date_obj = datetime.strptime(data.date, '%Y-%m-%d')
    input_data['Year'] = date_obj.year
    input_data['Month'] = date_obj.month
    input_data['Day'] = date_obj.day
    input_data['DayofWeek'] = date_obj.weekday()
    
    # D. Get Brand and Category from our dictionary
    brand = product_database[data.productName]['brand']
    category = product_database[data.productName]['category']
    
    # E. Apply One-Hot Encoding (Change specific 0s to 1s)
    # The 'if' statements ensure we don't crash if a column name has a slight typo
    if f"Product_Name_{data.productName}" in input_data:
        input_data[f"Product_Name_{data.productName}"] = 1
        
    if f"Brand_{brand}" in input_data:
        input_data[f"Brand_{brand}"] = 1
        
    if f"Category_Type_{category}" in input_data:
        input_data[f"Category_Type_{category}"] = 1
        
    if f"Event_Type_{data.eventType}" in input_data:
        input_data[f"Event_Type_{data.eventType}"] = 1
        
    # F. Convert to DataFrame (so it perfectly matches the shape of x_train)
    df_input = pd.DataFrame([input_data])
    
    # G. Make the Prediction!
    prediction = model.predict(df_input)[0]
    
    # Return the result as a JSON response
    return {
        "product": data.productName,
        "predicted_units_sold": int(prediction)
    }
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib


df = pd.read_csv("indian_shampoo_sales_data.csv")

# print(df.head())
# print(df.info())
# print(df.describe())

df['Date'] = pd.to_datetime(df['Date'])

df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayofWeek'] = df['Date'].dt.dayofweek

df = df.drop(columns=['Date'])

# print(df['Product_Name'].unique())

# product_map = {
#     'Clinic Plus Strong & Long (650ml)': 0, 'Clinic Plus Strong & Long (340ml)': 1, 'Clinic Plus Egg Protein (340ml)': 2, 'Clinic Plus Ayurveda (340ml)': 3, 'Clinic Plus Almond Gold (175ml)': 4, 'H&S Cool Menthol (650ml)': 5, 'H&S Smooth & Silky (340ml)': 6, 'H&S Anti-Hairfall (340ml)': 7, 'H&S Lemon Fresh (180ml)': 8, 'H&S Neem (180ml)': 9
# }

# df['Product_Name'] = df['Product_Name'].map(product_map)

columns_encode = ["Product_Name", "Brand", "Category_Type", "Event_Type"]

df = pd.get_dummies(df, columns=columns_encode, dtype=int)

# print(df.head())
# print(df.info())
# df.to_csv('updata.csv')

y = df['Units_Sold']

x = df.drop(columns=['Units_Sold'])

x_train, x_test, y_train, y_test = train_test_split(x,y,random_state=42, test_size=0.2)

model = RandomForestRegressor()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

print("R2", r2_score(y_test, y_pred))
print("MAE", mean_absolute_error(y_test, y_pred))

y_train_pred = model.predict(x_train)
print("Train r2", r2_score(y_train, y_train_pred))

print("Test r2", r2_score(y_test, y_pred))

joblib.dump(model, "model.pkl")
joblib.dump(list(x.columns), "columns.pkl")
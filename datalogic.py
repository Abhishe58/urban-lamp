import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
days = 730  # 2 Years of data (Jan 2024 - Dec 2025)
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=x) for x in range(days)]

# --- 2. PRODUCT CATALOG (Real World Products) ---
products = [
    # Brand 1: Clinic Plus (Mass Market - High Volume, Lower Price)
    {"name": "Clinic Plus Strong & Long (650ml)", "brand": "Clinic Plus", "type": "General", "base_price": 380, "base_demand": 150},
    {"name": "Clinic Plus Strong & Long (340ml)", "brand": "Clinic Plus", "type": "General", "base_price": 220, "base_demand": 200},
    {"name": "Clinic Plus Egg Protein (340ml)",   "brand": "Clinic Plus", "type": "General", "base_price": 230, "base_demand": 120},
    {"name": "Clinic Plus Ayurveda (340ml)",      "brand": "Clinic Plus", "type": "Herbal",  "base_price": 240, "base_demand": 100},
    {"name": "Clinic Plus Almond Gold (175ml)",    "brand": "Clinic Plus", "type": "General", "base_price": 110, "base_demand": 250},

    # Brand 2: Head & Shoulders (Premium/Functional - Specific Seasons)
    {"name": "H&S Cool Menthol (650ml)",           "brand": "Head & Shoulders", "type": "Summer", "base_price": 550, "base_demand": 80},
    {"name": "H&S Smooth & Silky (340ml)",         "brand": "Head & Shoulders", "type": "Beauty", "base_price": 310, "base_demand": 110},
    {"name": "H&S Anti-Hairfall (340ml)",          "brand": "Head & Shoulders", "type": "Monsoon", "base_price": 310, "base_demand": 90},
    {"name": "H&S Lemon Fresh (180ml)",            "brand": "Head & Shoulders", "type": "Summer", "base_price": 190, "base_demand": 130},
    {"name": "H&S Neem (180ml)",                   "brand": "Head & Shoulders", "type": "Herbal", "base_price": 185, "base_demand": 100},
]

all_data = []

# --- 3. HELPER FUNCTIONS FOR INDIAN CONTEXT ---

def get_indian_event_factor(date):
    """
    Returns (Event_Name, Demand_Multiplier, Is_Sale_Event)
    """
    m, d = date.month, date.day
    
    # National Sales (E-commerce "Big Billion" Days)
    # Republic Day (Jan 26), Independence Day (Aug 15), Gandhi Jayanti (Oct 2)
    if (m == 1 and d in [24, 25, 26]) or (m == 8 and d in [13, 14, 15]) or (m == 10 and d in [1, 2, 3]):
        return "National Sale", 2.5, True
        
    # Festivals (Approximate dates for logic)
    if (m == 3 and d == 25): return "Holi", 1.2, False  # Post-Holi wash
    if (m == 8 and d == 19): return "Raksha Bandhan", 1.3, False # Gifting
    if (m == 10 and d in [29, 30, 31]) or (m == 11 and d in [1]): return "Diwali", 1.5, True # Cleaning/Stocking
    
    # Wedding Season (Nov-Feb, May-June) - People want "Silky/Shiny" hair
    if m in [11, 12, 1, 2, 5, 6]:
        return "Wedding Season", 1.15, False

    return "Normal Day", 1.0, False

def get_seasonal_factor(date, product_type):
    """
    Adjusts demand based on product type and weather season in India.
    """
    m = date.month
    
    # SUMMER (Mar - Jun): High sweat, high demand for Menthol/Lemon
    if m in [3, 4, 5, 6]:
        if product_type == "Summer": return 1.6  # Huge spike for Cool Menthol
        if product_type == "General": return 1.1 # People shower more often
        return 1.0
        
    # MONSOON (Jul - Sep): Humidity, Frizz, Hairfall
    if m in [7, 8, 9]:
        if product_type == "Monsoon": return 1.5 # Anti-Hairfall spikes
        if product_type == "Beauty": return 0.9  # Frizz makes people unhappy with silk shampoos
        return 1.0
        
    # WINTER (Oct - Feb): Dry scalp, Dandruff
    if m in [10, 11, 12, 1, 2]:
        if product_type == "Summer": return 0.4  # No one buys Menthol in winter!
        if product_type == "Beauty": return 1.2  # Party/Wedding season styling
        if product_type == "Herbal": return 1.1  # Skin/Scalp care
        return 1.0
        
    return 1.0

# --- 4. GENERATION LOOP ---

print("Generating Data... Please wait.")

for prod in products:
    for date in dates:
        # A. Get Factors
        event_name, event_multiplier, is_sale = get_indian_event_factor(date)
        seasonal_multiplier = get_seasonal_factor(date, prod['type'])
        
        # B. Marketing & Price Logic
        # Companies spend huge ads during Sales & Cricket World Cup (simulated random)
        marketing_spend = np.random.randint(1000, 5000) 
        
        current_price = prod['base_price']
        
        # Discount Logic during Sales
        if is_sale:
            current_price = int(prod['base_price'] * 0.85) # 15% Off
            marketing_spend *= 2 # Double ad spend
        elif event_name == "Wedding Season" and prod['type'] == "Beauty":
            marketing_spend *= 1.5 # Push ads for silky hair
            
        # C. Calculate Sales
        # Formula: Base * (Event + Season) + (Marketing Impact)
        
        # Marketing Impact is lower for mass products (Clinic Plus) than premium (H&S)
        marketing_impact = (marketing_spend / 2000) if prod['brand'] == "Clinic Plus" else (marketing_spend / 800)
        
        base_calc = prod['base_demand'] * (event_multiplier * seasonal_multiplier)
        
        final_sales = base_calc + marketing_impact
        
        # D. Weekend Logic (Sunday Grocery Run)
        if date.weekday() == 6: # Sunday
            final_sales *= 1.25
        elif date.weekday() == 5: # Saturday
            final_sales *= 1.15
            
        # E. Random Noise (Real life variance)
        noise = np.random.normal(0, 10) # Bell curve noise
        final_sales = max(0, int(final_sales + noise))
        
        # Add to list
        all_data.append([
            date.strftime('%Y-%m-%d'),
            prod['name'],
            prod['brand'],
            prod['type'],
            current_price,
            marketing_spend,
            event_name,
            final_sales
        ])

# --- 5. SAVE TO CSV ---
df = pd.DataFrame(all_data, columns=['Date', 'Product_Name', 'Brand', 'Category_Type', 'Price_INR', 'Marketing_Spend_INR', 'Event_Type', 'Units_Sold'])
df.to_csv('indian_shampoo_sales_data.csv', index=False)

print("Success! Data Generated: 'indian_shampoo_sales_data.csv'")
print("\n--- SAMPLE DATA ---")
print(df.sample(5).to_string())

print("\n--- INSIGHT: Summer Impact on 'Cool Menthol' ---")
summer_sales = df[(df['Product_Name'].str.contains("Cool Menthol")) & (df['Event_Type'] == "Normal Day")]
print(summer_sales.groupby(df['Date'].str[5:7])['Units_Sold'].mean().head(6)) # Show Jan-Jun averages
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def fetch_weather_today(city_name="Berlin"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric&lang=ua"
    response = requests.get(url).json()
    return response

def fetch_weather_forecast(city_name="Berlin"):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric&lang=ua"
    response = requests.get(url).json()
    return response

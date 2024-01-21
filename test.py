import requests
import json

# Set up the API endpoint and parameters
url = "https://maps.googleapis.com/maps/api/building/insights/v3/shadows"
params = {
    "location": "37.7749,-122.4194", # latitude, longitude of the building
    "projection": "MAXIMUM_SHADOW_AREA",
    "shadowType": "SOLAR_PANEL",
    "key": "AIzaSyDu9WmzWfQnxsqJhWLE8CTMlSYB0VRUrkg"
}

# Make the API request
response = requests.get(url, params=params)
data = response.json()

# Extract the solar radiation data
solar_radiation = data["result"]["solarRadiation"]
print("Annual solar radiation:", solar_radiation, "kWh/kW/year")
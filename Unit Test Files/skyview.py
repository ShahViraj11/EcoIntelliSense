import requests
import apikeys

# Replace YOUR_API_KEY with your actual API key
api_key = apikeys.google_maps_api_key

# Specify the API endpoint and parameters
endpoint = "https://aerialview.googleapis.com/v1/videos:lookupVideo"
address = "600 Montgomery St, San Francisco, CA 94111"

# Create the request URL
url = f"{endpoint}?key={api_key}&address={address}"

# Make the GET request
response = requests.get(url)

# Check the status code and print the response content
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")

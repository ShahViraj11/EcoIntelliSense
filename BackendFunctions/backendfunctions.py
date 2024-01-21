import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import apikeys

def check_mountainous_region(api_key, latitude, longitude):
    """Checks if a region is mountainous based on elevation data."""
    
    endpoint = "https://maps.googleapis.com/maps/api/elevation/json"
    params = {
        'locations': f'{latitude},{longitude}',
        'key': api_key,
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    if response.status_code == 200 and 'results' in data:
        return data['results'][0]['elevation']
    else:
        return None


def get_solar_insights(api_key, latitude, longitude):
    endpoint = f"https://solar.googleapis.com/v1/buildingInsights:findClosest?location.latitude={latitude}&location.longitude={longitude}&requiredQuality=HIGH&key={api_key}"

    response = requests.get(endpoint)
    # https://developers.google.com/maps/documentation/solar/building-insights#example_response_object
    data = response.json()

    return data


def pollution_data(api, latitude, longitude):  
    startTime = (datetime.now() - timedelta(days=15)).isoformat() 
    endTime = (datetime.now() - timedelta(days=1)).isoformat()
    
    result = list()  
    
    url = f'https://airquality.googleapis.com/v1/history:lookup?key={api}'
    data = {
        "period": {
            "startTime": str(startTime) + "Z",
            "endTime": str(endTime) + "Z"
        },
        "pageSize": 99999,
        "pageToken": "",
        "location": {
            "latitude": latitude,
            "longitude": longitude
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=data, headers=headers)
    
    
    while('nextPageToken' in response.json() and response.json()['nextPageToken'] != ''):
        data['pageToken'] = response.json()['nextPageToken']
        response = requests.post(url, json=data, headers=headers)
        result.append(response.json())
    
    return result

def water_check(original_lat, original_lon):
   
    cardinal_directions = list()
    
    for i in [-1,1]:
        new_lat = original_lat + (i / 69)
        new_lon = original_lon + (0 / (69 * abs(original_lat)))
        cardinal_directions.append((new_lat, new_lon))
        
    for i in [-100,100]:
        new_lat = original_lat + (0 / 69)
        new_lon = original_lon + (i / (69 * abs(original_lat)))
        cardinal_directions.append((new_lat, new_lon))

    water_check = False

    m = Basemap(projection='cyl')

    m.drawcoastlines()
    m.fillcontinents(color='lightgray')
    m.drawmapboundary(fill_color='lightblue')

    for i in cardinal_directions:
        lat = i[0]
        lon = i[1]
        is_land = m.is_land(lon, lat)
        if is_land != True:
            water_check = True
        x, y = m(lon, lat)
        m.plot(x, y, 'ro', markersize=10)

    plt.title("Map with Coordinate")
    plt.show()

    return water_check

    
def geocode_address(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': api_key
    }

    response = requests.get(base_url, params=params)
    result = response.json()

    if result['status'] == 'OK':
        location = result['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        print(f"Geocoding failed. Status: {result['status']}")
        return None




'''
latitude = 37.7749
longitude = -122.4194
api_key = apikeys.google_maps_api_key


address_to_geocode = "1600 Amphitheatre Parkway, Mountain View, CA"
coordinates = geocode_address(address_to_geocode, api_key)
print(f"Coordinates for {address_to_geocode}: {coordinates}")
'''

'''
elevation = check_mountainous_region(api_key, latitude, longitude)
print(f"Elevation: {elevation} meters")

solar_data = get_solar_insights(api_key, latitude, longitude)
print(solar_data)

pollution_data = pollution_data(api_key, latitude, longitude)
print(pollution_data)
'''




import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

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
        elevation = data['results'][0]['elevation']
        return elevation  # Return only the elevation value
    else:
        return None  # Return None to indicate error or missing data

def get_solar_insights(api_key, latitude, longitude):
    endpoint = f"https://solar.googleapis.com/v1/buildingInsights:findClosest?location.latitude={latitude}&location.longitude={longitude}&requiredQuality=HIGH&key={api_key}"

    response = requests.get(endpoint)
    # https://developers.google.com/maps/documentation/solar/building-insights#example_response_object
    data = response.json()

    solar_analysis_data = {}

    # Solar Potential
    solar_analysis_data['max_sunshine_hours_per_year'] = data['solarPotential']['maxSunshineHoursPerYear']
    solar_analysis_data['solar_panel_configs'] = data['solarPotential']['solarPanelConfigs']

    # Roof and Building Statistics
    solar_analysis_data['whole_roof_stats'] = data['solarPotential']['wholeRoofStats']
    solar_analysis_data['building_stats'] = data['solarPotential']['buildingStats']

    # Solar Panel Information
    solar_analysis_data['panel_capacity_watts'] = data['panelCapacityWatts']
    solar_analysis_data['panel_dimensions'] = {'height_meters': data['panelHeightMeters'], 'width_meters': data['panelWidthMeters']}
    solar_analysis_data['panel_lifetime_years'] = data['panelLifetimeYears']

    # Financial Analyses
    solar_analysis_data['financial_analyses'] = data['financialAnalyses']

    # Geographical Information
    solar_analysis_data['center_coordinates'] = data['center']

    # Imagery Information
    solar_analysis_data['imagery_quality'] = data['imageryQuality']
    solar_analysis_data['imagery_processed_date'] = data['imageryProcessedDate']

    return solar_analysis_data


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

    





latitude = 37.7749
longitude = -122.4194
api_key = ''

'''
elevation = check_mountainous_region(api_key, latitude, longitude)
print(f"Elevation: {elevation} meters")

solar_data = get_solar_insights(api_key, latitude, longitude)
print(solar_data)

pollution_data = pollution_data(api_key, latitude, longitude)
print(pollution_data)
'''




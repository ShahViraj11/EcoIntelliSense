import requests
from datetime import datetime, timedelta
import pytz
from mpl_toolkits.basemap import Basemap
import pysolar


google_maps_api_key = 'AIzaSyDu9WmzWfQnxsqJhWLE8CTMlSYB0VRUrkg'
redis_password = 'EgORtEAym4obVur32FdT5qnBwi6QKAsK'
autho_domain = 'dev-oye6y425565bfb2p.us.auth0.com'
autho_client_id = 'JOsSt09A4sbeFTqq1U6DVIw6eRdyDbIp'
autho_client_secret = '3ONItRFS8Wf9w_w2_Nzu2H5zGNWelMz6E9ci1v_zw-srCFgbOcobWP_l8GGoEA26'
onebuild_api = '1build_ext.zo7ujfZa.e4ttcYOIKFi6Sy7t2FBLQy0F7L0ZrKrU'



def average_temp_and_wind(lat,lon,start_month= datetime.now().month,end_month=datetime.now().month):
    current_year = datetime.now()
    current_year = current_year.year - 1

    start_year = current_year - 1 if start_month > end_month else current_year
    end_year = current_year if start_month <= end_month else current_year + 1

    start_month = f'{start_month:02d}'
    end_month = f'{end_month:02d}'

    start_date = f'{start_year}-{start_month}-01'
    end_date = f'{end_year}-{end_month}-31'

    url = (f'https://archive-api.open-meteo.com/v1/era5?'
    f'latitude={lat}&longitude={lon}&'
    f'start_date={start_date}&end_date={end_date}&'
    f'hourly=temperature_2m,wind_speed_10m')

    response = requests.get(url)
    data = response.json()

    temp_data = data['hourly']['temperature_2m']
    average_temp = sum(temp_data)/len(temp_data)

    wind_data = data['hourly']['wind_speed_10m']
    average_wind_speed = sum(wind_data)/len(wind_data)

    return average_temp,average_wind_speed

def query_1build_construction_costs(lat,lng,api_key = onebuild_api):
    url = "https://gateway-external.1build.com/"
    headers = {
        "Content-Type": "application/json",
        "1build-api-key": api_key
    }

    queries = {
        "labor": {
            "searchTerm": "construction labor",
            "fields": "name burdenedLaborRateUsdCents"
        },
        "concrete": {
            "searchTerm": "concrete",
            "fields": "name materialRateUsdCents"
        },
        "site_preparation": {
            "searchTerm": "site preparation",
            "fields": "name calculatedUnitRateUsdCents"
        },
        "finishing_materials": {
            "searchTerm": "finishing materials",
            "fields": "name calculatedUnitRateUsdCents"
        }
    }

    results = {}

    for key, value in queries.items():
        graphql_query = """
        query sources($input: SourceSearchInput!) {
            sources(input: $input) {
                nodes {
                    %s
                }
            }
        }
        """ % value["fields"]

        variables = {
            "input": {
                "coordinate": {"lng": lng, "lat": lat},
                "searchTerm": value["searchTerm"],
                "page": {"limit": 3}
            }
        }

        response = requests.post(url, headers=headers, json={"query": graphql_query, "variables": variables})

        total_cost_cents = 0

        if response.status_code == 200:
            nodes = response.json()['data']['sources']['nodes']

            for node in nodes:
                if 'burdenedLaborRateUsdCents' in node:
                    total_cost_cents += node['burdenedLaborRateUsdCents']
                    uom = "$ per Hour"
                elif 'materialRateUsdCents' in node:
                    total_cost_cents += node['materialRateUsdCents']
                    uom = "$ per Cubic Yard"
                    break
                elif 'calculatedUnitRateUsdCents' in node:
                    total_cost_cents += node['calculatedUnitRateUsdCents']
                    uom = "$ per Square Foot"

            if total_cost_cents == 0:
                continue
            results[key] = str(total_cost_cents / 100) + uom  # Convert to dollars
        else:
            results[key] = f"Error: {response.status_code}, {response.text}"

    return results

def check_mountainous_region(latitude, longitude, api_key=google_maps_api_key):
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


def get_solar_insights(latitude, longitude,api=google_maps_api_key):
    endpoint = f"https://solar.googleapis.com/v1/buildingInsights:findClosest?location.latitude={latitude}&location.longitude={longitude}&requiredQuality=HIGH&key={api}"

    response = requests.get(endpoint)
    # https://developers.google.com/maps/documentation/solar/building-insights#example_response_object
    data = response.json()

    return data

def solar_data(lat, lon, area=6):
    start = datetime(20, 1, 1, 8, 0, 0, 0, tzinfo=pytz.utc)

    monthly_averages = [0] * 12
    monthly_counts = [0] * 12

    for i in range(0, 365 * 24, 1):
        date = start + timedelta(hours=-i)
        month = date.month - 1  # Adjust month to be 0-indexed
        altitude_deg = pysolar.solar.get_altitude(lat, lon, date)
        
        if altitude_deg > 0:
            radiation = (area * pysolar.radiation.get_radiation_direct(date, altitude_deg) / 1000) * 72
            monthly_averages[month] += radiation
            monthly_counts[month] += 1

    monthly_averages = [avg / count if count > 0 else 0 for avg, count in zip(monthly_averages, monthly_counts)]
    
    return monthly_averages

def pollution_data(latitude, longitude,api=google_maps_api_key):  
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


    return water_check

    
def geocode_address(address, api_key=google_maps_api_key):
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

def sustainability_score(latitude,longitude):
    data = dict()
    data['solar'] = True

    data['water_check'] = water_check(latitude, longitude)
    
    pollution_list = pollution_data(latitude, longitude)
    sum = 0
    for i in range(len(pollution_list)):
        sum += pollution_list[i]['hoursInfo'][0]['indexes'][0]['aqi']

    data['pollution'] = sum/len(pollution_list)

    
    score = 75
    if data['solar']:
        score += 25

    if data['water_check']:
        score -= 15

    pollution_num = 50
    while data['pollution'] > pollution_num:
        score -= 2
        pollution_num += 30
    
    return score



'''
address_to_geocode = "1600 Amphitheatre Parkway, Mountain View, CA"
coordinates = geocode_address(address_to_geocode, api_key)
print(f"Coordinates for {address_to_geocode}: {coordinates}")

#pollution_data[0]['hoursInfo'][0]['indexes'][0]['dominantPollutant']
pollution_data = pollution_data(latitude, longitude)
sum = 0
for i in range(len(pollution_data)):
    sum += pollution_data[i]['hoursInfo'][0]['indexes'][0]['aqi']

print(sum/len(pollution_data))

elevation = check_mountainous_region(api_key, latitude, longitude)
print(f"Elevation: {elevation} meters")

'''

print(average_temp_and_wind(40.7128, -74.0060))
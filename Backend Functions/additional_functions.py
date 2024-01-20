import requests
import datetime

def average_temp_and_wind(lat,lon,start_month,end_month):
    current_year = datetime.datetime.now()
    current_year = current_year.year - 1

    start_year = current_year - 1 if start_month > end_month else current_year
    end_year = current_year if start_month <= end_month else current_year + 1

    # Define the start and end dates in the format 'YYYY-MM-DD'
    start_month = f'{start_month:02d}'
    end_month = f'{end_month:02d}'

    start_date = f'{start_year}-{start_month}-01'
    end_date = f'{end_year}-{end_month}-31'

    # Construct the URL with the calculated dates and location
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

def query_1build_construction_costs(api_key,lat,lng):
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

print(query_1build_construction_costs('1build_ext.zo7ujfZa.e4ttcYOIKFi6Sy7t2FBLQy0F7L0ZrKrU',42.73,-84.48))

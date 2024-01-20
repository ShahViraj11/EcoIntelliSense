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

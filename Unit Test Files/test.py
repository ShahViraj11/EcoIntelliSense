import datetime
import pysolar

# define the location (Beijing, China)

def solar_data(lat,lon):
    start = datetime.datetime(2018, 1, 1, 8, 0, 0, 0, tzinfo=datetime.timezone.utc)

    solar_data = []
    for i in range(0, 6*90, 1):
        date = start + datetime.timedelta(hours=-i)
        altitude_deg = pysolar.solar.get_altitude(lat, lon, date)
        if altitude_deg <= 0:
            radiation = 0.
        else:
            radiation = pysolar.radiation.get_radiation_direct(date, altitude_deg)
        solar_data.append(radiation)
    return solar_data

print(solar_data(40.7128, -74.0060))
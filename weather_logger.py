import time
import os

import requests  # pip install requests
from dotenv import load_dotenv  # pip install python-dotenv
from influxdb import InfluxDBClient  # pip install influxdb


class IFDB(object):
    """Wrapper class for uploading data points to InfluxDB
    Requires set up database and a user with all privileges.
    The database should have two measurements for current weather
    and forecast"""

    @classmethod
    def create_client(cls):
        USER = os.getenv('INFLUX_USER')
        PASS = os.getenv('INFLUX_PASSWORD')
        DATABASE = os.getenv('INFLUX_DATABASE')
        cls.client = InfluxDBClient(
            username=USER,
            password=PASS,
            database=DATABASE)

    def __init__(self, measurement):
        self.measurement = measurement

    def add_points(self, time_data_list):
        """This weird solution for passing data happens because
        current weather is just a datapoint (with a lot of information in it)
        wheras forecast is multiple of such points passed in a list
        This could be probably handled better but it works so..."""

        for element in time_data_list:
            body = [{
                "measurement": self.measurement,
                "time": element[0],  # epoch in ns format
                "fields": element[1]}]  # data dictionary

            self.client.write_points(body)
        self.client.close()


class OpenWeather(object):

    def __init__(self):
        self.now = dict()
        self.forecast = list()

        self.APPID = os.getenv('OPEN_WEATHER_APPID')
        self.LAT = os.getenv('LATITUDE')
        self.LON = os.getenv('LONGITUDE')

    def update(self):
        try:
            response = requests.get('https://api.openweathermap.org/data/2.5/'
                                    'onecall?'
                                    f'&lat={self.LAT}'
                                    f'&lon={self.LON}'
                                    '&units=metric'
                                    f'&APPID={self.APPID}')
            response.raise_for_status()  # That will raise an HTTPError
            self.package = response.json()
            return True

        except requests.exceptions.HTTPError as httperr:
            print(httperr)
            return False

        except requests.exceptions.RequestException:
            print('No connection to the Open Weather server')
            return False

    def pack_data(self):
        p = self.package

        self.now_dt = int(p['current']['dt'] * 1e9)

        self.now['latitude'] = float(p['lat'])
        self.now['longitude'] = float(p['lon'])

        self.now['temperature'] = float(p['current']['temp'])
        self.now['feels_like'] = float(p['current']['feels_like'])
        self.now['pressure'] = float(p['current']['pressure'])
        self.now['humidity'] = float(p['current']['humidity'])

        self.now['uvi'] = float(p['current']['uvi'])
        self.now['clouds'] = float(p['current']['clouds'])
        self.now['wind_speed'] = float(p['current']['wind_speed'])
        self.now['wind_angle'] = float(p['current']['wind_deg'])

        self.now['id'] = int(p['current']['weather'][0]['id'])
        self.now['category'] = p['current']['weather'][0]['main']
        self.now['description'] = p['current']['weather'][0]['description']
        self.now['icon'] = p['current']['weather'][0]['icon']

        self.now['temp_max'] = float(p['daily'][0]['temp']['max'])
        self.now['temp_min'] = float(p['daily'][0]['temp']['min'])

        for h in range(48):
            t = int(p['hourly'][h]['dt'] * 1e9)

            data_dict = {'temperature': float(p['hourly'][h]['temp']),
                         'pop': float(p['hourly'][h]['pop'])}

            self.forecast.append([t, data_dict])


if __name__ == '__main__':
    load_dotenv('.env')

    IFDB.create_client()
    db_weather = IFDB(os.getenv('MEASUREMENT_NOW'))
    db_forecast = IFDB(os.getenv('MEASUREMENT_FORECAST'))

    weather = OpenWeather()
    reference = time.time()

    while True:
        if weather.update():
            weather.pack_data()
            db_weather.add_points([[weather.now_dt, weather.now]])
            db_forecast.add_points(weather.forecast)
            print(
                "Point saved. "
                f"Now: {weather.now['temperature']} \u00B0"
                f"Feels like: {weather.now['feels_like']} \u00B0")
        time.sleep(600)

import pytz
import requests
import time
import logging
# from influxdb import InfluxDBClient


class IFDB(object):
    """This is a wrapper class for uploading data points to InfluxDB"""

    def __init__(self, measurement, username, password, database):
        self.timezone = pytz.timezone('Europe/Stockholm')
        self.measurement = measurement
        self.username = username
        self.password = password
        self.database = database

    def add_points(self, data):
        # self._connect()
        self._format_and_write(data)
        # self.client.close()

    # def _connect(self):
    #     self.client = InfluxDBClient(host="localhost",
    #                                  port=8086,
    #                                  username=self.username,
    #                                  password=self.password,
    #                                  database=self.database
    #                                  )

    def _format_and_write(self, data):
        """Formatting data for the upload. Uses "data" which is subclass
        of sensors class defined in main logger script"""
        body = [
                    {
                        "measurement": self.measurement,
                        "time": data.dt,
                        "fields": {
                            "longitude": data.longitude,
                            "latitude": data.latitude,
                            "weather_id": data.weather_id,
                            "weather_category": data.weather_category,
                            "weather_description": data.weather_description,
                            "weather_icon": data.weather_icon,
                            "temperature": data.temperature,
                            "feels_like": data.feels_like,
                            "temp_min": data.temp_min,
                            "temp_max": data.temp_max,
                            "pressure": data.pressure,
                            "humidity": data.humidity,
                            "wind_speed": data.wind_speed,
                            "wind_angle": data.wind_angle,
                            "clouds": data.clouds,
                            "location": data.location,
                            "uv_index": data.uvi
                        }
                    }
                ]

        # self.client.write_points(body)
        return body


class container(object):
    pass


class OpenWeather(object):

    def __init__(self):
        self.data = container()

    def update(self):
        r = requests.get('https://api.openweathermap.org/data/2.5/'
                         'weather?'
                         '&lat=59.36142886509909'
                         '&lon=18.008168552706497'
                         '&units=metric'
                         '&APPID=33f6aa60676a838926b064aca4cadbdd')
        if len(r.json()) < 5:
            raise Exception(f'Error! {r.json()["message"]}')
        self.pack = r.json()

    def pack_data(self):
        self.data.latitude = float(self.pack['lat'])
        self.data.longitude = float(self.pack['lon'])

        self.data.dt = int(self.pack['current']['dt'] * 1e9)
        self.data.temperature = float(self.pack['current']['temp'])
        self.data.feels_like = float(self.pack['current']['feels_like'])
        self.data.pressure = float(self.pack['current']['pressure'])
        self.data.humidity = float(self.pack['current']['humidity'])
        self.data.uvi = float(self.pack['current']['uvi'])
        self.data.clouds = float(self.pack['current']['clouds'])
        self.data.wind_speed = float(self.pack['current']['wind_speed'])
        self.data.wind_angle = float(self.pack['current']['wind_deg'])

        self.data.weather_id = int(self.pack['current']['weather'][0]['id'])
        self.data.weather_category = self.pack['current']['weather'][0]['main']
        self.data.weather_description = self.pack['current']['weather'][0]['description']
        self.data.weather_icon = self.pack['current']['weather'][0]['icon']

        self.data.temp_max = float(self.pack['daily'][0]['temp']['max'])
        self.data.temp_min = float(self.pack['daily'][0]['temp']['min'])

        for i in range(12):
            globals()['fig%s' % x] = 'values'

        # FIELDS is a dictionary!

        # d = {}
        # for x in range(1, 10):
        #     d["string{0}".format(x)] = "Hello"


        # Pop (hourly)


delay = 5
db = IFDB('weather', 'grafana', 'raspberrypi', 'overseer')
reference = time.time()
alldata = list()

while True:

    if (time.time() - reference) <= delay:
        pass
    else:
        weather = OpenWeather()
        weather.update()
        # weather.pack_data()
        # alldata.append(db._format_and_write(weather.data))
        # db.add_points(weather.data)
        reference = time.time()
        print('Point saved')

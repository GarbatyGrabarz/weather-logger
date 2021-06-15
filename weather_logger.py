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

    def add_points(self, time_data_list):
        # self._connect()
        for element in time_data_list:
            self._format_and_write(element[0], element[1])
        # self.client.close()

    # def _connect(self):
    #     self.client = InfluxDBClient(username=self.username,
    #                                  password=self.password,
    #                                  database=self.database)

    def _format_and_write(self, time, data_dict):
        """time must be in epoch in ns format, data_dict comtains names
        of fields and their values"""
        body = [{"measurement": self.measurement,
                 "time": time,
                 "fields": data_dict}]

        # self.client.write_points(body)
        return body


class OpenWeather(object):

    def __init__(self):
        self.now = dict()
        self.forcast = list()

    def update(self):
        response = requests.get('https://api.openweathermap.org/data/2.5/'
                                'weather?'
                                '&lat=59.36142886509909'
                                '&lon=18.008168552706497'
                                '&units=metric'
                                '&APPID=33f6aa60676a838926b064aca4cadbdd')
        if len(response.json()) < 5:
            raise Exception(f'Error! {response.json()["message"]}')
        self.package = response.json()

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

        # !!! Verify [0] always gives 'today'
        self.now['temp_max'] = float(p['daily'][0]['temp']['max'])
        self.now['temp_min'] = float(p['daily'][0]['temp']['min'])

        # !!!
        """ Check if the dt has fixed time and only date changes.
        In such a case every time i check I will update timestamps
        (database IDs) and only add a new point every hour. This way I can
        have values linked to time (easy for visualizations) """
        for h in range(48):

            t = int(p['hourly'][h]['dt'] * 1e9)

            data_dict = {'temperature': float(p['hourly'][h]['temp']),
                        'pop': float(p['hourly'][h]['pop'])}

            self.forcast.append([t, data_dict])


delay = 5
db = IFDB('weather', 'grafana', 'raspberrypi', 'overseer')
weather = OpenWeather()
reference = time.time()
alldata = list()  # TESTS ONLY
alldata2 = list()  # TESTS ONLY

while True:

    if (time.time() - reference) <= delay:
        pass
    else:
        weather.update()
        # weather.pack_data()
        # alldata.append(db._format_and_write(weather.now_dt, weather.now))  # TESTS ONLY
        # alldata2.append(db._format_and_write(weather.now_dt, weather.forcast))  # TESTS ONLY
        # db.add_points([weather.now_dt, weather.now])
        # db.add_points(weather.forcast)
        reference = time.time()
        print('Point saved')

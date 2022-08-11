# Introduction

This program was meant to run as a service first on Raspberry Pi, then on Ubuntu, to obtain weather data that later is visualized with [Grafana](https://grafana.com/). However, the program can be run as it is.
The data is obtained at 10 minutes intervals and only selected weather information is saved to a database (see requirements). Server call returns all the information, it's just that the program extracts what I was interested in.

# Requirements

*   Python libraries:

    *   [Requests](https://pypi.org/project/requests/)

    *   [dotenv](https://pypi.org/project/python-dotenv/)

    *   [InfluxDBClient](https://pypi.org/project/influxdb/)

*   The computer that is running the program must have installed and configured InfluxDB (time series database). That means creating a database and a user (with all privileges).

## InfluxDB configuration

I would be too lazy to search the internet for the config information so why should I assume you wouldn't? Here is a cheat sheet :D

Type in the terminal `influx` to start the program. Then type the lines below. Content of { } is of course up to you, you also skip the brackets. For example, the first line could be `create database my_database`

```plaintext
create database {db_name}
create user {user} with password '{password}' with all privileges
grant all privileges on {db_name} to {user}
```

# Configuration (a.k.a .env file)

Remember to either make a copy of .env file or create .gitignore and add it there. Otherwise, any update will clear the file. Generally .env should not be part of git but it's just too inconvienient to make a new file each time. It's easier to have it cloned with the code.

## Location

Latitude and longitude for the place of interest. You can be as precise as you want but the final "resolution" depends on your local weather info gathering system that works with OpenWeather. You can use Google Maps to get both values.

## API key

Register at OpenWeather and get them from [here](https://home.openweathermap.org/api_keys). IMPORTANT: Free API key has a restriction of how often the server can be called. This program uses "OneCall". Sampling of once per 10 minutes is more than enough but you should know what can be the reason if you do some heavy testing and the server stopped responding

## InfluxDB

Here you need to provide the name of the database, the user, and the password. The remaining two are measurements and they are created dynamically so whatever you type here should be OK. To avoid problems I suggest simply "now" and "forecast"

Should you decide the InfluxDB is on another machine you will need to add some lines in `create_client` method. Beside already existing `username`, `password`, and `database` you should include `host` and `port` (typically 8086)
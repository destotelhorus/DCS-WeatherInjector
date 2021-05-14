# DCS-WeatherInjector

# Not updated yet to work with 2.7 clouds!!

## Prerequisites
- Get an account on https://www.checkwx.com/ and an apikey.
- Enter apikey into config.properties
- Enter folders of your source and target MIZ-files into config.properties

## Setup
`python3 -m venv ./venv`  
`source ./venv/bin/activate`  
`pip install -r requirements.txt`

## Run
`python DCSWeatherInjector.py --help`

## Help
```
usage: DCSWeatherInjector.py [-h] [--weatherfile WEATHERFILE]
                              [--copy-weather-from-miz COPY_WEATHER_FROM_MIZ]
                              [--dont-update-time]
                              [missionfile]
 
 Injects weather into DCS missions.
 
 positional arguments:
   missionfile           mission file to inject into (default: all files in
                         directory specified in config.properties). Using this
                         will cause an in-place injection with the source file
                         overwritten
 
 optional arguments:
   -h, --help            show this help message and exit
   --weatherfile WEATHERFILE
                         file with weatherdata to use (default: use real
                         weather in theatre)
   --copy-weather-from-miz COPY_WEATHER_FROM_MIZ
                         copies weather from specified existing mission to the
                         target mission(s). Doesnt change time of mission!
   --dont-update-time    Do not update the mission file with current time
```

## What will it do
It will copy every `*.miz` (excluding `*.realweather.miz`) from the source directory into the target directory under the name `*.realweather.miz` and inject weather and time information into it.

If you do not want current time injected into your mission, add the string `.fixedtime.` to the filename (example: `My.cool.mission.fixedtime.miz`).

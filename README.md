# DCS-WeatherInjector

## Prerequisites
- Get an account on https://www.checkwx.com/ and an apikey.
- Enter apikey into config.properties
- Enter folders of your source and target MIZ-files into config.properties

## Setup
`python3 -m venv ./venv`  
`source ./venv/bin/activate`  
`pip install -r requirements.txt`

## Run
`python DCSWeatherInjector.py`

## What will it do
It will copy every `*.miz` (excluding `*.realweather.miz`) from the source directory into the target directory under the name `*.realweather.miz` and inject weather and time information into it.

If you do not want current time injected into your mission, add the string `.fixedtime.` to the filename (example: `My.cool.mission.fixedtime.miz`).

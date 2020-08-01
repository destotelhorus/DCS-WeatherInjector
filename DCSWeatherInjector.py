import os
from shutil import copyfile
from MIZFile import MIZFile
from CheckWX import CheckWX
from DCSCheckWXConvertEnricher import DCSCheckWXConvertEnricher
from DCSWeatherFileConverter import DCSWeatherFileConverter
import configparser
import argparse

parser = argparse.ArgumentParser(description='Injects weather into DCS missions.')
parser.add_argument('missionfile', help='mission file to inject into (default: all files in directory specified '
                                        'in config.properties). Using this will cause an in-place injection with '
                                        'the source file overwritten', default=argparse.SUPPRESS, nargs='?')
parser.add_argument('--weatherfile', help='file with weatherdata to use (default: use real weather in theatre)',
                    required=False)
parser.add_argument('--copy-weather-from-miz', help='copies weather from specified existing mission to the target '
                                                    'mission(s). Doesn''t change time of mission!', required=False)
parser.add_argument('--dont-update-time', help='Do not update the mission file with current time',
                    action='store_true', required=False)

args = parser.parse_args()

config = configparser.RawConfigParser()
config.read('config.properties')

missiondir = config.get('DCS', 'missiondir')
targetdir = config.get('DCS', 'targetdir')
WXDATAAPIKEY = config.get('CheckWX', 'apikey')

def MIZFilter(haystack):
    return [str for str in haystack
            if (str.endswith('.miz') and not str.endswith('.realweather.miz'))]

def process_mission(target, weatherdata = None):
    missionbasename = os.path.splitext(target)[0]
    MIZ = MIZFile(target, False)
    print('Date of mission:', MIZ.getDateTime())
    print('Theatre:', MIZ.getTheatre())
    if weatherdata == None:
        weatherprovider = CheckWX(WXDATAAPIKEY)
        weatherdata = DCSCheckWXConvertEnricher(weatherprovider.getWeatherForLatLon(MIZ.getTheatreLatLon()['lat'],
                                                                                    MIZ.getTheatreLatLon()['lon']))
    print('Weather for mission:', weatherdata.getWeatherText())
    print('Weather was cached:', weatherdata.getWeatherCached())
    if not '.fixedtime.' in missionbasename and not args.dont_update_time:
        MIZ.setDateTimeNow()
    print('Date of mission (new):', MIZ.getDateTime())
    weather = MIZ.getWeather()
    weather['atmosphere_type'] = 0 #Setting static weather
    weather['cyclones'] = []
    weather['season']['temperature'] = weatherdata.getTemperatureASL()
    windASL = weatherdata.getWindASL()
    wind2000 = weatherdata.getWind2000()
    wind8000 = weatherdata.getWind8000()
    weather['wind']['atGround']['speed'] = windASL['speed']
    weather['wind']['atGround']['dir'] = windASL['direction']
    weather['wind']['at2000']['speed'] = wind2000['speed']
    weather['wind']['at2000']['dir'] = wind2000['direction']
    weather['wind']['at8000']['speed'] = wind8000['speed']
    weather['wind']['at8000']['dir'] = wind8000['direction']
    weather['enable_fog'] = weatherdata.getFogEnabled()
    weather['qnh'] = weatherdata.getBarometerMMHg()
    weather['dust_density'] = 0
    weather['enable_dust'] = False
    weather['clouds']['density'] = weatherdata.getCloudDensity()
    weather['clouds']['thickness'] = weatherdata.getCloudThickness()
    weather['clouds']['base'] = weatherdata.getCloudBase()
    weather['clouds']['iprecptns'] = weatherdata.getWeatherType()
    weather['groundTurbulence'] = weatherdata.getGroundTurbulence()
    weather['type_weather'] = 0
    weather['fog']['thickness'] = weatherdata.getFogThickness()
    weather['fog']['visibility'] = weatherdata.getFogVisibility()
    weather['visibility']['distance'] = weatherdata.getVisibility()

    MIZ.setWeather(weather)
    MIZ.commit()
    print('Saved', target, 'successfully.')

def copy_weather(source, target):
    print('Copying weather from ', source,' to ', target, '.')
    TargetMIZ = MIZFile(target, False)
    SourceMIZ = MIZFile(source, True)
    TargetMIZ.setWeather(SourceMIZ.getWeather())
    TargetMIZ.commit()
    print('Saved', target, 'successfully.')

if __name__ == '__main__':
    if args.copy_weather_from_miz:
        if not hasattr(args, 'missionfile'):
            missions = MIZFilter(os.listdir(missiondir))

            print('Processing missions:', missions)
            for mission in missions:
                missionbasename = os.path.splitext(mission)[0]
                print('> ', mission)
                copyfile(missiondir+'/'+mission, targetdir+'/'+missionbasename+'.realweather.miz')
                copy_weather(args.copy_weather_from_miz, targetdir+'/'+missionbasename+'.realweather.miz')
        else:
            copy_weather(args.copy_weather_from_miz, args.missionfile)
    else:
        if not hasattr(args, 'missionfile'):
            missions = MIZFilter(os.listdir(missiondir))

            print('Processing missions:', missions)
            for mission in missions:
                missionbasename = os.path.splitext(mission)[0]
                print('> ', mission)
                copyfile(missiondir+'/'+mission, targetdir+'/'+missionbasename+'.realweather.miz')
                process_mission(targetdir+'/'+missionbasename+'.realweather.miz')
        else:
            weatherdata = DCSWeatherFileConverter(args.weatherfile)
            process_mission(args.missionfile, weatherdata)


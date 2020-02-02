import os
from shutil import copyfile
from MIZFile import MIZFile
from CheckWX import CheckWX
from DCSCheckWXConvertEnricher import DCSCheckWXConvertEnricher
import configparser

config = configparser.RawConfigParser()
config.read('config.properties')

missiondir = config.get('DCS', 'missiondir')
targetdir = config.get('DCS', 'targetdir')
WXDATAAPIKEY = config.get('CheckWX', 'apikey')

def MIZFilter(haystack):
    return [str for str in haystack
            if (str.endswith('.miz') and not str.endswith('.realweather.miz'))]


if __name__ == '__main__':
    missions = MIZFilter(os.listdir(missiondir))
    weatherprovider = CheckWX(WXDATAAPIKEY)

    print('Processing missions:', missions)
    for mission in missions:
        missionbasename = os.path.splitext(mission)[0]
        print('> ', mission)
        copyfile(missiondir+'/'+mission, targetdir+'/'+missionbasename+'.realweather.miz')
        MIZ = MIZFile(targetdir+'/'+missionbasename+'.realweather.miz', False)
        print('Date of mission:', MIZ.getDateTime())
        print('Theatre:', MIZ.getTheatre())
        weatherdata = DCSCheckWXConvertEnricher(weatherprovider.getWeatherForLatLon(MIZ.getTheatreLatLon()['lat'], MIZ.getTheatreLatLon()['lon']))
        print('Weather for mission:', weatherdata.getLastWeather().text)
        print('Weather was cached:', weatherdata.getLastWeather().from_cache)
        if not '.fixedtime.' in missionbasename:
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
        print('Saved', mission, 'successfully.')

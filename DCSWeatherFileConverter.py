import configparser
import random
import inspect

class DCSWeatherFileConverter(object):
    """
    Enrichment procedures are mostly based on dcs_weather from here https://forums.eagle.ru/showthread.php?t=198402.
    Some other things are new, deterministic randomness, temperature correction for sea level, etc.
    """
    weatherdata = None
    weatherfile = None

    def __init__(self, weatherfile):
        self.weatherfile = weatherfile
        self.weatherdata = configparser.RawConfigParser()
        self.weatherdata.read(weatherfile)

    def seedRandom(self):
        """
        Seeds the PRNG deterministically for repeatable same randoms
        :return: None
        """
        callingFunc = inspect.stack()[1].function
        random.seed(self.getWeatherText() + callingFunc)

    def getDeterministicRandomFloat(self, min, max):
        """
        Returns a deterministic random value for a given function calling it and the underlaying weather data.
        :param min: minimum float
        :param max: maximum float
        :return: float between min and max randomly chosen in a repeatable way
        """
        assert max >= min
        randval = random.random()
        return min + ((max-min)*randval)

    def getDeterministicRandomInt(self, min, max):
        """
        Returns a deterministic random value for a given function calling it and the underlaying weather data.
        :param min: minimum int
        :param max: maximum int
        :return: int between min and max randomly chosen in a repeatable way
        """
        return random.randint(min, max)

    def normalizeDegrees(self, angle):
        retangle = angle
        if retangle < 0:
            retangle += 360

        if retangle >= 360:
            retangle -= 360

        return retangle

    def getWeatherText(self):
        return 'weather from file: '+self.weatherfile

    def getWeatherCached(self):
        return False

    def getLastWeather(self):
        return None

    def getClosestResult(self):
        return None

    def getStationElevation(self):
        return self.weatherdata.getint('Weather', 'station_elevation')

    def getBarometerMMHg(self):
        return self.weatherdata.getfloat('Weather', 'barometer') * 25.4

    def getTemperature(self):
        return self.weatherdata.getfloat('Weather', 'temperature')

    def getTemperatureASL(self):
        """
        The higher the elevation of the reporting station, the higher the sea level temperature really is.
        This is using https://sciencing.com/tutorial-calculate-altitude-temperature-8788701.html as formula
        to adjust the temperature for sea level.
        :return: estimated temperature at sea level
        """
        temperatureDelta = self.getStationElevation() * 0.0065
        return self.getTemperature() + temperatureDelta

    def getWindASL(self):
        return {'direction': self.weatherdata.getint('Wind', 'asl_direction'),
                'speed': self.weatherdata.getfloat('Wind', 'asl_speed')}

    def getWind2000(self):
        return {'direction': self.weatherdata.getint('Wind', 'a2000_direction'),
                'speed': self.weatherdata.getfloat('Wind', 'a2000_speed')}

    def getWind8000(self):
        return {'direction': self.weatherdata.getint('Wind', 'a8000_direction'),
                'speed': self.weatherdata.getfloat('Wind', 'a8000_speed')}

    def getGroundTurbulence(self):
        return self.weatherdata.getfloat('Wind', 'asl_gusts') * 0.514444

    def getCloudMinMax(self):
        return {'min': self.weatherdata.getint('Clouds', 'floor') + self.getStationElevation(),
                'max': self.weatherdata.getint('Clouds', 'ceiling') + self.getStationElevation()}

    def getCloudBase(self):
        return max(300, self.getCloudMinMax()['min'])

    def getCloudThickness(self):
        minmaxclouds = self.getCloudMinMax()
        return minmaxclouds['max']-minmaxclouds['min']

    def getCloudDensity(self):
        return self.weatherdata.getint('Clouds', 'density')

    def getWeatherType(self):
        return self.weatherdata.getint('Weather', 'precipitation')

    def getFogEnabled(self):
        return self.weatherdata.getboolean('Weather', 'fog')

    def getFogVisibility(self):
        if self.getFogEnabled():
            self.seedRandom()
            return self.getDeterministicRandomInt(800, 1000)
        else:
            return 0

    def getFogThickness(self):
        if self.getFogEnabled():
            self.seedRandom()
            return self.getDeterministicRandomInt(100, 300)
        else:
            return 0

    def getVisibility(self):
        try:
            visibility = self.weatherdata.getint('Weather', 'visibility')
            if visibility >= 9000:
                return 80000
            else:
                return visibility
        except:
            return 80000

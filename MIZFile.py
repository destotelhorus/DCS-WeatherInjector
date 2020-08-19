from math import floor

from ruamel.std.zipfile import InMemoryZipFile
from zipfile import ZipFile
from libraries.slpp import dcsslpp as lua
from datetime import datetime

WRITEACCESS_ERROR = 'This file is write-protected!'
class WriteProtectionError(Exception):
    pass

class MIZFile(object):
    MIZfilename = ''
    readonly = True
    missionData = None
    theatre = None

    def __init__(self, filename, readonly=True):
        self.MIZfilename = filename
        self.readonly = readonly

    def commit(self):
        if self.readonly:
            raise WriteProtectionError(WRITEACCESS_ERROR)
        mizfilehandle = InMemoryZipFile(self.MIZfilename)
        mizfilehandle.delete_from_zip_file(None, 'mission')
        mizfilehandle.append('mission', lua.encode(self.missionData)[1:-1].encode('UTF-8'))
        mizfilehandle.write_to_file(self.MIZfilename)

    def getMission(self):
        if self.missionData:
            return self.missionData['mission']
        mizfilehandle = ZipFile(self.MIZfilename, mode='r')
        missionfilehandle = mizfilehandle.open('mission', 'r')
        self.missionData = lua.decode('{' + missionfilehandle.read().decode('UTF-8') + '}')
        missionfilehandle.close()
        return self.missionData['mission']

    def setMission(self, missiondata):
        if self.readonly:
            raise WriteProtectionError(WRITEACCESS_ERROR)
        self.missionData['mission'] = missiondata

    def getTheatre(self):
        if self.theatre:
            return self.theatre
        mizfilehandle = ZipFile(self.MIZfilename, mode='r')
        theatrefilehandle = mizfilehandle.open('theatre', 'r')
        self.theatre = theatrefilehandle.read().decode('UTF-8')
        return self.theatre

    def getTheatreLatLon(self):
        if self.getTheatre() == 'Caucasus':
            return {"lat": 42.355691, "lon": 43.323853}
        elif self.getTheatre() == 'PersianGulf':
            return {"lat": 26.304151 , "lon": 56.378506}
        elif self.getTheatre() == 'Nevada':
            return {"lat": 36.145615, "lon": -115.187618}
        elif self.getTheatre() == 'Normandy':
            return {"lat": 49.183336, "lon": -0.365908}
        elif self.getTheatre() == 'Syria':
            return {"lat": 33.510414, "lon": 36.278336}
        else:
            return None

    def getDateTime(self):
        day = self.getMission()['date']['Day']
        month = self.getMission()['date']['Month']
        year = self.getMission()['date']['Year']
        starttime = self.getMission()['start_time']
        second = floor(starttime % 60)
        starttime /= 60
        minute = floor(starttime % 60)
        hour = floor(starttime / 60)
        datestr = f'{day:02}' + '.' + f'{month:02}' + '.' + f'{year:04}' + ' ' + f'{hour:02}' + ':' + f'{minute:02}'\
                  + ':' + f'{second:02}'
        return datetime.strptime(datestr, '%d.%m.%Y %H:%M:%S')

    def setDateTime(self, dt):
        if self.readonly:
            raise WriteProtectionError(WRITEACCESS_ERROR)
        missiondata = self.getMission()
        missiondata['date']['Day'] = dt.day
        missiondata['date']['Month'] = dt.month
        missiondata['date']['Year'] = dt.year
        missiondata['start_time'] = (((dt.hour*60) + dt.minute)*60) + dt.second
        self.setMission(missiondata)

    def setDateTimeNow(self):
        self.setDateTime(datetime.now())

    def getWeather(self):
        return self.getMission()['weather']

    def setWeather(self, weatherdata):
        if self.readonly:
            raise WriteProtectionError(WRITEACCESS_ERROR)
        missiondata = self.getMission()
        missiondata['weather'] = weatherdata
        self.setMission(missiondata)

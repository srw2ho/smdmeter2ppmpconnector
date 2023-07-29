
from datetime import datetime, timedelta, timezone
from dateutil import parser, relativedelta
# from time import time



class TimeSpan(object):
    def __init__(self):
        self.m_startTime = datetime.now(timezone.utc).astimezone()
        self.m_stopTime = self.m_startTime
        self.m_actTime = self.m_startTime

    def setStartTime(self, startTime):
        self.m_startTime = startTime

    def setActTime(self, actTime):
        self.m_actTime = actTime

    def setStopTime(self, stopTime):
        self.m_stopTime = stopTime

    def getTimediffernceintoHours(self, difference):

        delta = timedelta(
            days=difference.days,
            seconds=difference.seconds,
            microseconds=difference.microseconds,
            milliseconds=0,
            minutes=difference.minutes,
            hours=difference.hours,
            weeks=difference.weeks)
        return float(delta.total_seconds()) / float(3600)

    def getTimediffernceintoSecs(self, difference):
    
        delta = timedelta(
            days=difference.days,
            seconds=difference.seconds,
            microseconds=difference.microseconds,
            milliseconds=0,
            minutes=difference.minutes,
            hours=difference.hours,
            weeks=difference.weeks)
        return float(delta.total_seconds()) 
    
    def getTimeSpantoEndTime(self):

        difference = relativedelta.relativedelta(
            self.m_stopTime, self.m_startTime)
        return difference

    def getTimeSpantoNow(self):

        datenow = datetime.now(timezone.utc).astimezone()
        difference = relativedelta.relativedelta(datenow, self.m_startTime)
        return difference

    def getTimeSpantoActTime(self):

        datenow = datetime.now(timezone.utc).astimezone()
        difference = relativedelta.relativedelta(datenow, self.m_actTime)

        return difference


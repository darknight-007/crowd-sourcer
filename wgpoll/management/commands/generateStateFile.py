from django.core.management.base import BaseCommand, CommandError
from wgpoll.models import Vote
from wgpoll.models import WaveGliderState
from wgpoll.models import Ballot 
import os
from datetime import datetime as dt, timedelta
from django.contrib.gis.geos import Point,Polygon
from pykml import parser
import calendar 

import math
import numpy
from pydap.client import open_url
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib import mpl
class Command(BaseCommand):
	args = '<vote_id vote_id ...>'
	help = 'Updates Wave Glider state using voting data'

	def handle(self, *args, **options):
		startDate = dt(2013, 7, 26, 11, 31, 00, 739556)
        	endDate = dt(2013, 7, 26, 15, 15, 00, 739556)
		wgStates = WaveGliderState.objects.filter(time__gt=startDate, time__lt=endDate)
		myfile=open('stateOceans2013.csv','w')
		angle = {'unsure' : -1 , 'east' : 0, 'west': 180, 'stop': -10, 'north':90, 'south':270}		
		for state in wgStates:
			myfile.write(str(calendar.timegm(state.time.utctimetuple())) + ',' + str(state.latitude)  + ',' + str(state.longitude)  + ',' + str(state.temp)  + ','  + str(state.sal)  + ','  + str(state.chl)  + '\n')
		print wgStates[0]



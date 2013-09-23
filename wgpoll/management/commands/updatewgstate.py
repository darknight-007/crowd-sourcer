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

	def testIfPointInSafeRegion(self, lat,lon):
                pnt=Point(lat, lon)
                poly=Polygon(((36.936607018, -122.091610313), (36.958683905,-122.162639595) ,(36.987815521,-122.21506135) ,(37.15981,-122.56020),(36.69,-122.56020) ,(36.54776547,-121.992926099) ,(36.593976161,-121.989732818) ,(36.651878564,-121.95285214) ,(36.661324564,-121.909793526),(36.626844509,-121.880774172) ,(36.700304474,-121.835279292) ,(36.761488333,-121.823453925) ,(36.803637867,-121.812197052) ,(36.876714034,-121.853754579) ,(36.940579814,-121.895316436) ,(36.961193612,-121.929400728),(36.940762557,-121.971105151) ,(36.948092066,-122.002927721) ,(36.936402112,-122.028084038) ,(36.936607018,-122.091610313)))
                return poly.contains(pnt)
	
	def handle(self, *args, **options):
		try:
			#DEG_STEP = 0.0005
			# 0.1 deg longtitude = 9 km 
			# 0.1 deg latitude = 11 km 
			# wave glider speed : 0.9 m/s 
			# advection speed 0.3 m/s
			# last coord 37.0598171042004	-122.460206988621 
			LAT_MAX = 37.15981
			LON_MIN = -122.56020
			LAT_MIN = 36.69
			NUM_TICKS_PER_MIN = 6
			plotInTicks = 6
			WG_LAT_DEG_STEP_PER_MIN = 0.0299/NUM_TICKS_PER_MIN
			WG_LON_DEG_STEP_PER_MIN = 0.034/NUM_TICKS_PER_MIN
			collided = 0
			  
			#DEG_STEP = 0.005 
			voteCount = {'unsure' : 0, 'stop' : 0, 'north' : 0, 'south': 0, 'east' : 0, 'west' : 0}	
			latDeltaMap = {'unsure' : 0.0, 'stop' : 0.0, 'north' : WG_LAT_DEG_STEP_PER_MIN, 'south': -WG_LAT_DEG_STEP_PER_MIN, 'east' : 0.0, 'west' : 0.0}	
			lonDeltaMap = {'unsure' : 0.0, 'stop' : 0.0, 'north' : 0.0, 'south': 0.0, 'east' : WG_LON_DEG_STEP_PER_MIN, 'west' : -WG_LON_DEG_STEP_PER_MIN}	
			dirMap = {'unsure' : 0.0, 'stop' : 0.0, 'north' : 0.0, 'south': 180.0, 'east' : 90.0, 'west' : 270.0}	
			speedMap = {'unsure' : 0.0, 'stop' : 0.0, 'north' : 0.01, 'south': 0.01, 'east' : 0.01, 'west' : 0.01}	

			pollWindowInSecs = 10;
		        endDate = dt.now()
        		startDate = endDate - timedelta(0,pollWindowInSecs)
        		lastFew = Vote.objects.filter(date__gt=startDate, date__lt=endDate)

        		maxCount = -99;
        		maxVote = Vote(date=dt.now(),user=0, value='unsure',confidence=0.99) 
        		for vote_ in lastFew:
                        	voteCount[vote_.value] = voteCount[vote_.value] + 1;
                        	print vote_.value + ':' + str(voteCount[vote_.value])
				if voteCount[vote_.value] > maxCount and not(vote_.value == 'unsure'):
                                	maxCount = voteCount[vote_.value];
                                	maxVote = vote_
					print vote_.value

			val=maxVote.value
			latestState = WaveGliderState.objects.latest('time')
			newLat = latestState.latitude + latDeltaMap[val]
			newLon = latestState.longitude + lonDeltaMap[val]
			if not (self.testIfPointInSafeRegion(newLat,newLon)):
				newLat = latestState.latitude
				newLon = latestState.longitude
				collided = 0.1
			else:
				collided = 0.0
			
			lon = 360.0+newLon;
			lonInd = int(math.floor((lon-237.2)/(1.3/131)))
			latInd = int(math.floor((newLat-35.6)/(1.7/171)))
			
			hour = 0 
			
			dataset = open_url("http://ourocean.jpl.nasa.gov:8080/thredds/dodsC/MBNowcast/mb_das_20120520_mean.nc")
			sst = dataset['temp']
			tempMap = sst.array[hour,0,latInd,lonInd]
			tempVal = tempMap[0,0,0,0]
		
			salt = dataset['salt']
                        salMap = salt.array[hour,0,latInd,lonInd]
                        salVal = salMap[0,0,0,0]

			vmin_,vmax_ = 0,800
		  	trackWindowInSecs = 60*24;
                        endDate = dt.now()
                        startDate = endDate - timedelta(0,trackWindowInSecs)
                        lastFewUpdates = WaveGliderState.objects.filter(time__gt=startDate, time__lt=endDate)
                        lonVec = []
                        latVec = []
                        tempVec = []
                        salVec = []
                        chlVec = []
                        for wgUpdate in lastFewUpdates:
                                lonVec = numpy.append(lonVec,wgUpdate.longitude)
                                latVec = numpy.append(latVec, wgUpdate.latitude)
                                tempVec = numpy.append(tempVec, wgUpdate.temp)
                                salVec = numpy.append(salVec, wgUpdate.sal)
                                chlVec = numpy.append(chlVec, wgUpdate.chl)


                        plt.scatter(lonVec,latVec,10,chlVec,marker='s', edgecolors='none')
                        plt.xlim([LON_MIN,-121.79])
                        plt.ylim([LAT_MIN,LAT_MAX])
			fig = plt.gcf()
                        a=fig.gca()
                        a.set_frame_on(False)
                        a.set_xticks([]); a.set_yticks([])
                        plt.axis('off')
                        plt.clim(vmin_, vmax_)
                        plt.savefig('science_data_layer_chl.png',transparent=True,pad_inches=0,bbox_inches='tight',frameon=False)
                        os.system('cp /home/jd/science_data_layer_chl.png /var/www/cinaps/')

			plt.scatter(lonVec,latVec,10,salVec,marker='s', edgecolors='none')
                        plt.xlim([LON_MIN,-121.79])
                        plt.ylim([LAT_MIN,LAT_MAX])
			fig = plt.gcf()
                        a=fig.gca()
                        a.set_frame_on(False)
                        a.set_xticks([]); a.set_yticks([])
                        plt.axis('off')
			salvmin_, salvmax_ = plt.gci().get_clim()
                        plt.clim(salvmin_, salvmax_)
                        plt.savefig('science_data_layer_sal.png',transparent=True,pad_inches=0,bbox_inches='tight',frameon=False)
                        os.system('cp /home/jd/science_data_layer_sal.png /var/www/cinaps/')
			
			fig.clf()
                        ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
                        cmap = mpl.cm.jet
                        norm = mpl.colors.Normalize(vmin=salvmin_, vmax=salvmax_)

                        cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,norm=norm, orientation='horizontal')
                        cbytick_obj = plt.getp(cb1.ax.axes, 'xticklabels')
                        plt.setp(cbytick_obj, color='w')
                        plt.setp(cbytick_obj, fontsize=18)
			cb1.set_label('Score')
                        plt.savefig('/var/www/cinaps/jd/simoverlaycolorbarsal.png',transparent=True,pad_inches=0,bbox_inches='tight',frameon=False)
                        fig.clf()


			#chlVal = -38.3894999141604 -0.700239885543149*tempVal + 1.62938943619475*salVal	
			#doc = parser.parse('/home/jd/BatchGeo.kml').getroot()
                        #data = doc.Document.Placemark.LineString.coordinates.text.split(' ')
			f = open('/home/jd/plumePoints.txt')
			data = [line.rstrip('\n') for line in f]
			numPoints = len(data)
			print 'start science field generation...'
			fig = plt.gcf()
			timestamp=calendar.timegm(dt.now().utctimetuple())
			tick =  (timestamp/10)%numPoints
			print tick
			ind1 = tick
                        coord = data[ind1].split('\t')
                        coord0 = data[0].split('\t')
			fieldLon = float(coord[2])
                        fieldLat = float(coord[1])
                        #fieldLon2 = -121.9462130707369
                        #fieldLat2 = 36.87829987329702
			fieldLon2 = float(coord0[2]) 
                        fieldLat2 = float(coord0[1])

                        fig.clf()
                        pi = math.pi
                        widthScaler1 = 0.01/numPoints
                        widthScaler2 = 0.05/numPoints
                        sig = 0.01
                        sig1 = sig + ind1*widthScaler1
                        sig2 = sig + (numPoints-ind1)*widthScaler2
                        #sig2 = sig - (math.sin((((dt.now().second/60.0)*4*pi)-2*pi))*sig/2)+sig
                        deltaLat = 0.00909
			deltaLon = 0.0111
                        if ind1 % plotInTicks:
                        	x = numpy.arange(LON_MIN,-121.79,deltaLon)
                        	y = numpy.arange(LAT_MIN,LAT_MAX,deltaLat)
                        	X, Y = numpy.meshgrid(x, y)
				Z1 = mlab.bivariate_normal(X, Y, sig1,sig1 ,fieldLon,fieldLat)
				Z2 = mlab.bivariate_normal(X, Y, sig2, sig2,fieldLon2,fieldLat2)
				#CS1 = plt.contour(X, Y, Z1+Z2)
				CS2 = plt.pcolor(X, Y, Z1+Z2,alpha=0.5,shading='interp')
				#plt.clabel(CS1,inline=True,fontsize=10)
				plt.xlim([LON_MIN,-121.79])
				plt.ylim([LAT_MIN,LAT_MAX])
				#fig.patch.set_alpha(0.1)
				fig = plt.gcf()
				a=fig.gca()
				a.set_frame_on(False)
				a.set_xticks([]); a.set_yticks([])
				plt.axis('off')
				plt.savefig('/var/www/cinaps/jd/simoverlay.png',transparent=True,pad_inches=0,bbox_inches='tight',frameon=False)
				#vmin_, vmax_ = plt.gci().get_clim()

				fig.clf()
				ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
				cmap = mpl.cm.jet
				norm = mpl.colors.Normalize(vmin=vmin_, vmax=vmax_)

				cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,norm=norm, orientation='horizontal')
				cbytick_obj = plt.getp(cb1.ax.axes, 'xticklabels')   
				plt.setp(cbytick_obj, color='w')
	                        plt.setp(cbytick_obj, fontsize=18)
				cb1.set_label('Score')		
				plt.savefig('/var/www/cinaps/jd/simoverlaycolorbarchl.png',transparent=True,pad_inches=0,bbox_inches='tight',frameon=False)
				fig.clf()
			chlVal = mlab.bivariate_normal(newLon, newLat, sig1,sig1 ,fieldLon,fieldLat) + mlab.bivariate_normal(newLon, newLat, sig2, sig2,fieldLon2,fieldLat2)
			print 'end science field generation...' 
			print dt.now()
			now_ = dt.now()
			newWgState = WaveGliderState(time = now_, latitude = newLat,longitude = newLon, speed = speedMap[val], direction = dirMap[val],temp = tick+collided,sal = numpy.sum(chlVec)+chlVal,chl = chlVal)
			newWgState.save()
			ballot = Ballot(time=endDate,unsure=voteCount['unsure'],stop=voteCount['stop'],north=voteCount['north'],south=voteCount['south'], east=voteCount['east'],west=voteCount['west'],winner=maxVote.value)
        		ballot.save()
			plt.scatter(newWgState.longitude,newWgState.latitude,1,0,edgecolors='none')
                        plt.xlim([-122.51918826855467,-121.75083194531248])
                        plt.ylim([36.61883405115106,36.97622643672235])
                        fig = plt.gcf()
                        a=fig.gca()
                        a.set_frame_on(False)
                        a.set_xticks([]); a.set_yticks([])
                        plt.axis('off')
                        plt.savefig('science_data_layer_none.png',transparent=True,pad_inches=0,bbox_inches='tight',frameon=False)
                        os.system('cp /home/jd/science_data_layer_none.png /var/www/cinaps/')
	

			#fieldLat = 36.839438
			#fieldLon = -122.096538
			
			#fieldLat = newLat
                        #fieldLon = newLon


		except Vote.DoesNotExist:
			raise CommandError('Error updating Wave Glider state')
			
		self.stdout.write('Succesfully updated Wave Glider state')



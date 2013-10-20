from django.core.management.base import BaseCommand, CommandError
from wgpoll.models import VoteWP
from wgpoll.models import WaveGliderState
from wgpoll.models import BallotWP
import os
from datetime import datetime as dt, timedelta
from django.contrib.gis.geos import Point,Polygon
from pykml import parser
import calendar 
from geopy import Point
from geopy.distance import distance, VincentyDistance

import math
import numpy
from pydap.client import open_url
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib import mpl
import scipy
from scipy.cluster.vq import *
import pylab
pylab.close()

class Command(BaseCommand):
	args = '<vote_id vote_id ...>'
	help = 'Updates Wave Glider state using voting data'

	def testIfPointInSafeRegion(self, lat,lon):
                pnt=Point(lat, lon)
                
                poly=Polygon(((36.936607018, -122.091610313), (36.958683905,-122.162639595) ,(36.987815521,-122.21506135) ,(37.15981,-122.56020),(36.69,-122.56020) ,(36.54776547,-121.992926099) ,(36.593976161,-121.989732818) ,(36.651878564,-121.95285214) ,(36.661324564,-121.909793526),(36.626844509,-121.880774172) ,(36.700304474,-121.835279292) ,(36.761488333,-121.823453925) ,(36.803637867,-121.812197052) ,(36.876714034,-121.853754579) ,(36.940579814,-121.895316436) ,(36.961193612,-121.929400728),(36.940762557,-121.971105151) ,(36.948092066,-122.002927721) ,(36.936402112,-122.028084038) ,(36.936607018,-122.091610313)))
                
                return poly.contains(pnt)
                
	def bearing(self,lat1, lon1, lat2, lon2):
				dLon = lon2 - lon1;
				y = math.sin(dLon) * math.cos(lat2);
				x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon);
				return math.degrees(math.atan2(y, x));
	
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
			STEP_DIST_MILE = 1.00662;
			  
			#DEG_STEP = 0.005 
			pollWindowInSecs = 10;
			endDate = dt.now()
			startDate = endDate - timedelta(0,pollWindowInSecs)
			lastFew = VoteWP.objects.filter(date__gt=startDate, date__lt=endDate)

			latAvg = 0.0
			lonAvg = 0.0
			newLat = 0.0
			newLon = 0.0
			arr = numpy.ndarray(shape=(len(lastFew),2), dtype=float, order='F')
			ctr = 0;
			for vote_ in lastFew:
				latitude_ = vote_.latitude
				longitude_ = vote_.longitude
				if not (latitude_ < 1):
					
					arr[ctr,1] = latitude_
					arr[ctr,0] = longitude_
					ctr = ctr+1
				else:
					print 'zero lat detected'
			
			winners = [];
			scoreMax = -1;
			centerMax = []
			indMax = -1;
			for i in range(2,5):
				res, idx = kmeans2(arr,i)
				[c,d] = vq(arr, res)
				ua,uind=numpy.unique(idx,return_inverse=True)
				count=numpy.bincount(uind)
				maxCountInd = numpy.argmax(count)
				maxCount = max(count)
				center= [res[ua[maxCountInd],0],res[ua[maxCountInd],1]];
				score = pow(maxCount,2)*(1/numpy.sum(d))*(1/sum(scipy.spatial.distance.pdist(res,'euclidean')))
				if score > scoreMax:
					scoreMax = score
					centerMax = center
					indMax = i
				
			#res, idx = kmeans2(arr,indMax)

			
			# convert groups to rbg 3-tuples.
			#colors = ([([0,0,0],[0,1,1])[i] for i in idx])

			# show sizes and colors. each color belongs in diff cluster.
			#pylab.scatter(arr[:,1],arr[:,0],s=20, c=colors)
			#plt.plot(res[1,1],res[1,0])
			#pylab.savefig('/var/www/cinaps/jd/clust.png')
			lonAvg = centerMax[0]
			latAvg = centerMax[1]
			latestState = WaveGliderState.objects.latest('time')
			
			
			
			
			bearing_ = self.bearing(math.radians(latestState.latitude), math.radians(latestState.longitude),math.radians(latAvg),math.radians(lonAvg))
			print 'bearing=' + str(bearing_)
			destPoint = VincentyDistance(STEP_DIST_MILE).destination(Point(latestState.latitude,latestState.longitude),  bearing_)
			hour = 0 
			print destPoint
			print destPoint.latitude, destPoint.longitude
			newLat = destPoint.latitude
			newLon = destPoint.longitude
				
			
			
			#if not (self.testIfPointInSafeRegion(newLat,newLon)):
			#	newLat = latestState.latitude
			#	newLon = latestState.longitude
			#	print 'here0'
			#	collided = 0.1
			#else:
			collided = 0.0
			
			lon = 360.0+newLon;
			
			lonInd = int(math.floor((lon-237.2)/(1.3/131)))
			latInd = int(math.floor((newLat-35.6)/(1.7/171)))
				
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
			newWgState = WaveGliderState(time = now_, latitude = newLat,longitude = newLon, speed = 0, direction = bearing_,temp = tick+collided,sal = numpy.sum(chlVec)+chlVal,chl = chlVal)
			newWgState.save()
			ballot = BallotWP(time=endDate,latitude = latAvg,longitude=lonAvg		)
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


		except VoteWP.DoesNotExist:
			raise CommandError('Error updating Wave Glider state')
			
		self.stdout.write('Succesfully updated Wave Glider state')



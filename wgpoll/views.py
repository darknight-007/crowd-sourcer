import csv
from django.template import Context, loader
from wgpoll.models import VoteWP
from wgpoll.models import WaveGliderState
from wgpoll.models import BallotWP
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.gis.maps.google.gmap import GoogleMap
from django.contrib.gis.maps.google.overlays import GMarker, GEvent

from datetime import datetime, timedelta
from django import forms
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.utils import simplejson

from django.core import serializers
from django.template import RequestContext
    
def index(request):
    return render_to_response('wgpoll/index.html',RequestContext(request))
    
def vote(request):
	latitude_ = request.GET.get('lat')
	longitude_ = request.GET.get('lon')
	user_ = request.GET.get('user')
	confidence_ = request.GET.get('confidence')
	
	if not (latitude_ < 20):
		p = VoteWP(date=datetime.now(),user=str(user_)+ ',' + request.META['REMOTE_ADDR'], latitude=latitude_,longitude=longitude_,confidence=confidence_)
		p.save() 
	pollWindowInSecs = 10;
	endDate = datetime.now()
	startDate = endDate - timedelta(0,pollWindowInSecs)
	lastFewVotes = VoteWP.objects.filter(date__gt=startDate, date__lt=endDate)
			
	wgState = WaveGliderState.objects.latest('time');
	trackWindowInSecs = 60*2;
	endDate = datetime.now()
	startDate = endDate - timedelta(0,trackWindowInSecs)
	lastFewUpdates = WaveGliderState.objects.filter(time__gt=startDate, time__lt=endDate)
	voteList = serializers.serialize('json', lastFewVotes, fields=('latitude','longitude'))
	wgTrackLine = serializers.serialize('json', lastFewUpdates, fields=('latitude','longitude'))
	latestBallot = BallotWP.objects.latest('time')
	stateUpdate = {'latitude' : latestBallot.latitude, 'longitude' : latestBallot.longitude}
	stateUpdate['currLat'] = '{0:.8g}'.format(wgState.latitude);
	stateUpdate['currLon'] = '{0:.9g}'.format(wgState.longitude);
	stateUpdate['wgTrackLine'] = wgTrackLine
	stateUpdate['hour'] = (int(wgState.temp)-1)/6
	#stateUpdate['min'] = 
	stateUpdate['collison'] = '{0:.2g}'.format(round(wgState.temp - int(wgState.temp),2)*10)
	stateUpdate['temp'] = '{0:.4g}'.format(wgState.temp)
	stateUpdate['sal'] = '{0:.4g}'.format(wgState.sal)
	stateUpdate['chl'] = '{0:.10g}'.format(round(wgState.chl,0))
	stateUpdate['voteList'] = voteList
	json = simplejson.dumps(stateUpdate)
	return HttpResponse(json, mimetype='application/json')
   
def report(request):
	response = HttpResponse(content_type='text/csv')
    	response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    	writer = csv.writer(response)
	trackWindowInSecs = 60*3600;
        endDate = datetime.now()
        startDate = endDate - timedelta(0,trackWindowInSecs)
        wgStates = WaveGliderState.objects.filter(time__gt=startDate, time__lt=endDate)

	for wgState in wgStates:
		writer.writerow([wgState.latitude, wgState.longitude, wgState.speed, wgState.direction, wgState.temp, wgState.sal, wgState.chl])

    	return response    


def getvotes(request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

        writer = csv.writer(response)
        trackWindowInSecs = 60*3600;
        endDate = datetime.now()
        startDate = endDate - timedelta(0,trackWindowInSecs)
        wgStates = Vote.objects.filter(date__gt=startDate, date__lt=endDate)

        for wgState in wgStates:
                writer.writerow([wgState.user, wgState.value])

        return response

def getballots(request):
        response = HttpResponse(content_type='text')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

        writer = csv.writer(response)
        trackWindowInSecs = 60*3600;
        endDate = datetime.now()
        startDate = endDate - timedelta(0,trackWindowInSecs)
        wgStates = BallotWP.objects.filter(time__gt=startDate, time__lt=endDate)

        for wgState in wgStates:
                response.write(wgState.winner)

        return response 

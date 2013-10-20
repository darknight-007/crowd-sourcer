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
    return render_to_response('wgpoll/dash.html',RequestContext(request))

def update(request):
        wgState = WaveGliderState.objects.latest('time');
        trackWindowInSecs = 60*5;
	pollHistoryWindowInSecs = 10;
        endDate = datetime.now()
        startDate = endDate - timedelta(0,trackWindowInSecs)
	startDatePoll = endDate - timedelta(0,pollHistoryWindowInSecs)
        lastFewUpdates = WaveGliderState.objects.filter(time__gt=startDate, time__lt=endDate)
	lastFewVotes = VoteWP.objects.filter(date__gt=startDatePoll, date__lt=endDate)

        wgTrackLine = serializers.serialize('json', lastFewUpdates, fields=('latitude','longitude'))
        votes = serializers.serialize('json', lastFewVotes, fields=('user','value'))
	latestBallot = BallotWP.objects.latest('time')
        stateUpdate = {'unsure' : latestBallot.unsure, 'stop' : latestBallot.stop,'north' : latestBallot.north, 'south' : latestBallot.south, 'east' :latestBallot.east, 'west' : latestBallot.west, 'winner' : latestBallot.winner}
        stateUpdate['currLat'] = wgState.latitude;
        stateUpdate['currLon'] = wgState.longitude;
        stateUpdate['wgTrackLine'] = wgTrackLine
	stateUpdate['votes'] = votes
	stateUpdate['temp'] = '{0:.4g}'.format(wgState.temp)
        stateUpdate['sal'] = '{0:.4g}'.format(wgState.sal)
        stateUpdate['chl'] = '{0:.4g}'.format(wgState.chl)
	json = simplejson.dumps(stateUpdate)
        return HttpResponse(json, mimetype='application/json')
    

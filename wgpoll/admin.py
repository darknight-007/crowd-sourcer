from django.contrib import admin
from wgpoll.models import VoteWP
#from wgpoll.models import WaveGliderState
from wgpoll.models import BallotWP


admin.site.register(VoteWP)
#admin.site.register(WaveGliderState)
admin.site.register(BallotWP)

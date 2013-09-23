from django.contrib import admin
from wgpoll.models import Vote
from wgpoll.models import WaveGliderState
from wgpoll.models import Ballot 


admin.site.register(Vote)
admin.site.register(WaveGliderState)
admin.site.register(Ballot)

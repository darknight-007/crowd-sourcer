from django.db import models
import datetime


class Vote(models.Model):
    mapCenterLat = 36.798289
    mapCenterLon = -121.975021
    date = models.DateTimeField('date published')
    user = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    confidence = models.DecimalField(max_digits=3, decimal_places=2)
    def was_published_recently(self):
        return self.date >= datetime.datetime.now() - datetime.timedelta(seconds=20)
    
    was_published_recently.admin_order_field = 'date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'
    
    def __unicode__(self):
		return  self.user + ', ' + self.value + ', ' + str(self.confidence)
	
class WaveGliderState(models.Model):
	time = models.DateTimeField('time')
	latitude = models.FloatField()
	longitude = models.FloatField()
	speed = models.FloatField()
	direction = models.FloatField()
	temp = models.FloatField()
	sal = models.FloatField()
	chl = models.FloatField()
	def __unicode__(self):  # Python 3: def __str__(self):
        	return str(self.time) + ',' + str(self.latitude) + ',' + str(self.longitude) + ',' + str(self.temp) + ',' + str(self.sal) + ',' + str(self.chl) 

class Ballot(models.Model):
	time = models.DateTimeField('time')
	unsure = models.IntegerField()
	stop = models.IntegerField()
	north = models.IntegerField()
	south = models.IntegerField()
	east = models.IntegerField()
	west = models.IntegerField()
	winner = models.CharField(max_length=10)

	def __unicode__(self):  # Python 3: def __str__(self):
                return str(self.time) + ',' + self.winner


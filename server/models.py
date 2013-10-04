from django.db import models
from django.http import HttpResponse
from settings import NUM_REQUIRED_BEFORE_NODE_OR_LINK_GOES_LIVE
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models.signals import post_save



class Node(models.Model):
    hostname = models.CharField(max_length=256)
    ip_addr = models.CharField(max_length=15)
    creation_date = models.DateTimeField(auto_now = True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    authenticated = models.BooleanField(default=False)
    num_node_adders = models.IntegerField(default=0)

    def increment_and_check_authenticate(self, user=None):
        if self.authenticated:
            return

        if user is not None:
            user.nodes_uploaded.add(self)
            user.save()
        
        self.num_node_adders += 1
        if self.num_node_adders >= NUM_REQUIRED_BEFORE_NODE_OR_LINK_GOES_LIVE:
            self.authenticated = True
            self.creation_date = datetime.now()
        self.save()
    
    class Meta:
        app_label = 'server'

        
class Links(models.Model):
    node1 = models.ForeignKey(Node,related_name='node1')
    node2 = models.ForeignKey(Node,related_name='node2')
    creation_date = models.DateTimeField(auto_now = True)
    authenticated = models.BooleanField(default=False)
    num_link_adders = models.IntegerField(default=0)

    def increment_and_check_authenticate(self,user=None):
        if self.authenticated:
            return

        if user is not None:
            user.links_uploaded.add(self)
            user.save()
            
        self.num_link_adders += 1
        if self.num_link_adders >= NUM_REQUIRED_BEFORE_NODE_OR_LINK_GOES_LIVE:
            self.authenticated = True
            self.creation_date = datetime.now()

        self.save()
    
    class Meta:
        app_label = 'server'


class UserProfile(models.Model):
    # keeps track of all the links and nodes that a single user has
    # uploaded.
    user = models.OneToOneField(User)
    nodes_uploaded = models.ManyToManyField(Node)
    links_uploaded = models.ManyToManyField(Links)

    @staticmethod
    def check_create_user_profile(user):
        users = UserProfile.objects.filter(user__id = user.id)
        if len(users) == 0:
            prof = UserProfile(user=user)
            prof.save()
    
    class Meta:
        app_label = 'server'




class IPRange(models.Model):
    lower_bound = models.PositiveIntegerField()
    upper_bound = models.PositiveIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        app_label = 'server'


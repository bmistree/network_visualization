#!/usr/bin/python

from django.db import models
from django.http import HttpResponse
import json

        
class Node(models.Model):
    hostname = models.CharField(max_length=256)
    ip_addr = models.CharField(max_length=15)
    creation_date = models.DateTimeField(auto_now = True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        app_label = 'server'

        
class Links(models.Model):
    node1 = models.ForeignKey(Node,related_name='node1')
    node2 = models.ForeignKey(Node,related_name='node2')
    creation_date = models.DateTimeField(auto_now = True)
    
    class Meta:
        app_label = 'server'


class IPRange(models.Model):
    lower_bound = models.PositiveIntegerField()
    upper_bound = models.PositiveIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        app_label = 'server'


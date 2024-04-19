from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    name = models.CharField(max_length=255)
    video_url = models.URLField()
    #owner = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.video_url

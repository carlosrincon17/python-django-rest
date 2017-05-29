# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.files.storage import default_storage as storage
from django.db import models
from PIL import Image
# Create your models here.

class Apk(models.Model):
    name = models.CharField(max_length=80, blank=False)
    description = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover = models.ImageField(upload_to='thumbs')
    apk = models.FileField(upload_to='apk_uploads')
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        super(Apk, self).save(*args, **kwargs)
        if not self.make_thumbnail():
            raise Exception('Could not create thumbnail')

    def make_thumbnail(self):
        fh = storage.open(self.cover, 'r')
        try:
            image = Image.open(fh)
        except Exception as e:
            return False
        sizes = [(50, 50), (100, 100)]
        for thumb_size in sizes:
            img = image.copy()
            img.thumbnail(thumb_size, Image.ANTIALIAS)
            thumb_filename = "thumbs/{}_{}.png".format(self.id, thumb_size[0])
            img.save(thumb_filename, 'PNG')
        return True

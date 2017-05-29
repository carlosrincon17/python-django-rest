# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import StringIO
import zipfile
import os

from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.http.response import HttpResponse

# Create your views here.
from rest_framework import exceptions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from apks.authentication import TokenAuth
from apks.models import Apk
from apks.serializers import ApkSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)



class ListApks(APIView):
    authentication_classes = [TokenAuth]

    @staticmethod
    def __get_filter_request(request):
        name = request.query_params.get('name', None)
        filter_ = dict()
        if name:
            filter_['name__contains'] = name
        return filter_

    def post(self, request):
        apk = ApkSerializer(data=request.data)
        if apk.is_valid():
            apk.save(cover=request.FILES['cover'], apk=request.FILES['apk'],
                     user=request.user.user)
            send_notification_email()
            return JSONResponse(apk.data, status=status.HTTP_201_CREATED)
        return JSONResponse(apk.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        apks = Apk.objects.filter(**self.__get_filter_request(request))
        serializer = ApkSerializer(apks, many=True)
        return JSONResponse(serializer.data, status=status.HTTP_200_OK)


class Apks(APIView):
    authentication_classes = [TokenAuth]

    @staticmethod
    def get_object(id):
        try:
            apk = Apk.objects.get(id=id)
            return apk
        except Apk.DoesNotExist:
            raise exceptions.NotFound("Object not found")

    def get(self, request, id):
        apk = self.get_object(id)
        serializer = ApkSerializer(apk)
        return JSONResponse(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        apk = self.get_object(id)
        apk.delete()
        serializer = ApkSerializer(apk)
        return JSONResponse(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        apk = self.get_object(id)
        serializer = ApkSerializer(apk, data=request.data)
        if serializer.is_valid():
            serializer.save(cover=request.FILES['cover'],
                            apk=request.FILES['apk'])
            return JSONResponse(serializer.data, status=status.HTTP_200_OK)
        return JSONResponse(apk.errors, status=status.HTTP_400_BAD_REQUEST)


def send_notification_email():
    upload_apks = Apk.objects.count()
    if upload_apks % 5 == 0:
        apks = Apk.objects.all() \
            .prefetch_related('user') \
            .order_by('-created_at')
        csv_file = get_csv_file(apks)
        zip_file = get_zip_file(apks[:10])
        try:
            user = User.objects.filter(is_superuser=True).first()
            message = "Upload apks : {}".format(upload_apks)
            email = EmailMessage('Upload apks', message, EMAIL_HOST_USER,
                                 [user.email])
            email.attach('report.csv', csv_file.getvalue(), 'text/csv')
            email.attach('apks.zip', zip_file.getvalue(),
                         'application/octet-stream')
            email.send(fail_silently=False)
        except User.DoesNotExist:
            pass


def get_csv_file(apks):
    csv_file = StringIO.StringIO()
    writer = csv.writer(csv_file)
    labels = ['id', 'name', 'user']
    writer.writerow(labels)
    for apk in apks:
        writer.writerow([str(apk.id), apk.name, apk.user.username])
    return csv_file


def get_zip_file(apks):
    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")
    zip_subdir = "apks.zip"
    for apk in apks:
        # Calculate path for file in zip
        fdir, fname = os.path.split(apk.apk.url)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(apk.apk.url, zip_path)
    zf.close()
    return s

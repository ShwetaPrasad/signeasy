from django.urls import path

from . import api


urlpatterns = [
    path('upload', api.upload, name='upload'),
    path('download', api.download, name='download'),
    path('delete', api.delete, name='delete'),
    path('edit', api.edit, name='edit'),
    path('share', api.share, name='share')
]
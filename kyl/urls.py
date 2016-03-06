from django.conf.urls import url,include
from kyl import views

urlpatterns = [
    url(r'^$', views.homepage , name = 'homepage'),
    url(r'^contact$', views.contact , name = 'contact'),
    url(r'^newsfeed$', views.rssfeed , name = 'rssfeed'),
]

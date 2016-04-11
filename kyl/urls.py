from django.conf.urls import url,include
from kyl import views

urlpatterns = [
    url(r'^$', views.homepage , name = 'homepage'),
    url(r'^contact$', views.contact , name = 'contact'),
    url(r'^newsfeed$', views.rssfeed , name = 'rssfeed'),
    url(r'^login$', views.user_login , name = 'login'),
    url(r'^logout$', views.user_logout , name = 'logout'),
    url(r'^signup$', views.register , name = 'signup'),
    url(r'^users/verify_email/(?P<key>.+)$', views.verify_email , name = 'signup'),
    url(r'^leadership/modi$', views.leadership_modi , name = 'leadership_modi'),
    url(r'^leadership/obama$', views.leadership_obama , name = 'leadership_obama'),
]

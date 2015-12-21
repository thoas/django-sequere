from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('sequere.urls')),
    url(r'^', include('sequere.contrib.user.urls')),
]

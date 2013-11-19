from django.conf.urls import patterns, include


urlpatterns = patterns(
    '',
    (r'^', include('sequere.urls')),
    (r'^', include('sequere.contrib.user.urls')),
)

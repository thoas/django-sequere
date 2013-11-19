from django.conf.urls import patterns, url

from .views import FollowView, UnFollowView


urlpatterns = patterns(
    '',
    url('^follow/',
        FollowView.as_view(),
        name='sequere_follow'),

    url('^unfollow/',
        UnFollowView.as_view(),
        name='sequere_unfollow')
)

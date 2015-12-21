from django.conf.urls import url

from .views import FollowView, UnFollowView


urlpatterns = [
    url('^follow/',
        FollowView.as_view(),
        name='sequere_follow'),

    url('^unfollow/',
        UnFollowView.as_view(),
        name='sequere_unfollow')
]

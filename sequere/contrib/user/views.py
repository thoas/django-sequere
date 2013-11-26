from django.views import generic
from django.utils.decorators import method_decorator
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from sequere.registry import registry

from sequere.models import (get_followers_count,
                            follow,
                            unfollow,
                            get_followings_count)

from sequere.http import JSONResponse


class BaseFollowView(generic.View):
    http_method_names = ['post']
    redirect_url_name = 'redirect_url'
    success_url = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseFollowView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.data = request.POST

        self.identifier = self.data.get('identifier', None)

        object_id = self.data.get('object_id', None)

        if not all([self.identifier, object_id]):
            return HttpResponseBadRequest()

        model = registry.identifiers.get(self.identifier, None)

        try:
            object_id = int(object_id)
        except ValueError:
            return HttpResponseBadRequest()

        if not model:
            return HttpResponseBadRequest()

        self.instance = get_object_or_404(model, pk=object_id)

        if self.instance == self.request.user:
            return HttpResponseBadRequest()

        return self.redirect(self.success(self.instance))

    def redirect(self, instance):
        if not self.request.is_ajax():
            redirect_url = self.data.get(self.redirect_url_name, self.success_url)

            if redirect_url:
                return redirect(redirect_url)

        data = {
            'followers_count': get_followers_count(self.instance),
            'followings_count': get_followings_count(self.request.user),
            '%s_followers_count' % self.identifier: get_followers_count(self.instance, self.identifier),
            '%s_followings_count' % self.identifier: get_followings_count(self.request.user, self.identifier),
        }

        return JSONResponse(data)

    def success(self, instance):
        raise NotImplementedError


class FollowView(BaseFollowView):
    def success(self, instance):
        return follow(self.request.user, instance)


class UnFollowView(BaseFollowView):
    def success(self, instance):
        return unfollow(self.request.user, instance)

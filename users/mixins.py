from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.conf import settings


class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            if self.request.is_ajax():
                return JsonResponse({'status': 401})
            else:
                return HttpResponseRedirect(settings.LOGIN_URL)

        return super().dispatch(request, *args, **kwargs)

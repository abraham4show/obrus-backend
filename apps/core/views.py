from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
class GetCSRFTokenView(View):
    def get(self, request):
        token = get_token(request)
        return JsonResponse({'csrfToken': token})
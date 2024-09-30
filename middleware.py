import os
import time
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

class AdminMessageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and request.user.is_superuser:

            site_size = self.get_site_size(settings.BASE_DIR)

            max_size = getattr(settings, 'MAX_SITE_SIZE', None)

            if max_size is not None and site_size >= max_size:
                request.admin_message = f"Warning: The site size has reached {site_size / (1024 ** 2):.2f} Mb!"
            else:
                request.admin_message = None
        else:
            request.admin_message = None

        response = self.get_response(request)
        return response

    def get_site_size(self, start_path='.'):

        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    
    def send_admin_email(self, site_size):
        
        max_size = getattr(settings, 'MAX_SITE_SIZE', None)
        
        if max_size is not None and site_size == max_size:
            send_mail(
                'Site Size Warning',
                f'The site has reached the exact size limit of {site_size / (1024 ** 2):.2f} MB!',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )


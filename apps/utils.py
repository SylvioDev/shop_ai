from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

MEDIA_URL = settings.MEDIA_URL

def get_full_image_url(request, url_image : str) -> str:
    """Returns full image url"""
    domain = get_current_site(request).domain
    output = 'http://' + domain + str(url_image)
    return output 

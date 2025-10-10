from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode

def require_password_verification(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('password_verified'):
            return view_func(request, *args, **kwargs)
        next_url = request.get_full_path()
        verify_url = reverse('verify-password')
        query_string = urlencode({'next': next_url})
        return redirect(f'{verify_url}?{query_string}')
    return _wrapped_view

MONTH = {
        1 : 'January',
        2 : 'February',
        3 : 'March',
        4 : 'April',
        5 : 'May',
        6 : 'June',
        7 : 'July',
        8 : 'August',
        9 : 'September',
        10 : 'October',
        11 : 'November',
        12 : 'December'
    }

def parse_date(raw_date):
    output = ''
    temp = raw_date.split(' ')[0].split('-')
    day = temp[2]
    month = MONTH.get(int(temp[1]))
    year = temp[0]
    output = day + ' ' + month + ' ' + year
    return output

def full_name(user : object) -> str:
    output = user.first_name + ' ' + user.last_name
    return output
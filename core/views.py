import csv
import os
from datetime import datetime, timedelta

import redis
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings

from .utils import get_equity_data


redis_instance = redis.StrictRedis(host=settings.REDIS_URL.hostname, port=settings.REDIS_URL.port, charset="utf-8",
                                   decode_responses=True)


class HomeView(TemplateView):
    template_name = "data.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update({'host': settings.LOCAL_HOST})
        return self.render_to_response(context)


class StockListView(View):

    def get(self, request, *args, **kwargs):
        data = []
        if not redis_instance.get('last_updated'):
            get_equity_data()
        redis_last_updated = datetime.strptime(redis_instance.get('last_updated'), '%d/%m/%YT%H:%M:%S')
        current_datetime = datetime.now()
        if current_datetime.hour >= 18 and current_datetime.date() != redis_last_updated.date():
            # Update Redis Server with new data if the current time is more than 18
            # and last updated date is not equal to current date
            get_equity_data()
            redis_last_updated = datetime.strptime(redis_instance.get('last_updated'), '%d/%m/%YT%H:%M:%S')
        if kwargs.get('stock_name') == 'all':
            all_keys = redis_instance.keys()
            data.extend([redis_instance.hgetall(key) for key in all_keys if key != 'last_updated'])
        else:
            if redis_instance.hgetall(kwargs.get('stock_name')):
                data.append(redis_instance.hgetall(kwargs.get('stock_name')))
        return JsonResponse({'stock_data': data, 'last_updated': redis_last_updated.strftime("%d %b, %Y %I %p IST")},
                            status=HttpResponse.status_code)


def download(request, *args, **kwargs):
    headers = ['name', 'code', 'open', 'high', 'low', 'close']
    datetime_today = datetime.today().strftime("%d-%m-%YT%H:%M:%S")
    file_path = os.path.join(settings.MEDIA_ROOT, f'stock_details_{datetime_today}.csv')
    # writer = csv.DictWriter(response, fieldnames=headers)
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)

        writer.writeheader()
        if kwargs.get('stock_name') == 'all':
            all_keys = redis_instance.keys()
            for key in all_keys:
                if key == 'last_updated':
                    continue
                writer.writerow(redis_instance.hgetall(key))
        else:
            if redis_instance.hgetall(kwargs.get('stock_name')):
                writer.writerow(redis_instance.hgetall(kwargs.get('stock_name')))
    with open(os.path.join(settings.MEDIA_ROOT, f'stock_details_{datetime_today}.csv')) as file_obj:
        response = HttpResponse(file_obj.read(), content_type='text/csv')
        response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
    return response

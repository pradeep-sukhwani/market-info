from django.urls import path, re_path

from . import views

app_name = 'core-app'

urlpatterns = [
    path('home', views.HomeView.as_view(), name='home_page'),
    re_path(r'^get_data/(?P<stock_name>[\w-]+)/$', views.StockListView.as_view(), name='stock_data'),
    re_path(r'^download_csv/(?P<stock_name>[\w-]+)$', views.download, name='download_data'),
]

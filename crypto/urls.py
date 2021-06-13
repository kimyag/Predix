from django.urls import path

from . import views
app_name = 'crypto'
urlpatterns = [
	path('', views.index, name='index'),
	path('<int:cryptocurrency_id>/',views.detail, name = 'detail')

]
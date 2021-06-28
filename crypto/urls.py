from django.urls import path
from django.contrib import admin
from django.urls import include, path

from . import views
app_name = 'crypto'
urlpatterns = [
	path('', views.MyCryptoView.as_view(), name='index'),
	path('<int:cryptocurrency_id>/',views.DetailView.as_view(), name = 'detail'),
	#path('members/',include('django.contrib.auth.urls')),
	#path('members/',include('members.urls'))
	path('search_crypto/',views.SearchCryptoView.as_view(), name = 'search-cryptos'),
	path('add_post/', views.AddPostView.as_view(), name='add_post'),
	path('news/', views.PostView.as_view(), name='view_post'),
	path('news/<int:post_id>', views.PostDetail.as_view(), name='news_detail'),
	path('like/<int:pk>',views.LikeView.as_view(), name='like_post'),
]
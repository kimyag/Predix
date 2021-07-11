from django.urls import path
from django.contrib import admin
from django.urls import include, path

from . import views
from .views import LikeView, FavCoinView

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
	path('like/<int:pk>', LikeView, name='like_post'),
	path('fav/<int:pk>', FavCoinView, name='fav_coin'),
	path('news/<int:post_id>/comment/', views.AddCommentView.as_view(), name='add_comment'),	
	path('news/<int:post_id>/delete/', views.DeletePostView.as_view(), name='delete_post'),
	path('news/<int:post_id>/edit/', views.EditPostView.as_view(), name='edit_post'),
	path('exchange/', views.ExchangeView.as_view(), name='exchange'),

]
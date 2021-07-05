from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
import json
from .models import Cryptocurrency, CryptocurrencyLog, Post, Profile, Comment, Fav
import logging
from django.utils import timezone
import requests
from datetime import timedelta
from django.views import View
from .forms import PostForm, CommentForm
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin


class SearchCryptoView(View):
	def get(self, request):	
		searched = request.GET['searched']
		print("searching for ", searched)
		cryptos = Post.objects.filter(title__icontains=searched )

		return render(request,'crypto/search_cryptos.html',{'searched':searched,'cryptos':cryptos})
	def post(self, request):
		return render(request,'crypto/search_cryptos.html',{})



class MyCryptoView(View):
	def get(self, request):
		coins = Cryptocurrency.objects.all()
		interest = Fav.objects.filter(user=request.user)[:3]
		context = {
					'best_crypto_list': coins,
					'likes': Fav.objects.filter(user=request.user).values_list('cryptocurrency_id', flat=True),
					'interest': interest
					}
		return render(request, 'crypto/index.html', context)
	


#@login_required(login_url = 'crypto:login')
class DetailView(View):
	def get(self, request, cryptocurrency_id):
		cryptocurrency = CryptocurrencyLog.objects.filter(cryptocurrency_id=cryptocurrency_id).order_by('current_time')
		headers = {
		'Accepts': 'application/json',
		'X-CMC_PRO_API_KEY': '4d958451-c172-4363-a441-d13e8c9d093f',
		}
		params = {
			'symbol' : Cryptocurrency.objects.get(id=cryptocurrency_id).symbol,
			'convert' : 'USD'
		}
		url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
		jsonData = requests.get(url, params=params, headers=headers).json()
		labels = []
		data = []


		for ct in cryptocurrency:
			labels.append(ct.current_time.strftime("%Y-%m-%d %H:%M"))
			data.append(ct.current_price)
		data = json.dumps(data)
		context = {
			'labels': json.dumps(labels),
			'data': data,
			'name':Cryptocurrency.objects.get(id = cryptocurrency_id).name,
			'jsonData':jsonData['data'][Cryptocurrency.objects.get(id=cryptocurrency_id).symbol],
			'news': Post.objects.filter(title__contains = Cryptocurrency.objects.get(id=cryptocurrency_id).name)
			}
		return render(request, 'crypto/detail.html', context)
	
class AddPostView(View):
	def post(self, request):
		form = PostForm(request.POST)
		if form.is_valid():
			form.save()
		context = {'form':form}
		return redirect('crypto:index')
	def get(self, request):
		form = PostForm()
		context = {'form':form}
		return render(request, 'crypto/add_post.html', context)

class AddCommentView(View):
	def post(self, request,post_id):
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = Comment(name=request.POST.get('name'), body=request.POST.get('body'), post_id=post_id)
			comment.save()
		context = {'form':form}
		return HttpResponseRedirect(reverse('crypto:news_detail', args=[str(post_id)]))
	def get(self, request, post_id):
		form = CommentForm()
		context = {'form':form}
		return render(request, 'crypto/add_comment.html', context)

class PostView(View):
	def get(self, request):
		news = Post.objects.all()
		context = {'news':news}
		return render(request, 'crypto/news.html', context)

class PostDetail(View):
	def get(self, request, post_id):
		news = Post.objects.get(id=post_id)
		liked = False
		if news.likes.filter(id=self.request.user.id).exists():
			liked = True
		context = {
		'news':news,
		'comments':  Comment.objects.filter(post=news),
		'liked':liked
		}
		return render(request, 'crypto/news_detail.html', context)


def LikeView(request,pk):
		post = get_object_or_404(Post, id=request.POST.get('post_id'))
		liked = False
		if post.likes.filter(id=request.user.id).exists():
			post.likes.remove(request.user)
			liked = False
		else:
			post.likes.add(request.user)
			post.likes.set = True
		return HttpResponseRedirect(reverse('crypto:news_detail', args=[str(pk)]))

def FavCoinView(request,pk):
		crypto = get_object_or_404(Cryptocurrency, id=request.POST.get('Cryptocurrency_id'))
		liked = False
		if Fav.objects.filter(cryptocurrency_id=crypto.id).exists():
			Fav.objects.filter(cryptocurrency_id=crypto.id).delete()
			liked = False
		else:
			fav = Fav(user=request.user, cryptocurrency_id=crypto.id )
			fav.save()
		coins = Cryptocurrency.objects.all()

		return HttpResponseRedirect(reverse('crypto:index'))
		#return render(request,'crypto/index.html', context)



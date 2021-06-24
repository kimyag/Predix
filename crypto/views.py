from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
import json
from .models import Cryptocurrency, CryptocurrencyLog, Post
import logging
from django.utils import timezone
import requests
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.views import View
from .forms import PostForm


class search_cryptos(View):
	def post(self, request):	
		searched = request.POST['searched']
		cryptos = Cryptocurrency.objects.filter(name__contains = searched )
		return render(request,'crypto/search_cryptos.html',{'searched':searched,'cryptos':cryptos})
	def get(self, request):
		return render(request,'crypto/search_cryptos.html',{})



class MyCryptoView(View):
	def get(self, request):
		headers = {
		'Accepts': 'application/json',
		'X-CMC_PRO_API_KEY': '4d958451-c172-4363-a441-d13e8c9d093f',
		}
		params = {
			'start' : '1',
			'limit' : '50',
			'convert' : 'USD'
		}
		url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
		json = requests.get(url, params=params, headers=headers).json()
		coins = json['data']

		for coin in coins:
			rank = coin['cmc_rank']
			name = coin ['name']
			symbol = coin['symbol']
			price = coin ['quote']['USD']['price']
			if Cryptocurrency.objects.filter(symbol = symbol).exists():
				Cryptocurrency.objects.filter(symbol = symbol).update(rank=rank, price = price)
				current_time = timezone.now()
				current_price = price
				cryptocurrency = Cryptocurrency.objects.get(symbol = symbol)
				cryptolog = CryptocurrencyLog(name = name, current_time = current_time, current_price = current_price, cryptocurrency = cryptocurrency)
				cryptolog.save()


			else:
				c = Cryptocurrency(rank=rank, name=name, symbol=symbol, price=price)
				c.save()
				current_time = timezone.now()
				current_price = price
				cryptolog = CryptocurrencyLog(name = name, current_time = current_time, current_price = current_price, cryptocurrency = c)
				cryptolog.save()
		coins = Cryptocurrency.objects.all()
		context = {
			'best_crypto_list': coins
			}
		return render(request, 'crypto/index.html', context)
	


#@login_required(login_url = 'crypto:login')
class detail(View):
	def get(self, request, cryptocurrency_id):
		cryptocurrency = CryptocurrencyLog.objects.filter(cryptocurrency_id = cryptocurrency_id)
		headers = {
		'Accepts': 'application/json',
		'X-CMC_PRO_API_KEY': '4d958451-c172-4363-a441-d13e8c9d093f',
		}
		params = {
			'symbol' :Cryptocurrency.objects.get(id = cryptocurrency_id).symbol,
			'convert' : 'USD'
		}
		url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
		jsonData = requests.get(url, params=params, headers=headers).json()
		labels = []
		data = []


		count = 0
		for ct in cryptocurrency:
			if count % 2==0:
				data.append(ct.current_price*100)
			else:
				labels.append(ct.current_time.strftime("%Y-%m-%d %H:%M"))
				data.append(ct.current_price*100)
			count += 1
		context ={
			'labels': labels,
			'data': data,
			'name':Cryptocurrency.objects.get(id = cryptocurrency_id).name,
			'jsonData':jsonData['data'][Cryptocurrency.objects.get(id = cryptocurrency_id).symbol]
			}
		return render(request, 'crypto/detail.html', context)
	#cryptocurrency = CryptocurrencyLog.objects.filter(cryptocurrency_id = cryptocurrency_id, current_time__gte=timezone.now()-timedelta(hours=24))
	
class AddPostView(View):
	def post(self, request):
		form = PostForm(request.POST)
		if form.is_valid():
			form.save()
		context = {'form':form}
		return render(request, 'crypto/add_post.html', context)

class PostView(View):
	def get(self, request):
		news = Post.objects.all()
		print(news)
		context = {'news':news}
		return render(request, 'crypto/news.html', context)

class PostDetail(View):
	def get(self, request, post_id):
		news = Post.objects.get(id = post_id)
		print(news)
		context = {
		'author': news.author,
		'title':news.title,
		'body':news.body,
		'post_date':news.post_date,
		'likes':news.likes
		}
		return render(request, 'crypto/news_detail.html', context)


	
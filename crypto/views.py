from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, redirect
import json
from .models import Cryptocurrency, CryptocurrencyLog, Post, Profile, Comment, Fav, Entity
import logging
from django.utils import timezone
import requests
from datetime import timedelta
from django.views import View
from .forms import PostForm, CommentForm
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
import numpy
from sklearn.linear_model import LinearRegression



class SearchCryptoView(View):
	def get(self, request):	
		searched = request.GET['searched']
		cryptos = Post.objects.filter(title__icontains=searched )

		return render(request,'crypto/search_cryptos.html',{'searched':searched,'cryptos':cryptos})
	def post(self, request):
		return render(request,'crypto/search_cryptos.html',{})



class MyCryptoView(View):
	def get(self, request):
		# TODO: Keep the cryptocurrency and the price in a map to track it later and save to the database
		# TODO: Send to predicted prices to the front-end to display
		# predicted = model.predict(test_data)
		# each feature a column = time
		# each coin a sample = a row
		## [a1,a2,a3,a4] coin a's price over time
		## [b1,b2,b3,b4] coin b's price over time
		## ...
		##
		X = []
		training_Y = []
		Maxs = []
		# Keep max of each coin to also normalize the Y
		# calculate X
		all_cryptos = Cryptocurrency.objects.order_by('rank')


		for crypto in all_cryptos:
			# will ignore the data if the historical data size is less that 25
			# will use last 25 data for training
			if 25>len(CryptocurrencyLog.objects.filter(cryptocurrency=crypto).values_list('current_price', flat=True)):
				continue
			coin_price_over_time = CryptocurrencyLog.objects.filter(cryptocurrency=crypto).order_by('-current_time').values_list('current_price', flat=True)[:25]
			coin_price_over_time = list(coin_price_over_time)
			# Normalization- from sklearn import preprocessing can be used too
			mx = max(coin_price_over_time)
			Maxs.append(mx)
			coin_price_over_time = [x / mx for x in coin_price_over_time]
			X.append(coin_price_over_time)
			# calculate Y
			training_Y.append(crypto.price)
		# found X, convert to numpy
		X = numpy.array(X)


		temp = []

		for i, v in enumerate(training_Y):
			temp.append(v/Maxs[i])
		training_Y = temp
		training_Y = numpy.array(training_Y)


		model = LinearRegression(normalize = True)
		#training using 25 coins
		model.fit(X[:25], training_Y[:25])
		#Predict
		predicted = model.predict(X[25:])
		print("Predicted array is:", predicted, "\n\n######\n\nActual array is:",training_Y[25:])
		####################################################################################
		# Q:The result is between [0:1] should I multiply it by the max value to ge the correnct result?!
		####################################################################################
		# Denormalization
		result = []
		print("------AFTER DENORMALIZATION-------")
		for i,v in enumerate(predicted):
			result.append(v*Maxs[i])
			print(v, v*Maxs[i],"\n")

		#________________________________________
		coins = Cryptocurrency.objects.all()
		user=request.user
		if request.user.is_authenticated:
			interest = Fav.objects.filter(user=request.user)[:3]
			likes =Fav.objects.filter(user=request.user).values_list('cryptocurrency_id', flat=True)
		else:
			likes = []
			interest = []
		context = {
					'best_crypto_list': coins,
					'likes': likes,
					'interest': interest
					}
		return render(request, 'crypto/index.html', context)
	


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
	
class AddPostView(LoginRequiredMixin, View):
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
		user = request.user
		if request.method == 'POST':
			post_id = request.POST['post_id']
			post = get_object_or_404(Post, id=post_id)
			liked = False
			if post.likes.filter(id=request.user.id).exists():
				post.likes.remove(request.user)
				liked = False
			else:
				post.likes.add(request.user)
				post.likes.set = True
		context = {
					'liked':post.likes.filter(id=request.user.id).exists(),
					'total_likes': post.total_likes
					}
		return JsonResponse({'liked':post.likes.filter(id=request.user.id).exists()})


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


class DeletePostView(LoginRequiredMixin, View):
	def get(self, request, post_id):
		post = Post.objects.get(id=post_id)
		if post.author != request.user:
			raise Http404
		post.delete()
		return HttpResponseRedirect(reverse('crypto:index'))

class EditPostView(LoginRequiredMixin, View):
	def get(self, request, post_id):
		post = Post.objects.get(id=post_id)
		form = PostForm(instance = post)
		if post.author != request.user:
			raise Http404
		context = {'form':form}
		return render(request, 'crypto/edit_post.html', context)

	def post(self, request, post_id):
		form = PostForm(request.POST)
		if form.is_valid():
			post = Post.objects.get(id=post_id)
			if post.author != request.user:
				raise Http404
			post.delete()
			form.save()
		context = {'form':form}
		return redirect('crypto:index')

class ExchangeView(LoginRequiredMixin, View):
	def get(self, request):
		user_entities = Entity.objects.filter(user=request.user)
		total = 0
		for entity in user_entities:
			total += entity.cryptocurrency.price * entity.amount
		context = {
			'user_entities':user_entities,
			'total':total,
			'crypto_list': Cryptocurrency.objects.all()
		}
		return render(request, 'crypto/exchange.html',context )
	def post(self, request):
		user_entities = Entity.objects.filter(user=request.user)
		return render(request, 'crypto/exchange.html', {'user_entities':user_entities})

class BuyCryptoView(LoginRequiredMixin, View):
	def get(self, request):
			amount = request.GET['amount']
			crypto = Cryptocurrency.objects.get(id=request.GET['cryptos'])
			total=float(crypto.price)*float(amount)
			if Entity.objects.filter(cryptocurrency_id=crypto.id,user=request.user).exists():
				entity = Entity.objects.filter(cryptocurrency_id=crypto.id,user=request.user)
				entity2 = Entity.objects.get(cryptocurrency_id=crypto.id,user=request.user)
				entity.update(total=total+entity2.total,amount=float(amount)+entity2.amount)
				return redirect('crypto:exchange')
			else:
				entity = Entity(user=request.user, cryptocurrency=crypto, amount=amount, total=total)
				entity.save()
				print(entity.cryptocurrency.name,"BOUGHT")
				user_entities = Entity.objects.filter(user=request.user)
				return redirect('crypto:exchange')

class SellCryptoView(LoginRequiredMixin, View):
	def get(self, request):
			amount = request.GET['amount']
			crypto = Cryptocurrency.objects.get(id=request.GET['cryptos'])
			entity = Entity.objects.get(cryptocurrency_id=crypto.id,user=request.user)
			entity1 = Entity.objects.filter(cryptocurrency_id=crypto.id,user=request.user)
			if float(amount) < entity.amount:
				new_amount = entity.amount-float(amount)
				new_total = new_amount*crypto.price
				entity1.update(amount=new_amount,total=new_total)
			elif float(amount) == entity.amount:
				entity1.delete()
			else:
				print("you have not enough money")


			return redirect('crypto:exchange')



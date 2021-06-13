from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json
from .models import Cryptocurrency, CryptocurrencyLog
import logging
from django.utils import timezone
#import apikey
import requests
def search_cryptocurrency(request):
	return render(request,'events/search_venues.html',{})

def index(request):
	headers = {
	'Accepts': 'application/json',
	'X-CMC_PRO_API_KEY': '4d958451-c172-4363-a441-d13e8c9d093f',
	}
	params = {
		'start' : '1',
		'limit' : '100',
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
			Cryptocurrency.objects.filter(symbol = symbol).update(price = price)
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
	print(coins)
	context = {'best_crypto_list': coins}
	return render(request, 'crypto/index.html', context)
#TODO: visualize historical data
def detail(request, cryptocurrency_id):
	print(Cryptocurrency.objects.get(id = cryptocurrency_id).name)
	cryptocurrency = CryptocurrencyLog.objects.filter(cryptocurrency_id = cryptocurrency_id)
	print(cryptocurrency)
	return render(request, 'crypto/detail.html', {'cryptocurrency': cryptocurrency})
#TODO:  add users to comment,like, upvote?!
#TODO:  fix admin


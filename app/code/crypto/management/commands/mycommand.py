from django.core.management.base import BaseCommand
from crypto.models import Cryptocurrency, CryptocurrencyLog
import requests
from django.utils import timezone


class Command(BaseCommand):
	def handle(self, *args, **options):
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
				Cryptocurrency.objects.filter(symbol = symbol).update(rank=rank, price=price)
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


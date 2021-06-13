from django.db import models

class Cryptocurrency(models.Model):
	rank = models.IntegerField()
	name = models.CharField(max_length = 20)
	symbol = models.CharField(max_length= 5)
	price =  models.FloatField()
	#potential_price = models.FloatField()
	#general_info = models.CharField(max_length = 500)
	def __str__(self):
		s = str(self.rank)+" "+self.name+" "+self.symbol+" "+str(self.price)
		return s

class CryptocurrencyLog(models.Model):
	name = models.CharField(max_length=20)
	current_time = models.DateTimeField()
	current_price = models.FloatField()
	cryptocurrency = models.ForeignKey(Cryptocurrency, null= True, on_delete = models.CASCADE)
	def __str__(self):
		s = self.name+"\t"+str(self.current_time)+"\t"+str(self.current_price)+"\n"
		return s

class Tweet(models.Model):
	publisher = models.CharField(max_length = 50)
	context = models.CharField(max_length = 200)
	date = models.DateTimeField('date published')
	def __str__(self):
		return self.context

class News(models.Model):
	publisher = models.CharField(max_length = 50)
	date = models.DateTimeField('date published')
	context = models.CharField(max_length = 200)
	def __str__(self):
		return self.context

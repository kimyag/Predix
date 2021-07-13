from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField



class Cryptocurrency(models.Model):
	rank = models.IntegerField()
	name = models.CharField(max_length = 100)
	symbol = models.CharField(max_length= 10)
	price =  models.FloatField()
	favs = models.ManyToManyField(User, related_name = 'crypto_cryptocurrency')
	#potential_price = models.FloatField()
	#general_info = models.CharField(max_length = 500)
	def __str__(self):
		s = str(self.rank)+" "+self.name+" "+self.symbol+" "+str(self.price)
		return s

class CryptocurrencyLog(models.Model):
	name = models.CharField(max_length=100)
	current_time = models.DateTimeField()
	current_price = models.FloatField()
	cryptocurrency = models.ForeignKey(Cryptocurrency, null= True, on_delete = models.CASCADE)
	def __str__(self):
		s = self.name+"\t"+str(self.current_time)+"\t"+str(self.current_price)+"\n"
		return s

class Post(models.Model):
	title = models.CharField(max_length=255)
	header_image = models.ImageField(null=True, blank=True, upload_to="images/")
	title_tag = models.CharField(max_length=255)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	body = RichTextField(blank=True, null = True)
	post_date = models.DateField(auto_now_add=True)
	category = models.CharField(max_length=255, default='coding')
	snippet = models.CharField(max_length=255)
	likes = models.ManyToManyField(User, related_name = 'crypto_post')

	def total_likes(self):
		return self.likes.count()

	def __str__(self):
		return self.title + ' | ' + str(self.author)


class Profile(models.Model):
	user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
	bio = models.TextField()
	profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile/")
	website_url = models.CharField(max_length=255, null=True, blank=True)
	owned_dollar = models.FloatField(default=0)


	def __str__(self):
		return str(self.user)

class Entity(models.Model):
	user = models.ForeignKey(User, related_name='entities',on_delete=models.CASCADE)
	cryptocurrency = models.ForeignKey(Cryptocurrency, related_name='entities',on_delete=models.CASCADE)
	amount = models.FloatField(default=0)
	total = models.FloatField(default=0)


class Comment(models.Model):
	post = models.ForeignKey(Post,null= True,  on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	body = RichTextField(blank=True, null = True)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '%s - %s' % (self.name, self.body)

class Fav(models.Model):
	user = models.ForeignKey(User, related_name='favorites',on_delete=models.CASCADE)
	cryptocurrency = models.ForeignKey('Cryptocurrency', related_name='favorites',on_delete=models.CASCADE)




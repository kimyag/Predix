from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse



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

class Post(models.Model):
	title = models.CharField(max_length=255)
	header_image = models.ImageField(null=True, blank=True, upload_to="images/")
	title_tag = models.CharField(max_length=255)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	body = models.TextField()
	post_date = models.DateField(auto_now_add=True)
	category = models.CharField(max_length=255, default='coding')
	snippet = models.CharField(max_length=255)
	likes = models.ManyToManyField(User, related_name='blog_posts')

	def total_likes(self):
		return self.likes.count()

	def __str__(self):
		return self.title + ' | ' + str(self.author)

	def get_absolute_url(self):
		#return reverse('article-detail', args=(str(self.id)) )
		return reverse('index')

class Profile(models.Model):
	user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
	bio = models.TextField()
	profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile/")
	website_url = models.CharField(max_length=255, null=True, blank=True)
	#fav_coins

	def __str__(self):
		return str(self.user)

	def get_absolute_url(self):
		return reverse('index')

class Comment(models.Model):
	post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	body = models.TextField()
	date_added = models.DateTimeField(auto_now_add=True)
	post = models.ForeignKey(Post, null= True, on_delete = models.CASCADE)
	profile = models.ForeignKey(Profile, null= True, on_delete = models.CASCADE)

	def __str__(self):
		return '%s - %s' % (self.post.title, self.name)

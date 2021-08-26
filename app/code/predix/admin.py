from django.contrib import admin
from .models import Post, Cryptocurrency, CryptocurrencyLog, Profile, Comment
#from .Contact import Contact

admin.site.register(Post)
admin.site.register(Cryptocurrency)
admin.site.register(CryptocurrencyLog)
admin.site.register(Profile)
admin.site.register(Comment)
#admin.site.register(Contact)



from django.contrib import admin
from .models import User, Comment, Category, Bid, Watchlist, Auction

# Register your models here.

admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Watchlist)
admin.site.register(Auction)
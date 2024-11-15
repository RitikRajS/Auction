from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    pass


class Category(models.Model):
    category_name = models.CharField(max_length=200)
    category_image= models.URLField(max_length=5000 , blank=True) 

    def __str__(self):
        return(self.category_name)


class Auction(models.Model):
    title = models.CharField(max_length=100)
    description= models.CharField(max_length=1000)
    image_url= models.URLField(max_length=5000 , blank=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=datetime.now)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    active = models.BooleanField(default= True, help_text='Represents whether the listing is active or not', verbose_name='status')


    def __str__(self):
        return(f"{self.seller.username} posted a new listing of {self.title} at {self.date}")



class Watchlist(models.Model):
    watcher = models.OneToOneField(User, on_delete=models.CASCADE)
    watched_item = models.ManyToManyField(Auction, related_name="watched_items" )

    def __str__(self):

        watched_list= self.watched_item.all() # gets all the watched_item 
        title_name = [] # empty list where we append all the title within our list 

        for item in watched_list: # 
            title_name.append(item.title)

        items = ", ".join(title_name)

        if items:
            return(f"{self.watcher.username} is watching {items}")
        else:
            return(f"The watchlist of {self.watcher.username} is empty")


class Comment(models.Model):
    comment = models.TextField(max_length=1500)
    comment_date = models.DateTimeField(default=datetime.now)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE) 
    commented_item= models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return(f"{self.commenter.username} added a comment to {self.commented_item.title}")

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bidding_item = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return(f"{self.bidder.username} added a bid of {self.bid_amount} to {self.bidding_item.title}")


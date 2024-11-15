from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Auction, Category, Comment, Watchlist, Bid
from .forms import AuctionForm, CommentForm, WatchlistForm, BidForm, ActiveForm


def watchlist_count(request):

    if request.user.is_authenticated:
        user_object, created = Watchlist.objects.get_or_create(watcher= request.user)
        return user_object.watched_item.count()
    return None



def get_context(request, auction_details):
    """
    Will be used to get the auction context to avoid repetation.
    Will accept an auction object, and will return all the comments, bids,
    watcher associated with it.
    """

    # empty forms 
    comment = CommentForm()
    watchlist_form = WatchlistForm()
    active_form = ActiveForm()

    # bid forms and content 
    bidding_details = auction_details.bid_set.all()
    bid_form = BidForm(auction= auction_details)

    #comments for each item
    comment_details = Comment.objects.filter(commented_item= auction_details)

    # user watchlist 
    if request.user.is_authenticated:
        user_object, created = Watchlist.objects.get_or_create(watcher= request.user)
        in_watchlist = auction_details in user_object.watched_item.all()
        watchlist_count_value= watchlist_count(request)
    else:
        user_object= False
        in_watchlist = None
        watchlist_count_value = None


    # highest bidder
    if auction_details.active == False:
        winner = Bid.objects.filter(bidding_item = auction_details).order_by('-bid_amount').first()
    else:
        winner = None

    # highest bid
    highest_bid =Bid.objects.filter(bidding_item = auction_details).order_by('-bid_amount').first()
    current_price = highest_bid.bid_amount if highest_bid else auction_details.price 

    return {
        "auction": auction_details, 
        "comment":comment, 
        "item_comments":comment_details, 
        "watchlist_form": watchlist_form, 
        "in_watchlist": in_watchlist, 
        "bidform":bid_form, 
        "bids":bidding_details,
        "active": active_form, 
        "winner": winner,
        "count" : watchlist_count_value,
        "current_price": current_price,
        "categories":Category.objects.all()
    }


def index(request):

    auctions = Auction.objects.filter(active=True)
    auctions_prices = []

    for auction in auctions:
        highest_bid = auction.bid_set.order_by('-bid_amount').first()
        current_price = highest_bid.bid_amount if highest_bid else auction.price 
        auctions_prices.append({"auction": auction, 
                                "current_price": current_price})
    

    return render(request, "auctions/index.html", {
        "auctions_prices": auctions_prices, 
        "count": watchlist_count(request),
        "categories":Category.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            # if next exists, redirect to next, or redirect to the index page
            next_url = request.POST.get('next', reverse("index")) 
            return HttpResponseRedirect(next_url)
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):

    """
    To create a new listing 
    """

    if request.method == "GET":

        return render(request, "auctions/create.html", {
            "form": AuctionForm(),
            "count": watchlist_count(request),
            "categories":Category.objects.all()
        })
    
    elif request.method == "POST":

        form = AuctionForm(request.POST)

        if form.is_valid():
            auction =form.save(commit= False)
            auction.seller = request.user 
            auction.save()
            return HttpResponseRedirect(reverse('index'))
            

def auction(request, item):
    
    if request.method == "GET":
        auction_details = Auction.objects.get(id= item)

        context = get_context(request, auction_details)
        
        return render(request, "auctions/auction.html", context)


def category(request, category):

    if request.method == "GET":
        category_object = get_object_or_404(Category, category_name = category)
        items = Auction.objects.filter(category = category_object)
        print(items)

        for item in items:
            highest_bid =Bid.objects.filter(bidding_item = item).order_by('-bid_amount').first()
            item.current_price = highest_bid.bid_amount if highest_bid else item.price 

        return (render(request, "auctions/category.html", {
            "items":items, 
            "title":category, 
            "count": watchlist_count(request)
        }))
    
def categories(request):

    if request.method == "GET":
        items = Category.objects.all()
        return render(request, "auctions/categories.html", {
            "items":items,
            "count": watchlist_count(request)
        })


def comment(request, item): 

    if request.method == "POST":

        if request.user.is_authenticated:

            form= CommentForm(request.POST)
            auction_details = get_object_or_404(Auction, title= item)

            if form.is_valid():

                comment_content = form.save(commit=False)
                comment_content.commenter = request.user
                comment_content.commented_item = auction_details
                comment_content.save()

                return HttpResponseRedirect(reverse('auction', args=[auction_details.id]))
            
            else:

                context = get_context(request, auction_details)
                context['comment'] = form
                return render(request, "auctions/auction.html", context)
            
        else:

            return HttpResponseRedirect(f"{reverse('login')}?next={reverse('comment', args=[auction_details.id])}")


@login_required
def watchlist(request):

    if request.method == "GET":
        user_object, created = Watchlist.objects.get_or_create(watcher= request.user)
        interested_items = user_object.watched_item.all()

        return render (request, "auctions/watchlist.html", {
            "items": interested_items, 
            "count": watchlist_count(request),
            "categories":Category.objects.all()
        })

@login_required 
def watchlist_update(request, item):
    
    auction_details = Auction.objects.get(id=item)
    user_object, created = Watchlist.objects.get_or_create(watcher= request.user)
    

    if request.method == "POST":

        # if the checkbox is ticked, add the item to the watchlist
        if auction_details in user_object.watched_item.all():
            user_object.watched_item.remove(auction_details)
            messages.warning(request, f"{auction_details.title} has been removed from your watchlist")

        else:
            user_object.watched_item.add(auction_details)
            messages.success(request, f"{auction_details.title} has been added from your watchlist")

        return HttpResponseRedirect(reverse('auction', args=[item]))
    

    else:

        context = get_context(request, auction_details)
        context['watchlist_form'] = WatchlistForm(initial = {"watch": auction_details in user_object.watched_item.all()})
        return render(request, "auctions/auction.html", context)



@login_required
def bid(request, item):

    auction_details = Auction.objects.get(id=item)
    
    if request.method == "POST":
        
        form = BidForm(request.POST, auction= auction_details)

        if form.is_valid():

            bid_content = form.save(commit=False)
            bid_content.bidder = request.user
            bid_content.bidding_item = auction_details
            bid_content.save()
            messages.success(request, f"A bid of £{bid_content.bid_amount} has been placed")
            return HttpResponseRedirect(reverse('auction', args=[item]))
        
        else:

            context = get_context(request, auction_details)
            context['bidform'] = form
            return render(request, "auctions/auction.html", context)


def active(request, item):

    auction_details = Auction.objects.get(id=item)

    if request.method=="POST":
        auction_details.active = False
        messages.success(request, f"{auction_details.title} has been removed from Active Listing")
        auction_details.save()
        winner = Bid.objects.filter(bidding_item = auction_details).order_by('-bid_amount').first()
        if winner is not None:
            messages.success(request, f"{auction_details.title} is now closed. The winner of this auction is {winner.bidder} with an amount of {winner.bid_amount}.")
        else:
            messages.warning(request, f"{auction_details.title} is unsold. No bids have been placed on this item.")

        return HttpResponseRedirect(reverse('auction', args=[item]))


def closed(request):

    if request.method == "GET":

        auction_details = Auction.objects.filter(active=False)

        for auction in auction_details:

            winning_bid= Bid.objects.filter(bidding_item = auction).order_by('-bid_amount').first()
            auction.winning_bid = winning_bid

        return render(request, "auctions/inactive.html", {
            "items": auction_details,
            "count": watchlist_count(request),
            "categories":Category.objects.all()
        })







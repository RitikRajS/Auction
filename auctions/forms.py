from .models import User, Comment, Category, Bid, Watchlist, Auction
from django.forms import forms, ModelForm
from django import forms 

class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields=["title", "description", "image_url", "price", "category"] 
        widgets = {
            "title":forms.TextInput(attrs={"placeholder":"Title", "class":"form-control title-field"}), 
            "description":forms.Textarea(attrs={"placeholder":"Description", "class":"form-control description-field"}), 
            "image_url":forms.URLInput(attrs={"placeholder":"Image URL", "class":"form-control image-field"}),
            "price":forms.NumberInput(attrs={"placeholder":"Price", "class":"form-control price-field"}), 
            "category":forms.Select(attrs={"placeholder":"Cateogry", "class":"form-control category-field"})
        }
        labels = {
            "title":"Title", 
            "description": "Description", 
            "image_url":"Image URL", 
            "price": "Price", 
            "category":"Category"
        }
        

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields=["comment"] 
        widgets = {
            "comment":forms.Textarea(attrs={"placeholder":"Comment", "class":"form-control comment-field"}), 
        }
        labels= {
            "comment":""
        }


        # Validating the form is not empty

    def clean_comment(self):
        comment_content = self.cleaned_data.get("comment")

        if comment_content is None or comment_content== "":
            raise forms.ValidationError("Comment Form cannot be empty")
        return comment_content
            

class WatchlistForm(forms.Form):
    # True or False 
    watch = forms.BooleanField(required=False, label= "Watchlist", widget=forms.HiddenInput())


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["bid_amount"]
        widgets = {
            "bid_amount":forms.NumberInput(attrs={"placeholder":"Enter the Amount", "class":"form-control bid-field"}), 
        }
        labels= {
            "bid_amount":""
        }


    def __init__(self, *args, **kwargs):
        self.auction = kwargs.pop('auction', None)
        super().__init__(*args, **kwargs)

    
    def clean_bid_amount(self):
        bid_amount = self.cleaned_data.get('bid_amount') # retrives the bid value from the form
        starting_price = self.auction.price # the initial price of the item via the auction object
        highest_bid = self.auction.bid_set.order_by('-bid_amount').first()

        if highest_bid:
            highest_amount = highest_bid.bid_amount # trying to access the bid_amount field from the highest_bid object
            if bid_amount <= highest_amount:
                raise forms.ValidationError(f"Your current bid of {bid_amount} should be higher than {highest_amount}")
            
        elif bid_amount <= starting_price:
            raise forms.ValidationError(f"Your current bid of {bid_amount} should be higher than {starting_price}")
        
        return bid_amount



class ActiveForm(forms.Form):
    # True or False 
    active = forms.BooleanField(required=False, label= "Active_Listing", widget=forms.HiddenInput())


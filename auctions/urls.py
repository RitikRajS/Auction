from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"), 
    path("create", views.create, name="create"), 
    path("auction/<int:item>", views.auction, name="auction"),
    path("category/<str:category>", views.category, name="category"), 
    path("categories", views.categories, name="categories"), 
    path("comment/<str:item>", views.comment, name="comment"), 
    path("watchlist", views.watchlist, name="watchlist"), 
    path("watchlist/update/<int:item>", views.watchlist_update, name="watchlist_update"), 
    path("auction/bid/<int:item>", views.bid, name="bid"), 
    path("auction/update/<int:item>", views.active, name="active"),
    path("closed_auctions", views.closed, name="closed_auction") 
]

from django.urls import path
from shop.views import *

urlpatterns = [
    path("", index,  name="home"),
    path("categories/<int:pk>/", category,  name="category"),
    path("contact/", contact,  name="contact"),
    path("signup/", signup,  name="signup"),
    path("signin/", signin,  name="signin"),
    path("signout/", signout,  name="signout"),
    path("likes/", likes,  name="likes"),
    path("likes/<int:pk>/", like_toggle,  name="like"),
    path("products/<int:pk>/", detail,  name="detail"),
    path("basket/", basket,  name="basket"),
    path("basket_add/<int:pk>/", basket_add,  name="basket_add"),
    path("basket_update/<int:pk>/", basket_update,  name="basket_update"),
    path("basket_remove/<int:pk>/", basket_remove,  name="basket_remove"),
    path("search/", search,  name="search"),
]
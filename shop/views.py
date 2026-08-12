from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q, Min
from django.shortcuts import render, redirect
from random import sample
from shop.forms import SignUpForm, SignInForm
from shop.models import *


def index(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    offers = Offer.objects.all()
    sponsors = Sponsor.objects.all()
    products = list(Product.objects.all())
    featured_product = sample(products, min(8, len(products)))
    context = {
        "categories": categories,
        "subcategories": subcategories,
        "offers": offers,
        "sponsors": sponsors,
        "featured_products": featured_product,
        "recently_products": Product.objects.order_by('-id')[:8],
    }
    return render(request, "shop/index.html", context)

def category(request, pk):
    cat = Category.objects.get(pk=pk)
    products = Product.objects.filter(category=cat)
    sort_fields = request.GET.get('sort')
    price_fields = request.GET.getlist('price')
    color_fields = request.GET.getlist('color')
    size_fields = request.GET.getlist('size')
    if color_fields:
        products = products.filter(types__color__in=color_fields)
    if size_fields:
        products = products.filter(types__size__in=size_fields)
    if sort_fields:
        products = products.annotate(price=Min("types__price")).order_by(sort_fields)
    if price_fields:
        price_list = {
            "0-100": (0, 100),
            "100-200": (100, 200),
            "200-300": (200, 300),
            "300-400": (300, 400),
            "400-500": (400, 500),
        }
        query = Q()
        for key in price_fields:
            if key in price_list:
                low, high = price_list[key]
                query |= Q(types__price__gte=low, types__price__lte=high)
        if query:
            products = products.filter(query)
    products = products.distinct()
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    obj_list = paginator.get_page(page_number)
    context = {
        "products": obj_list
    }
    return render(request, "shop/category.html", context)

def contact(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        Contact.objects.create(full_name=full_name, email=email, subject=subject, message=message)
    return render(request, "shop/contact.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("home")
    else:
        form = SignUpForm()
    context = {
        "form": form
    }
    return render(request, "shop/signup.html", context)


def signin(request):
    if request.method == "POST":
        form = SignInForm(data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
    else:
        form = SignInForm()
    context = {
        "form": form
    }
    return render(request, "shop/signin.html", context)


def signout(request):
    logout(request)
    return redirect("signin")


def likes(request):
    user = request.user if request.user.is_authenticated else None
    likes = Like.objects.filter(user=user)
    products = [like.product for like in likes]
    context = {
        "products": products
    }
    return render(request, "shop/likes.html", context)


def like_toggle(request, pk):
    user = request.user if request.user.is_authenticated else None
    product = Product.objects.get(pk=pk)
    if product:
        likes = Like.objects.filter(user=user)
        if product in [like.product for like in likes]:
            liked_product = Like.objects.filter(user=user, product=product)
            liked_product.delete()
        else:
            Like.objects.create(user=user, product=product)
    next_page = request.META.get("HTTP_ERROR", "home")
    return redirect(next_page)


def detail(request, pk):
    products = list(Product.objects.exclude(pk=pk))
    product = Product.objects.get(pk=pk)
    data = sample(products, min(8, len(products)))

    context = {
        "product": product,
        "similar": data,
    }
    return render(request, "shop/detail.html", context)


def basket(request):
    user = request.user if request.user.is_authenticated else None
    products = Basket.objects.filter(user=user)
    total_sale = sum([item.get_total_sale() for item in products])
    total_price = sum([item.get_total_price() for item in products])
    total_quantity = sum([item.quantity for item in products])
    benefit = total_price - total_sale
    context = {
        "products": products,
        "total_sale": total_sale,
        "total_price": total_price,
        "total_quantity": total_quantity,
        "benefit": benefit,
    }
    return render(request, "shop/basket.html", context)


def basket_add(request, pk):
    user = request.user if request.user.is_authenticated else None
    product = Product.objects.get(pk=pk)
    quantity = request.POST.get("quantity")
    if quantity:
        quantity = int(quantity)
    else:
        quantity = 1
    basket, created = Basket.objects.get_or_create(product=product, user=user)
    if not created:
        basket.quantity += quantity
    else:
        basket.quantity = quantity
        basket.save()
    next_page = request.META.get("HTTP_REFERER", "home")
    return redirect(next_page)


def basket_update(request, pk):
    product = Basket.objects.get(pk=pk)
    if request.method == "POST":
        action = request.POST.get('action')
        if action == '+':
            product.quantity += 1
        else:
            if product.quantity > 1:
                product.quantity -= 1
            else:
                product.delete()
                return redirect("basket")
        product.save()
    return redirect("basket")


def basket_remove(request, pk):
    product = Basket.objects.get(pk=pk)
    product.delete()
    return redirect('basket')


def search(request):
    word = request.GET.get('q')
    products = Product.objects.filter(Q(title__icontains=word))
    context = {
        "products": products
    }
    return render(request, "shop/search.html", context)

from decimal import Decimal
from random import sample

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Min
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme, urlencode

from shop.context_processors import get_counts
from shop.forms import SignUpForm, SignInForm
from shop.models import *

SHIPPING_FEE = Decimal("10")


# ---------- Yordamchi funksiyalar ----------
def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def need_login(request):
    """Login qilmagan foydalanuvchini signin'ga yuboradi (qaytish manzili bilan)."""
    next_url = request.META.get("HTTP_REFERER") or request.get_full_path()
    url = f"{reverse('signin')}?{urlencode({'next': next_url})}"
    if is_ajax(request):
        return JsonResponse({"login": url}, status=401)
    return redirect(url)


# ---------- Sahifalar ----------
def index(request):
    products = list(Product.objects.all())
    context = {
        "categories": Category.objects.all(),
        "subcategories": SubCategory.objects.all(),
        "offers": Offer.objects.all(),
        "sponsors": Sponsor.objects.all(),
        "featured_products": sample(products, min(8, len(products))),
        "recently_products": Product.objects.order_by('-id')[:8],
    }
    return render(request, "shop/index.html", context)


def category(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=cat)
    sort_field = request.GET.get('sort')
    price_fields = request.GET.getlist('price')
    color_fields = request.GET.getlist('color')
    size_fields = request.GET.getlist('size')

    if color_fields:
        products = products.filter(types__color__in=color_fields)
    if size_fields:
        products = products.filter(types__size__in=size_fields)
    if sort_field in ("price", "-price", "id", "-id"):
        products = products.annotate(price=Min("types__price")).order_by(sort_field)
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
    obj_list = paginator.get_page(request.GET.get("page"))
    return render(request, "shop/category.html", {"products": obj_list})


def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )
        messages.success(request, "Xabaringiz yuborildi, rahmat!")
        return redirect("contact")
    return render(request, "shop/contact.html")


# ---------- Autentifikatsiya ----------
def signup(request):
    if request.method == "POST":
        form = SignUpForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Ro'yxatdan o'tdingiz! Endi tizimga kiring.")
            return redirect("signin")
    else:
        form = SignUpForm()
    return render(request, "shop/signup.html", {"form": form})


def signin(request):
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    form = SignInForm()
    if request.method == "POST":
        form = SignInForm(data=request.POST)
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("home")
        messages.error(request, "Username yoki parol noto'g'ri.")
    return render(request, "shop/signin.html", {"form": form, "next": next_url})


def signout(request):
    logout(request)
    return redirect("signin")


# ---------- Yoqtirilganlar ----------
@login_required
def likes(request):
    liked = Like.objects.filter(user=request.user).select_related("product")
    products = [like.product for like in liked]
    return render(request, "shop/likes.html", {"products": products})


def like_toggle(request, pk):
    if not request.user.is_authenticated:
        return need_login(request)
    product = get_object_or_404(Product, pk=pk)
    existing = Like.objects.filter(user=request.user, product=product)
    if existing.exists():
        existing.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, product=product)
        liked = True
    if is_ajax(request):
        likes_count, basket_count = get_counts(request.user)
        return JsonResponse({"liked": liked, "likes": likes_count, "basket": basket_count})
    return redirect(request.META.get("HTTP_REFERER", "home"))


# ---------- Mahsulot ----------
def detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    products = list(Product.objects.exclude(pk=pk))
    data = sample(products, min(8, len(products)))
    return render(request, "shop/detail.html", {"product": product, "similar": data})


# ---------- Savat ----------
@login_required
def basket(request):
    items = list(
        Basket.objects.filter(user=request.user, product__isnull=False)
        .select_related("product")
    )
    total_sale = sum(item.get_total_sale() for item in items)
    total_price = sum(item.get_total_price() for item in items)
    total_quantity = sum(item.quantity for item in items)
    shipping = SHIPPING_FEE if items else Decimal("0")
    context = {
        "products": items,
        "total_sale": total_sale,
        "total_price": total_price,
        "total_quantity": total_quantity,
        "benefit": total_price - total_sale,
        "shipping": shipping,
        "grand_total": total_sale + shipping,
    }
    return render(request, "shop/basket.html", context)


def basket_add(request, pk):
    if not request.user.is_authenticated:
        return need_login(request)
    product = get_object_or_404(Product, pk=pk)
    try:
        quantity = max(int(request.POST.get("quantity", 1)), 1)
    except ValueError:
        quantity = 1
    item, created = Basket.objects.get_or_create(
        product=product, user=request.user, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()
    if is_ajax(request):
        likes_count, basket_count = get_counts(request.user)
        return JsonResponse({"added": True, "likes": likes_count, "basket": basket_count})
    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def basket_update(request, pk):
    item = get_object_or_404(Basket, pk=pk, user=request.user)
    if request.method == "POST":
        if request.POST.get('action') == '+':
            item.quantity += 1
        elif item.quantity > 1:
            item.quantity -= 1
        else:
            item.delete()
            return redirect("basket")
        item.save()
    return redirect("basket")


@login_required
def basket_remove(request, pk):
    item = get_object_or_404(Basket, pk=pk, user=request.user)
    item.delete()
    return redirect('basket')


def search(request):
    word = request.GET.get('q', '')
    products = Product.objects.filter(title__icontains=word)
    return render(request, "shop/search.html", {"products": products})
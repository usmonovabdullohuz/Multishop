from django.db.models import Sum

from shop.models import Basket, Like


def get_counts(user):
    """(yoqtirilganlar soni, savatdagi mahsulotlar soni) qaytaradi."""
    if not user.is_authenticated:
        return 0, 0
    likes = Like.objects.filter(user=user).count()
    basket = (
        Basket.objects.filter(user=user, product__isnull=False)
        .aggregate(total=Sum("quantity"))["total"]
        or 0
    )
    return likes, basket


def counters(request):
    likes, basket = get_counts(request.user)
    return {"likes_count": likes, "basket_count": basket}
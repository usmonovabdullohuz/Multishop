from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ForeignKey

NO_USER_IMG = "https://i0.wp.com/digitalhealthskills.com/wp-content/uploads/2022/11/3da39-no-user-image-icon-27.png?fit=500%2C500&ssl=1"
NO_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original"


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **kwargs):
        if not username:
            raise ValueError("Username must be fill")
        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        if not kwargs.get("is_staff"):
            raise ValueError("Staff must be True")
        if not kwargs.get("is_superuser"):
            raise ValueError("Super User must be True")
        return self.create_user(username=username, password=password, **kwargs)


class User(AbstractUser):
    COUNTRY_CHOICES = [
        ("Uzbekistan", "Uzbekistan"),
        ("Kyrgyzstan", "Kyrgyzstan"),
        ("Kazakhstan", "Kazakhstan"),
        ("Tajikistan", "Tajikistan"),
    ]
    phone = models.CharField(max_length=14)
    country = models.CharField(max_length=15, choices=COUNTRY_CHOICES, default="Uzbekistan")
    province = models.CharField(max_length=15)
    region = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to="images/avatars/", blank=True, null=True)

    def get_avatar(self):
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                return NO_USER_IMG
        return NO_USER_IMG

    objects = UserManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


class Contact(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()

    def __str__(self):
        return self.full_name


class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to="images/categories/")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class SubCategory(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to="images/categories/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"


class Offer(models.Model):
    title = models.CharField(max_length=250)
    sale = models.IntegerField(default=5)
    image = models.ImageField(upload_to="images/offers/")

    def __str__(self):
        return self.title


class Sponsor(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to="images/sponsors")

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    information = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return self.title

    def get_image(self):
        first = self.images.first()
        if first:
            try:
                return first.image.url
            except Exception:
                return NO_IMAGE
        return NO_IMAGE


class ProductType(models.Model):
    SIZE_CHOICES = [
        ("xs", "extra small"),
        ("s", "small"),
        ("m", "medium"),
        ("l", "large"),
        ("xl", "extra large"),
    ]
    COLOR_CHOICES = [
        ("black", "black"),
        ("white", "white"),
        ("red", "red"),
        ("blue", "blue"),
        ("green", "green"),
        ("brown", "brown"),
    ]
    size = models.CharField(max_length=15, choices=SIZE_CHOICES, default="m")
    color = models.CharField(max_length=15, choices=COLOR_CHOICES, default="white")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sale = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="types")

    class Meta:
        unique_together = ("product", "size", "color")


class ProductImage(models.Model):
    image = models.ImageField(upload_to="images/products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")


class Like(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class Basket(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def _type(self):
        return self.product.types.first() if self.product else None

    def get_total_sale(self):
        t = self._type()
        if not t:
            return 0
        return (t.sale or t.price) * self.quantity

    def get_total_price(self):
        t = self._type()
        if not t:
            return 0
        return t.price * self.quantity

    def __str__(self):
        return self.product.title if self.product else "Deleted product"
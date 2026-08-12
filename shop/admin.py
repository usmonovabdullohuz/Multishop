from django.contrib import admin
from shop.models import *

admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Offer)
admin.site.register(Sponsor)
admin.site.register(Like)
admin.site.register(Basket)

class ProductTypeInline(admin.TabularInline):
    model = ProductType
    fk_name = "product"
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fk_name = "product"
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title',]
    inlines = [ProductTypeInline, ProductImageInline]

admin.site.register(Product, ProductAdmin)
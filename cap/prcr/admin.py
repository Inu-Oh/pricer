from django.contrib import admin

from prcr.models import Brand, Category, Price, Product, SubCategory


admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Price)
admin.site.register(Product)
admin.site.register(SubCategory)
from django.db import models
from django.core.validators import MinLengthValidator
# from django.contrib.auth.models import User
from django.conf import settings

# from taggit.managers import TaggableManageer # need to install and add to settings

class Category(models.Model):
    name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2, "Category name must be longer than two letters.")]
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"


class SubCategory(models.Model):
    name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2, "Sub-category name must be longer than two letters.")]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
        related_name="subcategory_category")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "subcategory"
        verbose_name_plural = "subcategories"


class Brand(models.Model):
    name = models.CharField(
        max_length=128,
        validators=[MinLengthValidator(2, "Brand name must be longer than two letters.")]
    )
    company_name = models.CharField(
        max_length=128
    )
    # add logo for upload
    # add trust rating
    # add categories or subcategories one to many field
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        if self.company_name:
            return self.name + " (" + self.company_name + ")"
        else:
            return self.name


class Product(models.Model):
    name = models.CharField(
        max_length=128,
        validators=[MinLengthValidator(2, "Product name must be longer than two letters.")]
    )
    brand = models.ForeignKey(Brand, null=True, on_delete=models.SET_NULL,
        related_name="product_brand")
    sub_category = models.ForeignKey(SubCategory, null=True, on_delete=models.SET_NULL,
        related_name="product_subcategory")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name="product_owner")
    # colors = array for colors or selection
    # features = description or array

    # Picture upload
    picture = models.BinaryField(null=True, blank=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, blank=True,
                                    help_text='The MimeTypeof the file')


    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        product_str = self.name 
        if self.brand and self.sub_category:
            product_str = product_str + " by " + self.brand.name + " (" + self.sub_category.category.name + ")"
        elif self.brand: 
            product_str = product_str + " by " + self.brand.name
        elif self.sub_category:
            product_str = product_str + " (" + self.sub_category.name + ", " + self.sub_category.category.name + ")"
        return product_str


class Price(models.Model):
    price = models.DecimalField(max_digits=8, decimal_places=2)
    link = models.URLField(max_length=256)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_product")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name="price_owner")

    date_observed = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        price_str = str(self.price) + " (on " + str(self.date_observed) + ")"
        return price_str
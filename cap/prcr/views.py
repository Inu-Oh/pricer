from prcr.models import Brand, Category, Price, Product, SubCategory

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView


class CategoryListView(ListView):
    template_name = "prcr/main_list.html"

    def get(self, request):
        category_list = Category.objects.all() # .order_by('word')
        subcategory_list = SubCategory.objects.all() # .order_by('word')
        context = {'category_list': category_list, 'subcategory_list': subcategory_list}
        return render(request, self.template_name, context)


# class ProductListView(ListView):
#     template_name = "prcr/produt_list.html"

#     def get(self, request, pk):
#         product_list = Product.objects.filter(sub_category.id = pk) # filter by subcategory id
#         context = {'product_list': product_list}
#         return render(request, self.template_name, context)
from prcr.forms import FeatureCreateForm, PriceCreateForm, ProductCreateForm, ProductAddImageForm, SubcategoryCreateForm
from prcr.models import Brand, Category, Feature, Price, Product, SubCategory

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturalday #, naturaltime
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

import pandas as pd
from plotly.offline import plot
import plotly.express as px
from urllib.parse import urlparse


class CategoryListView(ListView):
    template_name = "prcr/main_list.html"

    def get(self, request):
        category_list = Category.objects.all().order_by('category')
        category_count = category_list.count()
        subcategory_list = SubCategory.objects.all().order_by('subcategory')
        subcategory_count = subcategory_list.count()
        product_count = Product.objects.count()
        context = {
            'category_list': category_list,
            'subcategory_list': subcategory_list,
            'product_count': product_count,
            'category_count': category_count,
            'subcategory_count': subcategory_count
            }
        return render(request, self.template_name, context)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = '__all__'
    success_url = reverse_lazy('prcr:main_list')


class SubcategoryCreateView(LoginRequiredMixin, CreateView):
    model = SubCategory
    template_name = 'prcr/subcategory_form.html'
    
    def get(self, request, pk):
        form = SubcategoryCreateForm()
        category = Category.objects.get(id=pk)
        context = {'form': form, 'category': category}
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        form = SubcategoryCreateForm(request.POST)
        category = Category.objects.get(id=pk)
        
        if not form.is_valid():
            context = {'form': form, 'category': category}
            return render(request, self.template_name, context)
        
        # Add category to subcategory object before saving
        subcategory = form.save(commit=False)
        subcategory.category = category
        subcategory.save()
        new_subcategory_id = subcategory.id
        success_url = reverse_lazy('prcr:product_list', kwargs={'pk': new_subcategory_id})
        return redirect(success_url)


class BrandListView(ListView):
    template_name = "prcr/brand_list.html"

    def get(self, request):
        brand_list = Brand.objects.all().order_by('brand')
        brand_count = brand_list.count()
        product_list = Product.objects.all().order_by('product')
        product_count = product_list.count()
        context = {
            'brand_list': brand_list,
            'product_list': product_list,
            'brand_count': brand_count,
            'product_count': product_count
            }
        return render(request, self.template_name, context)


class BrandCreateView(LoginRequiredMixin, CreateView):
    model = Brand
    fields = '__all__'
    success_url = reverse_lazy('prcr:brand_list')


class FeatureCreateView(LoginRequiredMixin, View):
    template_name = 'prcr/feature_form.html'

    def get(self, request, pk):
        form = FeatureCreateForm()
        prod = Product.objects.get(id=pk)
        context = { 'form': form, 'product': prod }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = FeatureCreateForm(request.POST)
        prod = Product.objects.get(id=pk)

        if not form.is_valid():
            context = { 'form': form, 'product': prod }
            return render(request, self.template_name, context)

        # Add product to the model before saving
        price = form.save(commit=False)
        price.product = prod
        price.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': prod.id})
        return redirect(success_url)


class PriceCreateView(LoginRequiredMixin, View):
    template_name = 'prcr/price_form.html'

    def get(self, request, pk):
        form = PriceCreateForm()
        prod = Product.objects.get(id=pk)
        context = { 'form': form, 'product': prod }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = PriceCreateForm(request.POST)
        prod = Product.objects.get(id=pk)

        if not form.is_valid():
            context = { 'form': form, 'product': prod }
            return render(request, self.template_name, context)

        # Add owner and product to the model before saving
        price = form.save(commit=False)
        price.owner = self.request.user
        price.product = prod
        price.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': prod.id})
        return redirect(success_url)


class ProductListView(ListView):
    template_name = "prcr/product_list.html"

    def get(self, request, pk):
        product_list = Product.objects.all().order_by(Lower('product')).values()
        filtered_products = product_list.filter(subcategory_id=pk)
        subcategory = SubCategory.objects.get(id=pk)
        brands = Brand.objects.all()
        feature_list = Feature.objects.all()
        # to do: can alter brands to brand_list by filtering for brands related to product_list
        context = {
            'filtered_products': filtered_products,
            'subcategory': subcategory,
            'brands': brands,
            'feature_list': feature_list,
            }
        return render(request, self.template_name, context)


class ProductDetailView(DetailView):
    model = Product
    template_name = "prcr/product_detail.html"

    def get(self, request, pk=None):
        feature_list = Feature.objects.filter(product_id=pk)
        price_list = Price.objects.filter(product_id=pk)
        if price_list:
            for obj in price_list:
                obj.natural_date_observed = naturalday(obj.date_observed)
            highest_price = price_list.latest('price')
            high_price_dom = urlparse(highest_price.link).netloc
            highest_price.domain = '.'.join(high_price_dom.split('.')[-2:])
            lowest_price = price_list.earliest('price')
            low_price_dom = urlparse(lowest_price.link).netloc
            lowest_price.domain = '.'.join(low_price_dom.split('.')[-2:])
            latest_date = price_list.latest('date_observed') # delete or use
            earliest_date = price_list.earliest('date_observed') # delete or use
        else:
            highest_price = ''
            lowest_price = ''
            latest_date = ''# delete or use
            earliest_date = ''# delete or use
        product = Product.objects.get(id=pk)
        product.natural_updated = naturalday(product.updated_at)

        # Set up price chart
        if highest_price:
            price_dates = [price.date_observed for price in price_list]
            prices = [price.price for price in price_list]
            scale = [int(price.price) for price in price_list]
            price_data = {
                'Dates': price_dates,
                'Prices': prices,
                'Scale': scale
            }
            data_frame = pd.DataFrame(price_data)
            figure = px.scatter(
                data_frame, x='Dates', y='Prices', color='Scale', size='Scale'
            )
            # Embed the plot in an HTML div tag
            price_chart: str = plot(figure, output_type='div')
        else:
            price_chart: str = 'There are no prices to plot'
        context = {
            'product': product,
            'feature_list': feature_list,
            'price_list': price_list,
            'highest_price': highest_price,
            'lowest_price': lowest_price,
            'price_chart': price_chart
        }
        return render(request, self.template_name, context)
        

class ProductCreateView(LoginRequiredMixin, View):
    template_name = "prcr/product_form.html"

    def get(self, request, pk=None):
        form = ProductCreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = ProductCreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        
        # Add owner to the model before saving
        product = form.save(commit=False)
        product.owner = self.request.user
        product.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': product.id})
        
        return redirect(success_url)


class ProductUpdateView(LoginRequiredMixin, View):
    template_name = "prcr/product_form.html"

    def get(self, request, pk=None):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = ProductCreateForm(instance=product)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = ProductCreateForm(request.POST, request.FILES or None, instance=product)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        
        product = form.save(commit=False)
        product.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': product.id})

        return redirect(success_url)
    

class ProductAddImageView(LoginRequiredMixin, View):
    template_name = "prcr/product_add_image_form.html"

    def get(self, request, pk=None):
        product = get_object_or_404(Product, id=pk)
        form = ProductAddImageForm(instance=product)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        product = get_object_or_404(Product, id=pk)
        form = ProductAddImageForm(request.POST, request.FILES or None, instance=product)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        
        product = form.save(commit=False)
        product.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': product.id})

        return redirect(success_url)

# No delete product form at least at this time
# Product picture upload support function
def stream_file(request, pk):
    pic = get_object_or_404(Product, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response

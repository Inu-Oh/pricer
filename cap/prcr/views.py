from prcr.forms import FeatureCreateForm, PriceCreateForm, ProductBrandCreateForm, ProductAddImageForm, ProductSubcategoryCreateForm, ProductUpdateForm, SubcategoryCreateForm
from prcr.models import Brand, Category, Feature, Price, Product, SubCategory

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturalday #, naturaltime
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

import locale
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
        product_list = Product.objects.all().order_by('-created_at')
        product_count = product_list.count()
        context = {
            'category_count': category_count,
            'category_list': category_list,
            'subcategory_count': subcategory_count,
            'subcategory_list': subcategory_list,
            'product_count': product_count,
            'product_list': product_list,
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
        feature_list = Feature.objects.all()
        context = {
            'brand_list': brand_list,
            'product_list': product_list,
            'brand_count': brand_count,
            'product_count': product_count,
            'feature_list': feature_list,
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
        price_list = Price.objects.all().order_by('-price') # order for lowest price last

        # Get the lowest price for each product into a dictionary
        pruduct_lowest_price_dict = {}
        for product in filtered_products:
            product_id = str(product['id'])
            for price in price_list:
                price_product_id = str(price.product.id)
                if price_product_id == product_id: # last price saved is lowest
                    pruduct_lowest_price_dict[product_id] = price.price
        product_lowest_price_list = []
        # Transform it into an accessible list of lowest price tuples
        for product_id, price in pruduct_lowest_price_dict.items():
            product_lowest_price_list.append((int(product_id), price))

        context = {
            'filtered_products': filtered_products,
            'subcategory': subcategory,
            'brands': brands,
            'feature_list': feature_list,
            'product_lowest_price_list': product_lowest_price_list
            }
        return render(request, self.template_name, context)


class ProductDetailView(DetailView):
    model = Product
    template_name = "prcr/product_detail.html"

    def get(self, request, pk=None):
        feature_list = Feature.objects.filter(product_id=pk)
        price_list = Price.objects.filter(product_id=pk)
        price_list = price_list.order_by('-date_observed')

        if price_list:
            for price in price_list:
                price.natural_date_observed = naturalday(price.date_observed)
            highest_price = price_list.latest('price')
            high_price_dom = urlparse(highest_price.link).netloc
            highest_price.domain = '.'.join(high_price_dom.split('.')[-2:])
            lowest_price = price_list.earliest('price')
            low_price_dom = urlparse(lowest_price.link).netloc
            lowest_price.domain = '.'.join(low_price_dom.split('.')[-2:])
        else:
            highest_price = ''
            lowest_price = ''

        product = Product.objects.get(id=pk)
        product.natural_updated = naturalday(product.updated_at)

        # Set up price chart data
        if highest_price:
            price_dates = [price.date_observed for price in price_list]
            prices = [price.price for price in price_list]
            if highest_price.price != lowest_price.price:
                scale = [-int((price.price - lowest_price.price)/(highest_price.price - lowest_price.price) * 10) + 10 for price in price_list]
            else:
                scale = [5]
            dot_size = [val if val > 3 else 3 for val in scale]
            hover_texts = []
            locale.setlocale(locale.LC_ALL, 'C')
            def format_currency(amount):
                return '${:,.2f}'.format(amount)
            for price in price_list:
                hover_text = "<b>" + format_currency(price.price) + "</b><br>" + price.natural_date_observed + "<br>" 
                domain = urlparse(price.link).netloc
                hover_text += '.'.join(domain.split('.')[-2:])
                hover_texts.append(hover_text)
                price_domain = urlparse(price.link).netloc
                price.domain = '.'.join(price_domain.split('.')[-2:])

            # Set up price chart elements
            price_data = {
                'Price History': price_dates,
                'Price': prices,
                'Price Rating': scale,
                'Dot size': dot_size,
                'HoverTexts': hover_texts
            }
            data_frame = pd.DataFrame(price_data)
            figure = px.scatter(
                data_frame, x='Price History', y='Price', color='Price Rating', size='Dot size',
                color_continuous_scale='rdylgn')
            figure['layout']['yaxis']['autorange'] = 'reversed'
            figure.update_traces(mode='markers', hovertemplate=hover_texts)
            figure.update_layout(
                yaxis_tickprefix = '$', yaxis_tickformat = ',',
                xaxis={'visible': True, 'showticklabels': False})

            # Embed the chart plot in an HTML div tag
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
        

class ProductBrandCreateView(LoginRequiredMixin, View):
    template_name = "prcr/product_brand_form.html"

    def get(self, request, pk):
        brand = get_object_or_404(Brand, id=pk)
        form = ProductBrandCreateForm()
        ctx = {'form': form, 'brand': brand}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        brand = get_object_or_404(Brand, id=pk)
        form = ProductBrandCreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form, 'brand': brand}
            return render(request, self.template_name, ctx)
        
        # Add owner to the model before saving
        product = form.save(commit=False)
        product.owner = self.request.user
        product.brand = brand
        product.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': product.id})
        
        return redirect(success_url)


class ProductSubcategoryCreateView(LoginRequiredMixin, View):
    template_name = "prcr/product_subcategory_form.html"

    def get(self, request, pk):
        subcategory = get_object_or_404(SubCategory, id=pk)
        form = ProductSubcategoryCreateForm()
        ctx = {'form': form, 'subcategory': subcategory}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        subcategory = get_object_or_404(SubCategory, id=pk)
        form = ProductSubcategoryCreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form, 'subcategory': subcategory}
            return render(request, self.template_name, ctx)
        
        # Add owner to the model before saving
        product = form.save(commit=False)
        product.owner = self.request.user
        product.subcategory = subcategory
        product.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': product.id})
        
        return redirect(success_url)


class ProductUpdateView(LoginRequiredMixin, View):
    template_name = "prcr/product_form.html"

    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = ProductUpdateForm(instance=product)
        ctx = {'form': form, 'product': product}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = ProductUpdateForm(request.POST, request.FILES or None, instance=product)

        if not form.is_valid():
            ctx = {'form': form, 'product': product}
            return render(request, self.template_name, ctx)
        
        product = form.save(commit=False)
        product.save()
        success_url = reverse_lazy('prcr:product_detail', kwargs={'pk': product.id})

        return redirect(success_url)


class ProductAddImageView(LoginRequiredMixin, View):
    template_name = "prcr/product_add_image_form.html"

    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        form = ProductAddImageForm(instance=product)
        ctx = {'form': form, 'product': product}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        form = ProductAddImageForm(request.POST, request.FILES or None, instance=product)

        if not form.is_valid():
            ctx = {'form': form, 'product': product}
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

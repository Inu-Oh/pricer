from prcr.forms import CreateForm
from prcr.models import Brand, Category, Feature, Price, Product, SubCategory

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView


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
    fields = '__all__'
    success_url = reverse_lazy('prcr:main_list')


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


class ProductListView(ListView):
    template_name = "prcr/product_list.html"

    def get(self, request, pk):
        product_list = Product.objects.all().order_by(Lower('product')).values()
        filtered_products = product_list.filter(subcategory_id=pk)
        subcategory = SubCategory.objects.get(id=pk)
        brands = Brand.objects.all()
        context = {
            'filtered_products': filtered_products,
            'subcategory': subcategory,
            'brands': brands,
            }
        return render(request, self.template_name, context)


class ProductDetailView(DetailView):
    model = Product
    template_name = "prcr/product_detail.html"

    def get(self, request, pk=None):
        feature_list = Feature.objects.filter(product_id=pk)
        price_list = Price.objects.filter(product_id=pk)
        for obj in price_list:
            obj.natural_date_observed = naturalday(obj.date_observed)
        product = Product.objects.get(id=pk)
        # product.natural_updated = naturaltime(product.updated_at)

        context = {
            'product': product,
            'feature_list': feature_list,
            'price_list': price_list
        }
        return render(request, self.template_name, context)
        

class ProductCreateView(LoginRequiredMixin, View):
    template_name = "prcr/product_form.html"

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        
        # Add owner to the model before saving
        product = form.save(commit=False)
        product.owner = self.request.user
        product.save()
        success_url = reverse_lazy('prcr:product_list', kwargs={'pk': product.subcategory.id})
        
        return redirect(success_url)


class ProductUpdateView(LoginRequiredMixin, View):
    template_name = "prcr/product_form.html"

    def get(self, request, pk=None):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = CreateForm(instance=product)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=product)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        
        product = form.save(commit=False)
        product.save()
        success_url = reverse_lazy('prcr:product_list', kwargs={'pk': product.subcategory.id})

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

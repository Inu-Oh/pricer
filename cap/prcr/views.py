from prcr.models import Brand, Category, Price, Product, SubCategory
from prcr.forms import CreateForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView


class CategoryListView(ListView):
    template_name = "prcr/main_list.html"

    def get(self, request):
        category_list = Category.objects.all().order_by('name')
        subcategory_list = SubCategory.objects.all().order_by('name')
        context = {'category_list': category_list, 'subcategory_list': subcategory_list}
        return render(request, self.template_name, context)


class ProductListView(ListView):
    template_name = "prcr/product_list.html"

    def get(self, request, pk):
        product_list = Product.objects.all().order_by(Lower('name')).values()
        filtered_products = product_list.filter(sub_category_id=pk)
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


class ProductCreateView(LoginRequiredMixin, View):
    template_name = "prcr/product_form.html"

    def get(self, request, pk=None):
        form = CreateForm()
        context = {'form': form}
        return render(request, self.template_name, context)
    
    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)
        
        # Add owner to the model before saving
        product = form.save(commit=False)
        product.owner = self.request.user
        product.save()
        success_url = reverse_lazy('prcr:product_list', kwargs={'pk': product.sub_category.id})
        
        return redirect(success_url)


class ProductUpdateView(LoginRequiredMixin, View):
    template_name = "prcr/product_form.html"

    def get(self, request, pk=None):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = CreateForm(instance=product)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        product = get_object_or_404(Product, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=product)

        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)
        
        product = form.save(commit=False)
        product.save()
        success_url = reverse_lazy('prcr:product_list', kwargs={'pk': product.sub_category.id})

        return redirect(success_url)

# No delete product form at least at this time


def stream_file(request, pk):
    pic = get_object_or_404(Product, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response
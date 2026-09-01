from django.shortcuts import render, redirect, get_object_or_404
from .models import Product


def product_list(request):

    search = request.GET.get('search', '')

    if search:
        products = Product.objects.filter(
            name__icontains=search
        ).order_by('id')
    else:
        products = Product.objects.all().order_by('id')

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'search': search
        }
    )


def add_product(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        minimum_stock = request.POST.get('minimum_stock')

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            minimum_stock=minimum_stock
        )

        return redirect('product_list')

    return render(
        request,
        'products/add_product.html'
    )


def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':

        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.minimum_stock = request.POST.get('minimum_stock')

        product.save()

        return redirect('product_list')

    return render(
        request,
        'products/edit_product.html',
        {'product': product}
    )


def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')

    return render(
        request,
        'products/delete_product.html',
        {'product': product}
    )
from django.shortcuts import render
from .models import Item

def menu_view(request):
    token = request.GET.get('token')
    items = Item.objects.all().order_by('category', 'name')

    categories = {}
    for item in items:
        categories.setdefault(item.category, []).append(item)

    return render(request, 'index.html', {'categories': categories, 'token': token})

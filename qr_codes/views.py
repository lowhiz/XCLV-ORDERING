from django.shortcuts import redirect, render
from .models import ValidList

def validation(request):
    token = request.GET.get('token')  

    is_valid = ValidList.objects.filter(unique_token=token).exists()

    if is_valid:
        return redirect(f"{reverse('menu')}?token={token}")
    else:
        return render(request, 'unwelcome.html')

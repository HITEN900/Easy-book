from django.shortcuts import render

def support_view(request):
    return render(request, 'support/contact.html')
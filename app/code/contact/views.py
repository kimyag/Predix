from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import ContactForm


def contact_view(request):
    form = ContactForm()
    context = {'form': form}
    return render(request, 'contact/contact.html', context)
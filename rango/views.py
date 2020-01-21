from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    text = """"Rango says hey there partner! <br>
    <a href='/rango/about/'>About</a>)"""
    return HttpResponse(text)


def about(request):
    text = """ This is a about page <br>
     <a href="/rango/"> Click here to go back to main page </a>"""
    return HttpResponse(text)

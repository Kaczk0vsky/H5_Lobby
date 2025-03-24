from django.shortcuts import render
from django.http import HttpResponse


def ashanarena(request):
    return HttpResponse(
        "Greetings, Noble Warrior! Behold, the AshanArena3 is currently under construction. Take heed and return in the future, for great wonders shall await thee... Thou shalt not be disappointed!"
    )

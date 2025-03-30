from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit


@csrf_protect
@require_GET
@ratelimit(key="user_or_ip", rate="3/m", method="GET", block=True)
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("password_reset_complete")
        else:
            form = SetPasswordForm(user)

        return render(request, "password_reset_confirm.html", {"form": form})

    return render(request, "password_reset_invalid.html")


def ashanarena(request):
    return render(request, "main.html")

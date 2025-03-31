from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django.db import transaction
from django.contrib.sessions.models import Session


@csrf_protect
@require_http_methods(["GET", "POST"])
@ratelimit(key="user_or_ip", rate="3/m", method="GET", block=True)
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "password_reset_invalid.html")

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            with transaction.atomic():
                user.refresh_from_db()
                user.set_password(new_password)
                user.last_login = None
                user.save()
                Session.objects.filter(session_key__in=request.session.keys()).delete()
                return render(request, "password_reset_complete.html")
    else:
        form = SetPasswordForm(user)

    return render(request, "password_reset_confirm.html", {"form": form})


def ashanarena(request):
    return render(request, "frontend/index.html")

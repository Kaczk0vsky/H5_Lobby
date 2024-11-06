from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

import json


@csrf_exempt  # Disable CSRF for external requests; for production, secure this with proper auth
def register_new_player(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        password = data.get("password")
        repeat_password = data.get("repeat_password")
        email = data.get("email")

        if password != repeat_password or "@" not in email:
            return JsonResponse(
                {"success": False, "error": "Invalid input"}, status=400
            )

        try:
            user = User.objects.create_user(
                username=nickname, password=password, email=email
            )
            return JsonResponse({"success": True, "user_id": user.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@csrf_exempt  # Disable CSRF for external requests; for production, secure this with proper auth
def login_player(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        password = data.get("password")
        try:
            user = authenticate(username=nickname, password=password)
            return JsonResponse({"success": True, "user_id": user.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )

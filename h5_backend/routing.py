from django.urls import re_path
from h5_backend.consumer import TestConsumer

websocket_urlpatterns = [
    re_path(r"ws/test/$", TestConsumer.as_asgi()),
]

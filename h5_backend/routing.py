from django.urls import re_path
from h5_backend.consumer import QueueConsumer

websocket_urlpatterns = [
    re_path(r"ws/queue/(?P<nickname>\w+)/$", QueueConsumer.as_asgi()),
]

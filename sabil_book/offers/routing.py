from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"^ws/offers/(?P<offer_id>\d+)/chat/$",
        consumers.OfferChatConsumer.as_asgi(),
    ),
]

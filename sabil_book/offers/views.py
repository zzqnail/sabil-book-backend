from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from .models import Message
from .models import Offer
from .pagination import MessageCursorPagination
from .permissions import is_offer_participant
from .serializers import MessageSerializer


class MessageListView(ListAPIView):
    """Paginated chat history for an offer.

    Lets a client that opens the chat mid-conversation (or reconnects after
    a drop) fetch what it missed, instead of relying solely on the
    WebSocket stream. Access is restricted to the same two participants
    allowed into the WebSocket room — see
    `sabil_book.offers.permissions.is_offer_participant`, shared with
    `OfferChatConsumer` so the rule can't drift between the two entry points.
    """

    serializer_class = MessageSerializer
    pagination_class = MessageCursorPagination

    def get_queryset(self):
        offer = get_object_or_404(Offer, pk=self.kwargs["offer_id"])
        if not is_offer_participant(self.request.user, offer):
            # 404, not 403: don't reveal that the offer exists to non-participants.
            raise NotFound
        return Message.objects.filter(offer=offer).select_related("sender")

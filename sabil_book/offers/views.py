from __future__ import annotations

from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sabil_book.requests.models import Request
from sabil_book.users.models import ProviderProfile

from .models import Offer
from .serializers import OfferSerializer
from .services import InvalidTransitionError
from .services import accept_offer


class OfferViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    queryset = Offer.objects.select_related("request", "provider")

    @action(detail=False, methods=["get"], url_path="for-request")
    def for_request(self, request):
        request_id = request.query_params.get("request")
        if request_id is None:
            raise ValidationError(
                {"request": "This query parameter is required."},
            )
        offers = self.queryset.filter(
            request_id=request_id,
            request__customer=request.user,
        )
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        try:
            offer = accept_offer(int(pk), request.user)
        except Request.DoesNotExist as exc:
            msg = "Offer not found."
            raise NotFound(msg) from exc
        except InvalidTransitionError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(self.get_serializer(offer).data)

    def perform_create(self, serializer: OfferSerializer) -> None:
        provider = ProviderProfile.objects.filter(user=self.request.user).first()
        if provider is None:
            msg = "A provider profile is required."
            raise PermissionDenied(msg)

        if provider.kyc_status != ProviderProfile.KYCStatus.APPROVED:
            msg = "Approved KYC is required."
            raise PermissionDenied(msg)
        offer_request = serializer.validated_data["request"]

        if offer_request.status != Request.RequestStatus.PUBLISHED:
            msg = "A published request is required"
            raise ValidationError(msg)
        serializer.save(provider=provider)

    def get_queryset(self):
        return self.queryset.filter(provider__user=self.request.user)

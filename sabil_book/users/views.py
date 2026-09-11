import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from sabil_book.users.models import ProviderProfile
from sabil_book.users.models import User
from sabil_book.users.serializers import ProviderProfilePublicSerializer
from sabil_book.users.serializers import ProviderProfileSerializer
from sabil_book.users.serializers import RegisterSerializer
from sabil_book.users.serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        if request.method == "PATCH":
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)

        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RegisterView(CreateAPIView):
    """Register a new user and return it together with a JWT token pair."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "refreshToken": str(refresh),
            "authToken": str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Blacklist the given refresh token, effectively logging the user out."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise ValidationError({"refresh": "This field is required."})
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError as exc:
            raise ValidationError({"refresh": str(exc)}) from exc
        return Response(status=status.HTTP_205_RESET_CONTENT)


class CurrentUserView(APIView):
    """Return the currently authenticated user."""

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ProviderProfileViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    """Become a provider, view a provider's public profile, manage your own."""

    queryset = ProviderProfile.objects.all()
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProviderProfilePublicSerializer
        return ProviderProfileSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        if ProviderProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError({"detail": "You already have a provider profile."})
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["patch"], url_path="me")
    def me(self, request):
        profile = get_object_or_404(ProviderProfile, user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["post"], url_path="me/kyc/initiate")
    def initiate_kyc(self, request):
        """Stub: kick off an external KYC/AML check and mark it pending."""
        profile = get_object_or_404(ProviderProfile, user=request.user)
        profile.kyc_status = ProviderProfile.KYCStatus.PENDING
        profile.save(update_fields=["kyc_status"])
        data = {
            "verification_id": str(uuid.uuid4()),
            "kyc_status": profile.kyc_status,
        }
        return Response(status=status.HTTP_202_ACCEPTED, data=data)


class KYCWebhookView(APIView):
    """Stub callback endpoint for a KYC/AML provider's verification result.

    Not user-authenticated (it's a server-to-server call from the provider);
    guarded instead by a shared secret set via KYC_WEBHOOK_SECRET.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        secret = request.headers.get("X-Webhook-Secret", "")
        if not settings.KYC_WEBHOOK_SECRET or secret != settings.KYC_WEBHOOK_SECRET:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        allowed_statuses = {
            ProviderProfile.KYCStatus.APPROVED,
            ProviderProfile.KYCStatus.REJECTED,
        }
        new_status = request.data.get("status")
        if new_status not in allowed_statuses:
            raise ValidationError(
                {"status": f"Must be one of {sorted(allowed_statuses)}."},
            )

        profile = get_object_or_404(
            ProviderProfile,
            pk=request.data.get("provider_profile_id"),
        )
        profile.kyc_status = new_status
        profile.save(update_fields=["kyc_status"])
        return Response(status=status.HTTP_200_OK)

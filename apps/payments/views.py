# views.py
import datetime
from dateutil.relativedelta import relativedelta
import razorpay
import hmac, hashlib
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now
from user_details.models import FamilyMember
from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from .models import Transaction, Subscription, UserSubscription
from .serializers import TransactionSerializer, SubscriptionSerializer


class RazorpayView(custom_viewsets.ModelViewSet):
    permission_classes = [IsUserBlockedPermission]
    model = Transaction
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_permissions(self):
        if self.action in ['callback']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['create', 'partial_update', 'patch', 'list', 'create_order', 'payment_history']:
            permission_classes = [IsUserBlockedPermission]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    @action(detail=False, methods=['POST'])
    def create_order(self, request):
        days=0
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        subscription = request.data.get("subscription")
        pricing = Subscription.objects.filter(id=1).first()
        if not pricing:
            return Response({"error": "Pricing not available for this subscription."}, status=400)
        
        # Get subscription count (defaults to 1 if not provided)
        subscription = request.data.get("subscription", 1)
        try:
            subscription = int(subscription)
            if subscription < 1:
                return Response({"error": "Subscription count must be at least 1"}, status=400)
        except (TypeError, ValueError):
            return Response({"error": "Invalid subscription count"}, status=400)
        
        # Calculate amount: subscription count × price from database
        amount = subscription * float(pricing.price)
        currency = pricing.currency
        # existing_subscription = UserSubscription.objects.filter(user=request.user,
        #                                                         start_date__lte=datetime.datetime.now(),
        #                                                         end_date__gte=datetime.datetime.now()).first()
        # if existing_subscription:
        #     raise Exception("Already Subscribed")

        try:
            order = client.order.create({
                "amount": int(amount) * 100,  # Amount in paise
                "currency": "INR",  # Currency code
                "receipt": "receipt#123",  # Optional custom receipt number
                "payment_capture": 1,  # Auto-capture payment (1 for auto, 0 for manual)
                "notes": {
                    "callback_url": f"{settings.BED_BASE_URL}/api/payments/callback/",
                    "business_name": "My Business Name",
                    "user_id": str(request.user.id),
                    "purpose": "Booking/Subscription/Service Name",
                    "email": request.user.email,
                }
            })

            # order = client.order.create({"amount": int(amount) * 100, "currency": currency, "payment_capture": 1})

            # Save transaction
            transaction = Transaction.objects.create(user=request.user, razorpay_order_id=order["id"], amount=amount,
                                       currency=currency, status="created", subscription=pricing)
            return Response({"order_id": order["id"], "razorpay_key": settings.RAZORPAY_KEY_ID, "amount": amount,
                             "currency": currency}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["POST"])
    def callback(self, request):
        data = request.data

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        if not order_id or not payment_id or not signature:
            return Response({"error": "Missing parameters"}, status=400)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Fetch transaction
        try:
            transaction = Transaction.objects.get(razorpay_order_id=order_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)

        # Verify Razorpay signature
        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                }
            )
        except razorpay.errors.SignatureVerificationError:
            transaction.status = "failed"
            transaction.save()
            return Response({"error": "Invalid signature"}, status=400)

        # Fetch payment details
        try:
            payment = client.payment.fetch(payment_id)
        except razorpay.errors.RazorpayError as e:
            transaction.status = "failed"
            transaction.save()
            return Response({"error": f"Payment fetch failed: {str(e)}"}, status=400)

        actual_status = payment.get("status")

        # Capture payment if authorized
        if actual_status == "authorized":
            try:
                capture_response = client.payment.capture(
                    payment_id, int(transaction.amount * 100)
                )
                actual_status = capture_response.get("status", actual_status)
            except razorpay.errors.RazorpayError as e:
                transaction.status = "failed"
                transaction.save()
                return Response({"error": f"Payment capture failed: {str(e)}"}, status=400)

        # Handle successful payment
        if actual_status == "captured":
            transaction.status = "success"

            start_date = now()
            subscription = transaction.subscription

            if subscription.duration == "yearly":
                end_date = start_date + relativedelta(years=1)
            elif subscription.duration == "monthly":
                end_date = start_date + relativedelta(months=1)
            else:
                end_date = start_date + relativedelta(years=1)

            # Prevent duplicate subscription
            if not UserSubscription.objects.filter(user=transaction.user, is_active=True):
                UserSubscription.objects.get_or_create(
                    user=transaction.user,
                    subscription=subscription,
                    defaults={
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
            family_members = FamilyMember.objects.filter(primary_user=transaction.user)
            family_members.update(is_active=True)

            # ==========================
            # SEND SUCCESS EMAIL
            # ==========================
            context = {
                "user_name": transaction.user.full_name,
                "membership_id": transaction.user.membership_id,
                "start_date": start_date.strftime("%d %b %Y"),
                "end_date": end_date.strftime("%d %b %Y"),
                "amount": transaction.amount,
                "DashboardURL": "https://vaidyabandhu.com/",
                "Year": now().year,
                "CompanyName": "Vaidyabandhu",
            }

            html_message = render_to_string(
                "admin/membership_purchase.html", context
            )
            plain_message = strip_tags(html_message)
            if transaction.user.email:
                try:
                    send_mail(
                        subject="Membership Purchase Successful - Vaidyabandhu",
                        message=plain_message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[transaction.user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                except Exception as e:
                    # Email failure should not affect payment success
                    print(f"Email sending failed: {str(e)}")

        else:
            transaction.status = actual_status

        # Update transaction fields
        transaction.razorpay_payment_id = payment_id
        transaction.razorpay_signature = signature
        transaction.save()

        return Response(
            {
                "status": f"Payment {transaction.status}",
                "payment_id": payment_id,
                "order_id": order_id,
            },
            status=200,
        )

    @action(detail=False, methods=['GET'])
    def status(self, request):
        payment_id = request.query_params.get("payment_id")
        if not payment_id:
            return Response({"error": "Missing payment_id"}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            payment = client.payment.fetch(payment_id)
            return Response({
                "status": payment["status"],
                "amount": payment["amount"] / 100,
                "method": payment["method"],
                "email": payment["email"],
                "contact": payment["contact"]
            }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['GET'])
    def payment_history(self, request):
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=200)


class SubscriptionView(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Subscription
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    status_code = 200

    def get_permissions(self):

        if self.action in ['get', 'list']:
            permission_classes = [IsUserBlockedPermission]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

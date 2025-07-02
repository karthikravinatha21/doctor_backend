from django.shortcuts import render, get_object_or_404
from .models import Page

def dynamic_page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'terms/home_page.html', {'page': page})

def home_page(request, slug='home'):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'terms/home_page.html', {'page': page})

# from django.shortcuts import render, get_object_or_404, redirect
# from django.utils import timezone
# from datetime import timedelta
# from django.template.loader import render_to_string
# from django.contrib.auth.hashers import make_password
# from django.contrib import messages
# from apps.candidates.serializers import SigninSerializer,CandidateSerializer
# from apps.candidates.models import Candidate
# from utils.adaptor import send_templated_email_via_mandrill
# from django.contrib.auth import authenticate, login
# from user_details.views import get_location_details
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.decorators import action
# from rest_framework.views import APIView
# from rest_framework.viewsets import ViewSet
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import AllowAny
# from datetime import datetime, timedelta
# import apps.meta_app
# from user_details.models import UserTokens
# import apps.meta_app.serializers
# import jwt

# class AppUserView(ViewSet):
#     permission_classes = [AllowAny]

#     @action(detail=False, methods=['POST'])
#     def api_signin(self,request):
#         serializer = SigninSerializer(data=request.data)

#         if serializer.is_valid():
#             identifier = request.data.get('identifier')
#             password = request.data.get('password')
#             # latitude = request.data.get('latitude')
#             # longitude = request.data.get('longitude')

#             # Validate location
#             # if latitude and longitude:
#             #     details = get_location_details(latitude, longitude)
#             #     if details['country'] not in ['India', 'Guyana', 'Republic of Guyana']:
#             #         # messages.error(request, "Access restricted to users in Guyana.")
#             #         return Response({"error": "Access restricted to users in Guyana"}, status=status.HTTP_400_BAD_REQUEST)
          

#             try:
#                 # Identify user by email or mobile
#                 parent = Candidate.objects.get(email=identifier) if '@' in identifier else Candidate.objects.get(mobile=identifier)

#                 if not parent.email_verified:
#                     if parent.last_verification_sent and parent.last_verification_sent > timezone.now() - timedelta(hours=24):
#                         messages.error(request, 'Your email is not verified. Please check your email for the verification link sent earlier.')
#                     else:
#                         # Resend verification link
#                         verify_token = generate_random_key()
#                         parent.verify_token = verify_token
#                         parent.last_verification_sent = timezone.now()  # Update timestamp for verification email
#                         parent.save()

#                         # Send the email verification link
#                         body = f"""
#                         Dear {parent.first_name},

#                         Please verify your email address by clicking the link below:

#                         {request.scheme}://{request.get_host()}/verify_email/?verify_token={verify_token}

#                         If you did not request this, please ignore this email.

#                         The GDS Team
#                         """
                        
#                         html_content = ""  # Optional: Add HTML content for better formatting

#                         try:
#                             send_templated_email_via_mandrill(
#                                 "Email Verification Resent - Guyana Digital School",
#                                 body,
#                                 html_content,
#                                 parent.email,
#                                 settings.EMAIL_HOST_USER,
#                                 'Guyana Digital School'
#                             )
#                             messages.success(request, 'A new verification email has been sent to your email address.')
#                         except Exception as e:
#                             print(f"Email sending failed: {e}")
#                             # messages.error(request, 'Unable to send verification email. Please try again later.')

#                     # Prevent login for unverified accounts
#                     # return Response(ParentSerializer(parent).data, status=status.HTTP_200_OK)
#                     return Response({"error": "Please verify your E-mail ID"}, status=status.HTTP_400_BAD_REQUEST)

#                 # Authenticate user
#                 user = authenticate(request, username=identifier, password=password)
#                 if user is not None:
#                     user_exist = user
#                     expire_time = datetime.utcnow() + timedelta(seconds=12000000000)
#                     payload = {
#                         'id': user.id,
#                         'email': user.email,
#                         'first_name': user.first_name,
#                         'mobile': user.mobile,
#                         'user_type': 'parent',
#                         'user_role':[],
#                         'created_time': str(datetime.utcnow())
#                     }
              
#                     token = jwt.encode(
#                         payload, settings.SECRET_KEY, algorithm="HS256")
                    
#                     UserTokens.objects.filter(parent_user=user).delete()
#                     UserTokens.objects.create(parent_user=user, token=token)
                    
#                     refresh = RefreshToken.for_user(user_exist)
#                     refreshtoken = str(refresh)
#                     # request.session['token'] = parent.id
#                     # request.session['user'] = ParentSerializer(parent).data
                    
#                     return Response({"user":CandidateSerializer(parent).data,"token":token}, status=status.HTTP_200_OK)
#                 else:
#                     return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

#             except Candidate.DoesNotExist:
#                 return Response({"error": "Account not found. Please check your email or mobile number"}, status=status.HTTP_400_BAD_REQUEST)
#                 # messages.error(request, 'Account not found. Please check your email or mobile number.')
                
#         return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


#     @action(detail=False, methods=['POST'])
#     def api_signup(self,request):
#         serializer = UserRegistrationSerializer(data=request.data)

#         if serializer.is_valid():
#             # Extract data from the submitted form
#             first_name = request.data.get('first_name')
#             middle_name = ''
#             last_name = request.data.get('last_name')
#             country = 'Guyana'
#             mobile = request.data.get('mobile')
#             email = request.data.get('email')
#             password = request.data.get('password')
#             # latitude = request.data.get('latitude')
#             # longitude = request.data.get('longitude')

#             # Validate location
#             # if not latitude or not longitude:    
#             #     return Response({"error": "Location information is required to sign up"}, status=status.HTTP_400_BAD_REQUEST)

#             # location_details = get_location_details(latitude, longitude)
#             # allowed_countries = ['India', 'Guyana', 'Republic of Guyana']

#             # if location_details['country'] not in allowed_countries:
#             #     # messages.error(request, 'Sign-up is restricted to users from Guyana.')
#             #     return Response({"error": "Sign-up is restricted to users from Guyana."}, status=status.HTTP_400_BAD_REQUEST)

#             # Check if email already exists
#             existing_parent = Parent.objects.filter(email=email).first()
#             if existing_parent:
#                 if not existing_parent.email_verified:
#                     # Check if the last verification email was sent within the last 24 hours
#                     if existing_parent.last_verification_sent and timezone.now() - existing_parent.last_verification_sent < timedelta(hours=24):
#                         # messages.error(request, 'An email verification link has already been sent. Please check your inbox.')
#                         return Response({"error": "An email verification link has already been sent. Please check your inbox."}, status=status.HTTP_400_BAD_REQUEST)
#                         # return redirect('signup')

#                     # Resend verification email
#                     verify_token = generate_random_key()
#                     existing_parent.verify_token = verify_token
#                     existing_parent.last_verification_sent = timezone.now()
#                     existing_parent.save()

#                     body = f"""
#                     Dear {existing_parent.first_name},

#                     You requested a new email verification link for your account at Guyana Digital School.
#                     Please click the link below to verify your email:

#                     {request.scheme}://{request.get_host()}/verify_email/?verify_token={verify_token}

#                     If you did not request this, please ignore this email.

#                     The GDS Team
#                     """
#                     send_templated_email_via_mandrill(
#                         "Email Verification - Guyana Digital School",
#                         body,
#                         "",
#                         email,
#                         settings.EMAIL_HOST_USER,
#                         'Guyana Digital School'
#                     )
#                     return Response({"error": "A new email verification link has been sent to your email address."}, status=status.HTTP_400_BAD_REQUEST)
#                 else:
                    
#                     return Response({"error": "This email is already registered. Kindly login using this email."}, status=status.HTTP_400_BAD_REQUEST)

#             # Check if mobile already exists
#             if Parent.objects.filter(mobile=mobile).exists():
#                 # messages.error(request, 'An account with this mobile number already exists. Please use another mobile number.')
#                 return Response({"error": "An account with this mobile number already exists. Please use another mobile number."}, status=status.HTTP_400_BAD_REQUEST)

#             # Encrypt password and generate verification token
#             encrypted_password = make_password(password)
#             verify_token = generate_random_key()

#             # Create parent record
#             parent = Parent.objects.create(
#                 first_name=first_name,
#                 middle_name=middle_name,
#                 last_name=last_name,
#                 country=country,
#                 mobile=mobile,
#                 email=email,
#                 password=encrypted_password,
#                 verify_token=verify_token,
#                 last_verification_sent=timezone.now(),
#             )

#             # Send verification email
#             body = f"""
#             Dear {first_name},

#             Thank you for signing up for the Guyana Digital School! To complete your registration and access your application, 
#             please verify your email address by clicking the link below:

#             {request.scheme}://{request.get_host()}/verify_email/?verify_token={verify_token}

#             This step ensures the security of your account and confirms your eligibility for our platform. 
#             If you did not wish to initiate this request, please ignore this email.

#             For assistance, contact us at support@digitalschool.moe.edu.gy.

#             Welcome to Guyana Digital School!

#             The GDS Team
#             """
#             send_templated_email_via_mandrill(
#                 "Email Verification - Guyana Digital School",
#                 body,
#                 "",
#                 email,
#                 settings.EMAIL_HOST_USER,
#                 'Guyana Digital School'
#             )
            

#         # If the request is not POST, render the signup page
#         return Response({"message": "An email for verification has been sent to your email address."}, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['POST'])
#     def api_reset_password(self,request):
#         email = request.data.get('email')
#         parent = Parent.objects.filter(email=email)
#         if not parent.exists():
#             return Response({"error": "Parent with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)

#         parent = parent.last()

#         # Check if the reset request count exceeds the limit within 24 hours
#         current_time = timezone.now()
#         if parent.reset_request_time and (current_time - parent.reset_request_time) <= timedelta(hours=24):
#             if parent.reset_request_count >= 3:
#                 return Response({"error": "You have exceeded the maximum number of reset requests within 24 hours."}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             # Reset the count if 24 hours have passed
#             parent.reset_request_count = 0
#             parent.reset_request_time = current_time

#         verify_token = generate_random_key()
#         parent.forgot_token = verify_token
#         parent.reset_request_count += 1
#         parent.reset_request_time = current_time
#         parent.save()

#         body = f"""
#         Dear {parent.first_name},

#         Please reset your password through the following link:

#         {request.scheme}://{request.get_host()}/reset_password/?forgot_token={verify_token}

#         If you did not wish to initiate this request, please ignore this email.

#         For assistance, contact us at support@digitalschool.moe.edu.gy.

#         The GDS Team
#         """
#         html_content = ""

#         try:
#             send_templated_email_via_mandrill(
#                 "Reset Password - Guyana Digital School", body, html_content, email, settings.EMAIL_HOST_USER, 'Guyana Digital School'
#             )
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"message": "Link to reset your password is sent successfully"}, status=status.HTTP_200_OK)
        
        
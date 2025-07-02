import jwt
from django.conf import settings
from pip._internal.resolution.resolvelib.base import Candidate
from rest_framework import permissions

from user_details.exceptions import UserAccountBlockedException
from utils.user_sesssion import get_custom_session, set_custom_session

from .models import User, UserTokens
# from apps.candidates.models import Candidate

CUSTOM_MESSAGE = "You don't have permission to do this action!"


class IsUserUnblockedPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        
        if 'HTTP_AUTHORIZATION' in request.META and request.META['HTTP_AUTHORIZATION']:

            authtoken = request.META['HTTP_AUTHORIZATION']

            if 'bearer ' in authtoken:
                usertoken = authtoken.split()[1]
            else:
                usertoken = authtoken
            decode = jwt.decode(
                usertoken, settings.SECRET_KEY, algorithms='HS256')

            if UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.user = Candidate.objects.get(id=request.id)
                    return True
            raise UserAccountBlockedException

        else:
            return True
        

class IsCandidateblockedPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):

        if request.META['HTTP_AUTHORIZATION']:

            authtoken = request.META['HTTP_AUTHORIZATION']

            if 'bearer ' in authtoken:
                usertoken = authtoken.split()[1]
            else:
                usertoken = authtoken
        
            decode = jwt.decode(
                usertoken, settings.SECRET_KEY, algorithms='HS256')

            if UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.user = Candidate.objects.get(id=request.id)
                    return True
            raise UserAccountBlockedException

        else:
            raise UserAccountBlockedException
        
class IsUserBlockedPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE


    def has_permission(self, request, view):

        if request.META['HTTP_AUTHORIZATION']:

            authtoken = request.META['HTTP_AUTHORIZATION']

            if 'bearer ' in authtoken:
                usertoken = authtoken.split()[1]
            else:
                usertoken = authtoken
                
            decode = jwt.decode(
                usertoken, settings.SECRET_KEY, algorithms='HS256')

            if UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.user = User.objects.get(id=request.id)
                    return True
            raise UserAccountBlockedException

        else:
            raise UserAccountBlockedException



class IsAdminUserblockedPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):

        if request.META['HTTP_AUTHORIZATION']:

            authtoken = request.META['HTTP_AUTHORIZATION']

            if 'bearer ' in authtoken:
                usertoken = authtoken.split()[1]
            else:
                usertoken = authtoken
            decode = jwt.decode(
                usertoken, settings.SECRET_KEY, algorithms='HS256')

            if UserTokens.objects.filter(token=usertoken, admin_user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.user = Candidate.objects.get(id=request.id)
                    return True
            raise UserAccountBlockedException

        else:
            raise UserAccountBlockedException


from django.http import JsonResponse
def IsWebCandidateblockedPermission(view_func):
    message = CUSTOM_MESSAGE
   
    def wrapped_view(request, *args, **kwargs):
        try:
            
            
            authtoken=None
            if 'HTTP_AUTHORIZATION' in request.META and request.META['HTTP_AUTHORIZATION']:

                authtoken = request.META['HTTP_AUTHORIZATION']
            elif 'token' in request.GET and request.GET.get('token'):
                authtoken=request.GET.get('token')
                
                
            if not authtoken:
                session_id=request.session.session_key

               
                if session_id:
                    decode, authtoken=get_custom_session(session_id)
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.token = authtoken
                    # request.user = Candidate.objects.get(id=decode['id'])
                    return view_func(request, *args, **kwargs)
                
            if authtoken:

                if 'bearer ' in authtoken:
                    usertoken = authtoken.split()[1]
                else:
                    usertoken = authtoken
            
                decode = jwt.decode(
                    usertoken, settings.SECRET_KEY, algorithms='HS256')

                if UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                    if 'id' in decode and decode['id']:
                        request.META['id'] = decode['id']
                        request.id = decode['id']
                        request.token = authtoken
                        request.user = Candidate.objects.get(id=request.id)
                        
                        set_custom_session(request)
                        
                        return view_func(request, *args, **kwargs)
                raise UserAccountBlockedException

            else:
                raise UserAccountBlockedException
            
        except Exception as e:
            print(e)
            return JsonResponse({'error': message}, status=403)
    
    return wrapped_view

from datetime import datetime

import jwt
from django.conf import settings
from rest_framework import permissions

from user_details.exceptions import UserAccountBlockedException

from .models import User, UserTokens

CUSTOM_MESSAGE = "You don't have permission to do this action!"


class IsUserUnblockedPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE
    
    def has_permission(self, request, view):
        try:
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
        except:
            return True
        

class IsUserblockedPermission(permissions.BasePermission):
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
           
            if 'access_type' in decode and decode['access_type'] == 'vendor' and UserTokens.objects.filter(token=usertoken, vendor_user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.access_type = decode['access_type']
                    request.user = Vendor.objects.get(id=request.id)
                    return True
                
            elif UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.user = User.objects.get(id=request.id)
                    return True
            raise UserAccountBlockedException

        else:
            raise UserAccountBlockedException


class IsVendorrblockedPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):

        if 'HTTP_AUTHORIZATION' in request.META and request.META['HTTP_AUTHORIZATION']:

            # import pdb
            # pdb.set_trace()
            
            authtoken = request.META['HTTP_AUTHORIZATION']

            if 'bearer ' in authtoken:
                usertoken = authtoken.split()[1]
            else:
                usertoken = authtoken
            decode = jwt.decode(
                usertoken, settings.SECRET_KEY, algorithms='HS256')
            

            if UserTokens.objects.filter(token=usertoken, vendor_user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.user = Vendor.objects.get(id=request.id)
                    return True
            raise UserAccountBlockedException

        else:
            raise UserAccountBlockedException
        

class IsCandidateUrlAccessPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):

        if 'HTTP_AUTHORIZATION' in request.META and request.META['HTTP_AUTHORIZATION']:
         
            authtoken = request.META['HTTP_AUTHORIZATION']
            decode_value = None
            if 'bearer ' in authtoken:
                usertoken = authtoken.split()[1]
            else:
                usertoken = authtoken
            
            spoc_user_id = request.query_params.get('spoc_id', None)
            
            try:
                
                if not spoc_user_id:
                    decode = jwt.decode(
                        usertoken, settings.SECRET_KEY, algorithms='HS256')
            
                if UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                    if 'id' in decode and decode['id']:
                        request.META['id'] = decode['id']
                        request.id = decode['id']
                        request.user = User.objects.get(id=request.id)
                        return True
                elif UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                    if 'id' in decode and decode['id']:
                        request.META['id'] = decode['id']
                        request.id = decode['id']
                        request.access_type = 'candidate'
                        request.user = Candidate.objects.get(id=request.id)
                        return True
            except:
                candidate_object = Candidate.objects.filter(unique_id=usertoken).first()
                request.candidate = candidate_object
                request.access_type = 'candidate'
                if candidate_object and spoc_user_id:
                    request.user = User.objects.get(id=spoc_user_id)
                    return True
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

            if UserTokens.objects.filter(token=usertoken, user__id=decode['id']).exists():
                if 'id' in decode and decode['id']:
                    request.META['id'] = decode['id']
                    request.id = decode['id']
                    request.user = Candidate.objects.get(id=request.id)
                    return True
            raise UserAccountBlockedException

        else:
            raise UserAccountBlockedException

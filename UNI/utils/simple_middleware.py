import re
from rest_framework_simplejwt.tokens import RefreshToken
import json
from datetime import datetime, timedelta
from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

JWT_EXP_DELTA_SECONDS=99999999

def shortcircuitmiddleware(f):
	def _shortcircuitmiddleware(*args, **kwargs):
		return f(*args, **kwargs)
	return _shortcircuitmiddleware


class HttpResponseUnAutharized(HttpResponse):
    status_code = 401



class JWTAuthenticationmiddleware(object):

	def __init__(self, get_response):
		self.get_response = get_response


	def __call__(self, request):
		response = self.get_response(request)
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	
	# http.csrf().disable()
	
	def process_response(self, request, response):
		response["Access-Control-Allow-Origin"] = "*"
		return response
	 
	def process_view(self, request, view_func, view_args, view_kwargs):
		if view_func.__name__ == "_shortcircuitmiddleware":
			try:
				# if request.META['HTTP_AUTHORIZATION']:
				# 	#print(request.META['HTTP_AUTHORIZATION']+"asda")
				# 	authtoken = request.META['HTTP_AUTHORIZATION']
				# 	import datetime

				# 	if 'bearer ' in authtoken:
				# 		usertoken = authtoken.split()[1]
				# 	else:
				# 		usertoken = authtoken

					

				# 	encode = jwt.decode(usertoken, settings.SECRET_KEY, algorithms='HS256')
				print('ddd')

				# 	if 'auth_id' in encode and encode['id']:
				# 		request.META['id'] = encode['id']
				return view_func(request, *view_args, **view_kwargs)
				# 	else:
				# 		return HttpResponseUnAutharized('{"message":"Invalid token"}', content_type="application/json")
				# else:
				# 	return HttpResponseUnAutharized('{"message":"Invalid token"}', content_type="application/json")
			except Exception as error:
				return HttpResponseUnAutharized('{"message":"Autharization required / Invalid Format"}', content_type="application/json")

		return None

	def process_exception(self, request, exception):
		# print(exception)
		return HttpResponseBadRequest('{"status":false,"message":"Request data fields missing"}', content_type="application/json")

from django.http import JsonResponse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
# from apps.candidates.serializers import CandidateSerializer

def set_custom_session(request):
    # Generate a new session or use an existing session ID
   
    # session_id = request.user.id  # Custom session ID from the parameter
    # session = SessionStore(session_key=str(session_id))
    
    request.session['token'] = request.token
    request.session['user'] = CandidateSerializer(request.user).data
    # Set data in the session
    # session['id'] = request.user.id
    # session['user'] = CandidateSerializer(request.user).data
    # session.create()  # Save the session
    
    return JsonResponse({
        "message": "Session created successfully",
        "session_id": request.token
    })



def get_custom_session(session_id):
    
    if not session_id:
        return JsonResponse({"error": "Session ID is required"}, status=400)
    
    try:
        session = SessionStore(session_key=session_id)
        
        # Check if session exists
        if not session.exists(session.session_key):
            return JsonResponse({"error": "Session not found"}, status=404)
        
        # Retrieve data from the session
        user_data = session.get('user', {})
        token = session.get('token', {})
        
        return user_data , token
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

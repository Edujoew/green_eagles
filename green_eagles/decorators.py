from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect

def wing_admin_required(wing_code):
    """
    Allows access if the user is a superuser, an EXEC role, 
    or a COORDINATOR/EXEC belonging to the specific wing (GE or MOP).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('green_eagles:login')
            
            # Superusers have global oversight
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            profile = getattr(request.user, 'profile', None)
            if not profile:
                raise PermissionDenied("No member profile found.")
                
            # Executive admins can access everything
            if profile.role == 'EXEC':
                return view_func(request, *args, **kwargs)
                
            # Check if user is a coordinator for this exact wing (or handles BOTH wings)
            if profile.role == 'COORDINATOR' and (profile.wing == wing_code or profile.wing == 'BOTH'):
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied("You do not have administrative privileges for this wing.")
        return _wrapped_view
    return decorator
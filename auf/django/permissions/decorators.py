from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404

def get_object(cls, perm=None, key='pk', arg=0, kwarg=None):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            key_val = kwargs[kwarg] if kwarg else args[arg]
            obj = get_object_or_404(cls, **{key: key_val})
            args = list(args)      # Make args mutable
            if kwarg:
                del kwargs[kwarg]
            else:
                del args[arg]
            args.insert(0, obj)
            f = user_passes_test(lambda user: user.has_perm(perm, obj))(view_func) if perm else view_func
            return f(request, *args, **kwargs)
        return wrapped_view
    return decorator

from functools import wraps


def step(step_count=1):
    """
    Convience Decorator that sets the step count and declutters the view function
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, step_count=step_count, **kwargs)

        return decorated_function

    return decorator


def sub_title(title=""):
    """
    Convience Decorator that sets the sub_title and declutters the view function
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, sub_title=title, **kwargs)

        return decorated_function

    return decorator

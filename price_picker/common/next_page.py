from flask import request, url_for


def next_page(fallback_url='main.home'):
    next_ = request.args.get('next')
    if next_ is None or not next_.startswith('/'):
        next_ = url_for(fallback_url)
    else:
        try:
            next_ = url_for(next_)
        except Exception as e:
            print(e)
    return next_

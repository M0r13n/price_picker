from flask import url_for
from flask import request


def url_for_other_page(endpoint, page, **kwargs):
    args = request.args.copy()
    args['page'] = page
    # note list(dict.items()) is used to prevent runtime error
    for key, value in list(args.items()):
        if value == '__None':
            del args[key]
    return url_for(endpoint, **args, **kwargs)

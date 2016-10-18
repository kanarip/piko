from flask import abort
from flask import g
from flask import redirect
from flask import url_for

from functools import wraps

def role_required(f, role):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.get('user', None) is None:
            return redirect(url_for('piko.login', next=request.url))

        if role not in [ 'candlepin_admin' ]:
            return abort(403)

        return f(*args, **kwargs)

    return decorated_function

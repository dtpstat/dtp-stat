from threading import local

_user = local()


def get_current_user():
    try:
        return _user.value
    except:
        return None
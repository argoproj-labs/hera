host = None
token = None


def set_global_host(h):
    """Sets the Argo Workflows host at a global level so services can use it"""
    global host
    host = h
    print()


def get_global_host():
    """Returns the Argo Workflows global host"""
    return host


def set_global_token(t):
    """Sets the Argo Workflows token at a global level so services can use it"""
    global token
    token = t


def get_global_token():
    """Returns the Argo Workflows global token"""
    return token

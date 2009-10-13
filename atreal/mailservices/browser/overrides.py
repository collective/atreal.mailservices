"""
"""
from zope.publisher.browser import isCGI_NAME
from zope.i18n.interfaces import IUserPreferredCharsets
from Products.Five.browser.decode import _decode


def processInputs(request, charsets=None):
    """ Override Products.Five.browser.decode.processInputs
    """
    if charsets is None:
        envadapter = IUserPreferredCharsets(request)
        charsets = envadapter.getPreferredCharsets() or ['utf-8']
    
    for name, value in request.form.items():
        if not (isCGI_NAME(name) or name.startswith('HTTP_')):
            # XXX => really dirty
            if name=='groups' or name=='users':
                request.form[name] = value
            elif isinstance(value, str):
                request.form[name] = _decode(value, charsets)
            elif isinstance(value, list):
                request.form[name] = [ _decode(val, charsets)
                                       for val in value
                                       if isinstance(val, str) ]
            elif isinstance(value, tuple):
                request.form[name] = tuple([ _decode(val, charsets)
                                             for val in value
                                             if isinstance(val, str) ])

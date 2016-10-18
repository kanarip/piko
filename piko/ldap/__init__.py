import _ldap
import ldap
import ldap.async
import ldap.controls
import ldap.filter
import time

from piko import App
from piko.celery import celery
app = App('piko')

@celery.task(bind=True)
def get_effective_rights(subject_dn, subject_pw, object_dn, object_attrs):
    """
        Obtain the effective rights that the subject holds over the object,
        as a post-processor for other functions.

        This version of :py:func:`piko.ldap.LDAP.get_effective_rights` is
        intended to run asynchronously through background worker processes.

        :param  subject_dn:     The subject or actor.

        :param  subject_pw:     The subject's or actor's bind password. If
                                not specified, it is assumed the default bind
                                credentials can proxy authorize the connection.

        :param  object_dn:      The object or actee.

        :param  object_attrs:   A list of attributes to return for the object
                                or actee.
    """
    l = LDAP()

    if not subject_pw == None:
        l.bind(dn=subject_dn, password=subject_pw)
    else:
        # TODO: Proxy authz
        pass

    sctrls = [ldap.controls.simple.GetEffectiveRightsControl(True, 'dn: %s' % (subject_dn.encode('utf-8')))]
    l.set_option(_ldap.OPT_SERVER_CONTROLS, sctrls)
    return l.get_entry(subject_dn, object_dn, sctrls=sctrls)

class LDAP(ldap.ldapobject.ReconnectLDAPObject):
    #: The URI to the LDAP server.
    uri = app.config.get('LDAP_URI', None)

    #: The default bind DN for this LDAP connection
    bind_dn = app.config.get('LDAP_BIND_DN', None)

    #: The default bind password for this LDAP connection
    bind_pw = app.config.get('LDAP_BIND_PW', None)

    def __init__(self):
        """
            Create an LDAP object.
        """
        ldap.ldapobject.ReconnectLDAPObject.__init__(
                self,
                self.uri,
                retry_max=200,
                retry_delay=1.0
            )

    def __repr__(self):
        """
            Return the representation of this class.

            .. NOTE::

                This is deliberately associated with the class name
                and the current credentials, in order to facilitate
                caching -- :py:mod:`flask.ext.cache.Cache` uses
                :py:func:`__repr__` to form the cache key.
        """
        return "LDAP(%r)" % (self.bind_dn)

    def bind(self, dn=None, password=None):
        if dn == None:
            dn = self.bind_dn
        else:
            self.bind_dn = dn

        if password == None:
            password = self.bind_pw
        else:
            self.bind_pw = password

        return self.simple_bind_s(dn, password)

    def search(self):
        self.bind()
        _search = ldap.ldapobject.ReconnectLDAPObject.search(
                self,
                'dc=example,dc=org',
                scope = ldap.SCOPE_SUBTREE,
                filterstr = '(|(objectclass=*)(objectclass=ldapsubentry))',
                attrlist = ['*', 'nsuniqueid', 'nsrole'],
                attrsonly = False
            )

        _results = []
        _result_type = None

        while not _result_type == ldap.RES_SEARCH_RESULT:
            (_result_type, _result) = self.result(_search, False, 0)

            if not _result == None:
                for (dn, attrs) in _result:
                    task = get_effective_rights.delay(self.bind_dn, self.bind_pw, dn, attrs)
                    _results.append((dn, attrs, task.id))

        return _results

    def get_effective_rights(self, subject_dn, subject_pw, object_dn, object_attrs):
        """
            Obtain the effective rights that the subject holds over the object.

            This is the same as the :py:func:`piko.ldap.get_effective_rights` function,
            except that it waits for the task submitted to be completed.
        """
        task = get_effective_rights.delay(subject_dn, subject_pw, object_dn, object_attrs)
        task.wait()

    def get_entry(self, bind_dn, entry_dn, sctrls=[]):
        results = self.search_ext_s(entry_dn, ldap.SCOPE_BASE, '(|(objectclass=*)(objectclass=ldapsubentry))', serverctrls=sctrls)
        return (results[0][0], results[0][1])


    def add_entry(self, entry_dn, entry_attrs):
        pass

    def modify_entry(self, entry_dn, entry_attrs):
        pass

    def delete_entry(self, entry_dn):
        pass

__all__ = [
        'get_effective_rights',
        'LDAP'
    ]

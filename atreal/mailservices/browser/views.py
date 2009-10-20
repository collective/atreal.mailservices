"""
"""
from Acquisition import aq_inner
from itertools import chain

from zope.component import getMultiAdapter, queryUtility
from zope.interface import implements

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from kss.core.interfaces import IKSSView
from plone.app.kss.plonekssview import PloneKSSView as base
from kss.core import kssaction

from atreal.mailservices import MailServicesMessageFactory as _
from atreal.mailservices.browser.controlpanel import IMailServicesSchema


def merge_search_results(results, key):
    """Merge member search results.
    Based on PlonePAS.browser.search.PASSearchView.merge.
    """
    output={}
    for entry in results:
        id=entry[key]
        if id not in output:
            output[id]=entry.copy()
        else:
            buf=entry.copy()
            buf.update(output[id])
            output[id]=buf
    return output.values()


class MailServicesView(BrowserView):
    """ 
    """

    @property
    def _options (self):
        """
        """
        _siteroot = queryUtility (IPloneSiteRoot)
        return IMailServicesSchema (_siteroot)
    
    def recipients(self):
        """ 
        """
        recipients = []
        recipients.append(dict(id = 'to', title = _("To")))
        recipients.append(dict(id = 'cc', title = _("Cc")))
        # XXX : Support BCC
        #if getattr(self._options, 'mailservices_privacy_mode', True) is not True:
        #    recipients.append(dict(id = 'cc', title = _("Cc")))
        #    recipients.append(dict(id = 'bcc', title = _("Bcc")))
        return recipients
    
    
    def mailservices_additionals(self):
        """
        """
        return getattr(self._options, 'mailservices_additionals', False)
    
    def usermail_from_address(self):
        """
        """
        pms = getToolByName(self.context, 'portal_membership')
        usermail = pms.getAuthenticatedMember().email
        if not usermail:
            usermail = pms.getAuthenticatedMember().getProperty('email')
        if not usermail:
            return None
        return usermail
    
    def existing_results(self, type):
        info = []
        
        results = self.request.form.get(type, None)
        if results is None:
            return info
        
        empty_recipients = dict([(r['id'], False) for r in self.recipients()])
        
        for result in results:
            if len(result) > 2:
                recipients = empty_recipients.copy()
                flag = False
                for empty_recipient in empty_recipients:
                    if getattr(result, 'recipient_'+empty_recipient, None) == 'True':
                        recipients[empty_recipient] = True
                        flag = True
                if flag == True:
                    info.append(dict(id = result.id,
                                     title = result.title,
                                     recipients = recipients))
        return info
    
    def groups_settings(self):
        existing_results = self.existing_results('groups')
        group_results = self.group_search_results()

        requested = self.request.form.get('groups', None)
        if requested is not None:
            new_group_results = []
            for group in group_results:
                if group['id'] not in [abc['id'] for abc in existing_results]:
                    new_group_results.append(group)
            group_results = new_group_results
        
        # XXX => really dirty
        new_group_results = []
        for group in group_results:
            if group['id'] != 'AuthenticatedUsers':
                new_group_results.append(group)
        group_results = new_group_results
        
        current_settings = existing_results + group_results
        current_settings.sort(key=lambda x: str(x["title"].lower()))
        return current_settings

    def users_settings(self):
        existing_results = self.existing_results('users')
        user_results = self.user_search_results()
        
        requested = self.request.form.get('users', None)
        if requested is not None:
            new_user_results = []
            for user in user_results:
                if user['id'] not in [abc['id'] for abc in existing_results]:
                    new_user_results.append(user)
            user_results = new_user_results
        
        current_settings = existing_results + user_results
        current_settings.sort(key=lambda x: str(x["title"].lower()))
        return current_settings
    
    def _principal_search_results(self,
                                  search_for_principal,
                                  get_principal_by_id,
                                  get_principal_title,
                                  principal_type,
                                  id_key):
        """Return search results for a query to add new users or groups.
        Returns a list of dicts, as per role_settings().
        Arguments:
            search_for_principal -- a function that takes an IPASSearchView and
                a search string. Uses the former to search for the latter and
                returns the results.
            get_principal_by_id -- a function that takes a user id and returns
                the user of that id
            get_principal_title -- a function that takes a user and a default
                title and returns a human-readable title for the user. If it
                can't think of anything good, returns the default title.
            principal_type -- either 'user' or 'group', depending on what kind
                of principals you want
            id_key -- the key under which the principal id is stored in the
                dicts returned from search_for_principal
        """
        context = aq_inner(self.context)
        
        if principal_type == 'user':
            search_term = self.request.form.get('search_user_term', None)
        else:
            search_term = self.request.form.get('search_group_term', None)
            if self.request.form.get('form.button.FindAllGroups', None) is not None:
                search_term = "form.button.FindAllGroups"
        if not search_term:
            return []
        
        #existing_principals = set([p['id'] for p in self.existing_role_settings() 
        #                        if p['type'] == principal_type])
        empty_recipients = dict([(r['id'], False) for r in self.recipients()])
        info = []
        
        hunter = getMultiAdapter((context, self.request), name='pas_search')
        for principal_info in search_for_principal(hunter, search_term):
            principal_id = principal_info[id_key]
            principal = get_principal_by_id(principal_id)
            recipients = empty_recipients.copy()
            if principal is None:
                continue
            info.append(dict(id    = principal_id,
                             title = get_principal_title(principal,
                                                         principal_id),
                             recipients = recipients))
        return info

    def user_search_results(self):
        """Return search results for a query to add new users.
        Returns a list of dicts, as per role_settings().
        """
        def search_for_principal(hunter, search_term):
            if self.request.form.get('type', None) == 'searchalluser':
                return merge_search_results(chain(*[hunter.searchUsers()
                                 for field in ['login', 'fullname']]
                              ), 'userid')
            else:
                return merge_search_results(chain(*[hunter.searchUsers(**{field: search_term})
                                 for field in ['login', 'fullname']]
                              ), 'userid')
        
        def get_principal_by_id(user_id):
            acl_users = getToolByName(self.context, 'acl_users')
            return acl_users.getUserById(user_id)
        
        def get_principal_title(user, default_title):
            return user.getProperty('fullname') or user.getId() or default_title
            
        return self._principal_search_results(search_for_principal,
            get_principal_by_id, get_principal_title, 'user', 'userid')
    
    def group_search_results(self):
        """Return search results for a query to add new groups.
        Returns a list of dicts, as per role_settings().
        """
        def search_for_principal(hunter, search_term):
            if self.request.form.get('type', None) == 'searchallgroup':
                return hunter.searchGroups()
            else:
                return hunter.searchGroups(id=search_term)
        
        def get_principal_by_id(group_id):
            portal_groups = getToolByName(self.context, 'portal_groups')
            return portal_groups.getGroupById(group_id)
        
        def get_principal_title(group, _):
            return group.getGroupTitleOrName()
          
        return self._principal_search_results(search_for_principal,
            get_principal_by_id, get_principal_title, 'group', 'groupid')


class KSSMailServicesView(base):
    """KSS view for sharing page.
    """
    implements(IKSSView)

    template = ViewPageTemplateFile('mailservices.pt')
    
    @kssaction
    def updateSearchGroup(self, type='', search_term=''):
        macro_wrapper = ViewPageTemplateFile('macro_group_wrapper.pt', globals()).__of__(self)
        mailservices = getMultiAdapter((self.context, self.request,), name="mailservices")
    
        # get the html from a macro
        ksscore = self.getCommandSet('core')
        
        the_id = 'group-mailservices'
        macro = self.template.macros[the_id]
        res = macro_wrapper(the_macro=macro, instance=self.context, view=mailservices)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(the_id), res)

    @kssaction
    def updateSearchUser(self, search_term=''):
        macro_wrapper = ViewPageTemplateFile('macro_user_wrapper.pt', globals()).__of__(self)
        mailservices = getMultiAdapter((self.context, self.request,), name="mailservices")
    
        # get the html from a macro
        ksscore = self.getCommandSet('core')

        the_id = 'user-mailservices'
        macro = self.template.macros[the_id]
        res = macro_wrapper(the_macro=macro, instance=self.context, view=mailservices)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(the_id), res)




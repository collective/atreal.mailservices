"""
"""
from zope.interface import Interface
from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser.decode import setPageEncoding
from Products.Five.formlib.formbase import FiveFormlibMixin

from plone.fieldsets.fieldsets import FormFieldsets
from plone.fieldsets.form import FieldsetsInputForm

from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage

from atreal.mailservices.browser.widgets import TextAreaWidgetCustom
from atreal.mailservices.browser.overrides import processInputs
from atreal.mailservices.browser.views import MailServicesView
from atreal.mailservices import MailServicesMessageFactory as _

from Products.CMFDefault.formlib.schema import EmailLine


class IMailServicesGroupsUsersSchema(Interface):
    """
    """
    
class IMailServicesAdditionalsSchema(Interface):
    """
    """
    
class IMailServicesMailSchema(Interface):
    """
    """
    send_from_address = EmailLine(title=_(u"label_send_from",
                                          default=u"From"),
                                  description=_(u"help_send_from",
                                                default=u"Your email address."),
                                  required=True)
    subject = schema.TextLine(title=_(u"label_subject",
                                      default=u"Subject"),
                               description=_(u"help_subject",
                                             default=u"The subject of your email."),
                               required=True)
    body = schema.SourceText(title=_(u"label_message",
                                     default=u"Body"),
                             description=_(u"help_message",
                                           default=u"The body of your email."),
                             required=True)

class IMailServicesFormSchema(IMailServicesGroupsUsersSchema,
                              IMailServicesAdditionalsSchema,
                              IMailServicesMailSchema):
    """ Define the fields of the form
    """
    
ms_groupsusersset = FormFieldsets(IMailServicesGroupsUsersSchema)
ms_groupsusersset.id = 'groupsusers'
ms_groupsusersset.label = _(u"Groups & Users")

ms_additionalsset = FormFieldsets(IMailServicesAdditionalsSchema)
ms_additionalsset.id = 'additionals'
ms_additionalsset.label = _(u"Additionals mails")

ms_mailset = FormFieldsets(IMailServicesMailSchema)
ms_mailset.id = 'mail'
ms_mailset.label = _(u"Write the mail")


class MailServicesForm(MailServicesView, FieldsetsInputForm):
    """
    """
    
    form_fields = FormFieldsets(ms_groupsusersset,
                                ms_additionalsset,
                                ms_mailset)

    form_name = _(u"Mail Services")
    label = _(u"Mail Services")
    description = _(u"description_mailservices",
                    default=u"Fill the three tabs and valid the form to send an email.")

    template = ZopeTwoPageTemplateFile('mailservices.pt')
    
    def update(self):
        processInputs(self.request)
        setPageEncoding(self.request)
        super(FiveFormlibMixin, self).update()        

    def getMailForUserById(self, user_id = ""):
        """
        """
        user = self.acl_users.getUserById(user_id)
        if user is None:
            return None
        return user.getProperty('email', None)

    def getMailsForUsersByIds(self, user_ids = []):
        """
        """
        return set([self.getMailForUserById(user)
                    for user in user_ids
                    if self.getMailForUserById(user) is not None])

    def getMailsForGroupById(self, group_id = ""):
        """
        """
        group = self.acl_users.getGroupById(group_id)
        if group is None:
            return set([])
        return self.getMailsForUsersByIds(group.getAllGroupMemberIds())
    
    def getMailsForGroupsByIds(self, group_ids = []):
        """
        """
        result = set()
        for group_id in group_ids:
            result |= self.getMailsForGroupById(group_id)
        return result
    
    def getAllMails(self):
        """
        """
        self.acl_users = getToolByName(self.context, 'acl_users')
        
        mails = {
            'to': set([]),
            'cc': set([]),
            'bcc': set([]),
        }

        for recipient in self.recipients():
            #
            id = recipient['id']
            
            #
            if self.request.form.get('groups', None) is not None:
                mails[id] |= self.getMailsForGroupsByIds(
                    [group.id
                     for group in self.request.form['groups']
                     if getattr(group, 'recipient_'+id, False)=='True'])
            
            #
            if self.request.form.get('users', None) is not None:
                mails[id] |= self.getMailsForUsersByIds(
                    [user.id
                     for user in self.request.form['users']
                     if getattr(user, 'recipient_'+id, False)=='True'])
            
            #
            additionals = self.request.form.get('email_'+id, None)
            if additionals is not None:
                mails[id] |= set([additional
                                  for additional in additionals.replace(' ','').split(';')
                                  if len(additional)])
        
        #
        site_properties = getToolByName(self, 'portal_properties').site_properties
        mails['admin'] = site_properties.email_from_address
        # XXX : Support BCC
        #if getattr(self._options, 'mailservices_admin_bcc', True) is True:
        #    mails['bcc'] |= set([mails['admin'],])
        if getattr(self._options, 'mailservices_admin_bcc', True) is True:
            mails['cc'] |= set([mails['admin'],])
        
        # XXX : Support BCC
        #if getattr(self._options, 'mailservices_privacy_mode', True) is True:
        #    mails['bcc'] |= mails['to']
        #    mails['to'] = set([])
        
        #
        mails['from'] = self.request.form['form.send_from_address']
        mails['to'] |= set([mails['from'],])
        
        #
        mails['to'] = list(mails['to'])
        mails['cc'] = list(mails['cc'])
        mails['bcc'] = list(mails['bcc'])
        return mails
    
    def sendMail(self):
        """ Send an email to all emails from emailsList,
            with the info passsed in info, via the host object.
            Return a dict with the (email,exception) of problematics
            emails, or empty if no errors occured.
        """
        host = getToolByName(self, 'MailHost')
        mails = self.getAllMails()
        
        plone_utils = getToolByName(self.context, 'plone_utils')
        encoding = plone_utils.getSiteEncoding() 
        
        result = {}
        try:
            host.secureSend(self.request.form['form.body'],
                            mails['to'],
                            mails['admin'],
                            mbcc=mails['bcc'],
                            subject=self.request.form['form.subject'],
                            mcc=mails['cc'],
                            subtype='plain',
                            charset=encoding,
                            debug=False,
                            From=mails['from'])
        except Exception,e:
            result['email']=e.__class__.__name__+' : '+str(e)
        return result

    @form.action(_(u"Send"), name=u"send")
    def action_send(self, action, data):
        """
        """
        result = self.sendMail()
        res = result.get('email', None)
        if res is not None:
            self.form_reset = False
            self.status = _(u"Mail not sent.") + res
            return

        type = 'info'
        message = _(u"Mail sent.")
        
        #
        props = getToolByName(self.context, 'portal_properties')
        stp = props.site_properties
        view_action_types = stp.getProperty('typesUseViewActionInListings', ())
        
        #
        suffix = ""
        if self.context.portal_type in view_action_types:
            suffix = '/view'
        
        #
        self.request.response.redirect(self.context.absolute_url()+suffix)
        IStatusMessage(self.request).addStatusMessage(message, type=type)
        return ""

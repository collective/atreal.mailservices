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
    email_to = schema.Text(title=_(u"To"),
                           description=_(u"help_additional_recipient_type",
                                         default=u"Add more direct recipients separated by ';'"),
                           required=False)

    email_cc = schema.Text(title=_(u"Cc"),
                           description=_(u"help_additional_recipient_type",
                                         default=u"Add more direct recipients separated by ';'"),
                           required=False)

    email_bcc = schema.Text(title=_(u"Bcc"),
                            description=_(u"help_additional_recipient_type",
                                          default=u"Add more direct recipients separated by ';'"),
                            required=False)
    
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

    form_fields['email_to'].custom_widget = TextAreaWidgetCustom
    form_fields['email_cc'].custom_widget = TextAreaWidgetCustom
    form_fields['email_bcc'].custom_widget = TextAreaWidgetCustom

    form_name = _(u"Mail Services")
    label = _(u"Mail Services")
    description = _(u"description_mailservices",
                    default=u"Fill the three tabs and valid the form to send an email.")

    template = ZopeTwoPageTemplateFile('mailservices.pt')
    
    def update(self):
        processInputs(self.request)
        setPageEncoding(self.request)
        super(FiveFormlibMixin, self).update()        
    
    @form.action(_(u"Send"), name=u"send")
    def action_send(self, action, data):
        """
        """
        if isinstance(self.context, (ATImage, ATFile)):
            suffix="/view"
        else:
            suffix=""
        self.request.response.redirect(self.context.absolute_url()+suffix)
        IStatusMessage(self.request).addStatusMessage(_(u"Mail sended."),
                                                      type='info')
        return ""
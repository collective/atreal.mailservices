from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.schema import SourceText, TextLine, Choice, Bool, List
from zope.formlib import form

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from atreal.mailservices import MailServicesMessageFactory as _
from plone.app.controlpanel.form import ControlPanelForm

DEFAULT_MAILTEMPLATE_SUBJECT = \
u"""[${portal_title}] New Publication"""

DEFAULT_MAILTEMPLATE_BODY = \
u"""Publication of new document on ${portal_title} : ${object_title} at ${object_url}"""

class IMailServicesSchema(Interface):

    # XXX : Support BCC
    #mailservices_privacy_mode = Bool(
    #    title=_(u'label_privacy_mode',
    #            default=u"Privacy Mode ?"),
    #    description=_(u"help_privacy_mode",
    #                  default=u"This option allows to the user to choose cc to send a mail."),
    #    default=True,
    #    required=True)

    mailservices_admin_bcc = Bool(
        title=_(u'label_admin_bcc',
                default=u"Would you like Adminstrator of this Plone Site receive all mails ?"),
        description=_(u"help_admin_bcc",
                      default=u"This will mail each mail sended with MailServices to Portal Administrator."),
        default=True,
        required=True)

    mailservices_additionals = Bool(
        title=_(u'label_mailservices_additionals',
                default=u"Would you like Users can send mail to additionals recipients ?"),
        description=_(u"help_mailservices_additionals",
                      default=u"This will add additionals fields to MailServices form to add mail address manually."),
        default=False,
        required=True)

    mailservices_subject = TextLine(
        title=_(u'label_mailservices_subject',
                default=u"Default Subject"),
        description=_(u"help_mailservices_subject",
                      default=u"Default subject. You can use ${portal_title}, ${object_title}, ${object_url} to replace with values."),
        default = DEFAULT_MAILTEMPLATE_SUBJECT,
        required=True
    )
    
    mailservices_body = SourceText(
        title=_(u'label_mailservices_body',
                default=u"Message template"),
        description=_(u"help_mailservices_body",
                      default=u"Default body message. You can use ${portal_title}, ${object_title}, ${object_url} to replace with values."),
        default = DEFAULT_MAILTEMPLATE_BODY,
        required=True
    )

class MailServicesControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMailServicesSchema)

    def __init__(self, context):
        super(MailServicesControlPanelAdapter, self).__init__(context)

    # XXX : Support BCC
    #mailservices_privacy_mode = ProxyFieldProperty(IMailServicesSchema['mailservices_privacy_mode'])
    mailservices_admin_bcc = ProxyFieldProperty(IMailServicesSchema['mailservices_admin_bcc'])
    mailservices_additionals = ProxyFieldProperty(IMailServicesSchema['mailservices_additionals'])
    mailservices_subject = ProxyFieldProperty(IMailServicesSchema['mailservices_subject'])
    mailservices_body = ProxyFieldProperty(IMailServicesSchema['mailservices_body'])

class MailServicesControlPanel(ControlPanelForm):
    form_fields = form.FormFields(IMailServicesSchema)
    label = _("MailServices settings")
    description = _("MailServices settings for this site.")
    form_name = _("MailServices settings")

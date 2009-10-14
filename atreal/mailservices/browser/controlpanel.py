from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.schema import TextLine, Choice, Bool, List
from zope.formlib import form

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from atreal.mailservices import MailServicesMessageFactory as _
from plone.app.controlpanel.form import ControlPanelForm

class IMailServicesSchema(Interface):

    mailservices_privacy_mode = Bool(
        title=_(u'label_privacy_mode',
                default=u"Privacy Mode ?"),
        description=_(u"help_privacy_mode",
                      default=u"This option allows to the user to choose cc to send a mail."),
        default=True,
        required=True)

    mailservices_admin_bcc = Bool(
        title=_(u'label_admin_bcc',
                default=u"Would you like Adminstrator of this Plone Site receive all mails ?"),
        description=_(u"help_admin_bcc",
                      default=u"This will mail each mail sended with MailServices to Portal Administrator."),
        default=True,
        required=True)


class MailServicesControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMailServicesSchema)

    def __init__(self, context):
        super(MailServicesControlPanelAdapter, self).__init__(context)

    mailservices_privacy_mode = ProxyFieldProperty(IMailServicesSchema['mailservices_privacy_mode'])
    mailservices_admin_bcc = ProxyFieldProperty(IMailServicesSchema['mailservices_admin_bcc'])


class MailServicesControlPanel(ControlPanelForm):
    form_fields = form.FormFields(IMailServicesSchema)
    label = _("MailServices settings")
    description = _("MailServices settings for this site.")
    form_name = _("MailServices settings")

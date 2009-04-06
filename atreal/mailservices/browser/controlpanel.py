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

    mailservices_cc_field = Bool(
        title=_(u'label_cc_field',
                default=u"Cc field ?"),
        description=_(u"help_cc_field",
                      default=u"This option allows to the user to choose cc to send a mail."),
        default=True,
        required=True)
    
    mailservices_bcc_field = Bool(
        title=_(u'label_bcc_field',
                default=u"Bcc field ?"),
        description=_(u"help_bcc_field",
                      default=u"This option allows to the user to choose bcc to send a mail."),
        default = True,
        required=True)

class MailServicesControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMailServicesSchema)

    def __init__(self, context):
        super(MailServicesControlPanelAdapter, self).__init__(context)

    mailservices_cc_field = ProxyFieldProperty(IMailServicesSchema['mailservices_cc_field'])
    mailservices_bcc_field = ProxyFieldProperty(IMailServicesSchema['mailservices_bcc_field'])
    
class MailServicesControlPanel(ControlPanelForm):
    form_fields = form.FormFields(IMailServicesSchema)
    label = _("MailServices settings")
    description = _("MailServices settings for this site.")
    form_name = _("MailServices settings")

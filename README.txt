==================================
atreal.mailservices Package Readme
==================================

Overview
--------

MailServices allowing to send a mail to portal's users and groups.

Description
-----------

* This very lightweight plone products let's you mailing people from your
 portal, by groups or by choosing wished users.

* It allows you to mail freely people that are'nt members of the portals too,
 but WITHOUT ANY VERIFICATION! (for the moment)

* Otherwise, it adds a document action and a user action, which works in the
 same way that classic plone 'send_to' action, but let's you choosing your
 target by scanning the portal groups/users.

* It adds too a user action, which works in the same way that classic
 plone 'send_to' action, but let's you choosing your target by scanning the
 portal groups/users.

* Manager can choose in ControlPanel :
  - default subject,
  - default body,
  - if he will receive a copy of each mail sent with mailservices,
  - if users can sent mail not only to users and groups but to additionals
  recipients.

* Mail is sent from user email adress.
 
 
Important
---------

Permission is set for 'Manager and 'Member'


Note
----

Bcc support is coded but when you send an email, all recipients can see the list
of blind copy carbon recipients. That's why we have unactivated the bcc support
while we investigate on that issue.


Authors
-------

:atReal Team - contac@atreal.net :
Matthias Broquet <tiazma>
Florent Michon <f10w>


Credits
-------

* Sponsorised by ML-COM - www.ml-com.com (and some international research labs)


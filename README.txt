==================================
atreal.mailservices Package Readme
==================================

Overview
--------

MailServices allows to send emails to portal's users and groups.


Description
-----------

* This very lightweight plone product let's you mailing people from your
 portal, by groups or by selecting users.

* It equally allows you to mail people that are'nt members of the portals,
 but WITHOUT ANY VERIFICATION! (for the moment).

* Otherwise, it adds a document action, which works in the
 same way that classic plone 'send_to' action, but let's you choosing your
 target by scanning the portal groups/users.

* It also adds an user action, which works in the same way as described above.

* Manager can choose in ControlPanel :
  - default subject,
  - default body,
  - if he will receive a copy of each mail sent,
  - if users are able to send mails to non-portal's users.

* Mails are sent from user email address. For security purposes, this can't be
  modified.
 
 
Important
---------

Permission is set for 'Manager and 'Member'


Note
----

Bcc support is currently implemented in a branche. However, due to MailHost behaviour,
all recipients can see the bcc list.
We are working on this issue, feel free to send your proposals in case you have some.


Authors
-------

:atReal Team - contac@atreal.net :
Matthias Broquet <tiazma>
Florent Michon <f10w>


Credits
-------

* Sponsorised by ML-COM - www.ml-com.com (and some international research labs)


TODO
----

* Make BCC mailing work.
* Modify template mechanism to adopt the same granularity that's provided in 
  collective.contentrule.mail.


# -*- coding: utf-8 -*-
{
    'name': 'Registration App',
    'version': '17.0',
    'summary': """ Registration App Summary """,
    'author': 'Abdelfatah Mohamad',
    'website': 'abdelfatah.mohamad.99@gmail.com',
    'depends': ['website_slides', ],
    "data": [
        
        "views/registration_application_views.xml",
        "security/ir.model.access.csv",
        "views/templates.xml",
        "views/slide_channel_views.xml",
        "data/corn.xml",
        "data/mails.xml"
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}


# -*- coding: utf-8 -*-
{
    'name': 'Custom Event',
    'version': '1.0',
    'category': 'Marketing/Events',
    'sequence': 146,
    'summary': 'Custom Event',
    'description': """Custom Event""",
    'depends': ['web', 'website', 'auth_custom'],
    'data': [
        'security/event_security.xml',
        'security/ir.model.access.csv',
        'views/event_management_event_views.xml',
        'views/event_menu_views.xml',
        
        'views/snippets/event_custom.xml',
        'views/snippet.xml',
    ],
    'demo' : [
        'demo/events.xml',
    ],
    'assets': {
       'web.assets_frontend': [
            'event_custom/static/src/js/event_custom.js',
       ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

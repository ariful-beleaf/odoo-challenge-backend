# -*- coding: utf-8 -*-
{
    'name': 'Custom Auth',
    'version': '1.0',
    'category': 'Authentication',
    'summary': 'Custom authentication module with JWT support',
    'description': """
        This module provides JWT-based authentication for Odoo.
        Features:
        - JWT token generation on successful login
        - Secure password validation
        - API endpoint for authentication
    """,
    'depends': ['base', 'web', 'base_setup'],
    'data': [
        "views/res_config_settings_views.xml"
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

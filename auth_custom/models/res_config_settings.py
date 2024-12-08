# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_auth_custom = fields.Boolean("JWT Authentication")
    signature_type = fields.Selection([("secret", "Secret"), ("public_key", "Public key")], required=True, default='secret', config_parameter='auth_custom.signature_type')
    secret_key = fields.Char(config_parameter='auth_custom.secret_key', default='99ba3de366b2af12eee8e4747ac874bf8403162eeb7493dd50a4ad1def2f62fa')
    secret_algorithm = fields.Selection(
        [
            # https://pyjwt.readthedocs.io/en/stable/algorithms.html
            ("HS256", "HS256 - HMAC using SHA-256 hash algorithm"),
            ("HS384", "HS384 - HMAC using SHA-384 hash algorithm"),
            ("HS512", "HS512 - HMAC using SHA-512 hash algorithm"),
        ],
        default="HS256",
        config_parameter='auth_custom.secret_algorithm',
    )
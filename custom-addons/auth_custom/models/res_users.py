from odoo import models, fields, api
import jwt
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_credentials(self, password, user_agent_env):
        if self.env.context.get('auth_custom'):
            if not self.env.user:
                self.env.user = self
        return super()._check_credentials(password, user_agent_env)

    @api.model
    def verify_jwt_token(self, token):
        try:
            secret_key = self.env['ir.config_parameter'].sudo().get_param(
                'custom_auth.jwt_secret_key', 'your-secret-key'
            )
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')

            if not user_id:
                raise AccessDenied()

            user = self.browse(user_id)
            if not user.exists():
                raise AccessDenied()

            return user
        except jwt.ExpiredSignatureError:
            raise AccessDenied('Token has expired')
        except jwt.InvalidTokenError:
            raise AccessDenied('Invalid token')
        except Exception:
            raise AccessDenied()
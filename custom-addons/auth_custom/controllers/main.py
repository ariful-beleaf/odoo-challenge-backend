from odoo import http
from odoo.http import request, Response
import jwt
import datetime
import json
# from werkzeug.security import check_password_hash

class CustomAuthController(http.Controller):
    @http.route('/api/signin', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def signin(self, **kwargs):
        try:
            # Get request data
            data = json.loads(request.httprequest.data.decode('utf-8'))
            login = data.get('login')
            password = data.get('password')

            if not login or not password:
                return self._json_response(
                    {'error': 'Missing login or password'},
                    status=400
                )

            # Find user
            user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)

            if not user:
                return self._json_response(
                    {'error': 'Invalid credentials'},
                    status=401
                )

            # Verify password
            user_agent_env = {'interactive': True}
            try:
                user.with_context({'auth_custom': True})._check_credentials(password, user_agent_env)
            except Exception as e:
                return self._json_response(
                    {'error': 'Invalid credentials'},
                    status=401
                )

            # Generate JWT token
            payload = {
                'user_id': user.id,
                'login': user.login,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }

            secret_key = request.env['ir.config_parameter'].sudo().get_param(
                'auth_custom.secret_key', '99ba3de366b2af12eee8e4747ac874bf8403162eeb7493dd50a4ad1def2f62fa'
            )
            algorithm = request.env['ir.config_parameter'].sudo().get_param(
                'auth_custom.signature_type'
            ) or 'HS256'

            token = jwt.encode(
                payload,
                secret_key,
                algorithm=algorithm
            )

            return self._json_response({
                'token': token,
                'id': user.id,
                'name': user.name,
                'login': user.login,
            })

        except Exception as e:
            return self._json_response(
                {'error': str(e)},
                status=500
            )

    def _json_response(self, data, status=200):
        return {
            'status': status,
            'data': data
        }

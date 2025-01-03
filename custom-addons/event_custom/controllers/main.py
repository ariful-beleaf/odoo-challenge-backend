from odoo import http, fields
from odoo.http import request, Response
import jwt
import json

from datetime import datetime
from odoo.exceptions import AccessDenied, ValidationError

class CustomEventController(http.Controller):

    @http.route(['/api/events', '/api/events/<int:id>'], type='json', auth='none', methods=['POST'], cors='*', csrf=False)
    def create_event(self, **kwargs):
        try:
            # Verify JWT and admin rights
            token = request.httprequest.headers.get('Authorization')
            if not token:
                return self._json_response({'error': 'No token provided'}, 401)

            payload, user = self.validate_request(request)
            expiry_datetime = datetime.fromtimestamp(payload['exp'])
            print(f"Token expires at: {expiry_datetime}")

            if datetime.now() >= expiry_datetime:
                return self._json_response({'error': 'Token expired.'}, 401)


            # Validate request and get user
            if not user:
                return self._json_response({'error': 'No user found'}, 401)
            if not user.has_group('event_custom.group_event_manager'):
                return self._json_response({'error': 'User has no access'}, 401)

            data = json.loads(request.httprequest.data)
            if data and not data.get('id'):

                if not data.get('name') or not data.get('location') or not data.get('date'):
                    return self._json_response({'error': 'Data missing: Name or Location or Date'}, 401)
                if data.get('date'):
                    try:
                        date_val = fields.Datetime.from_string(data['date'])
                        if not isinstance(date_val, datetime):
                            return self._json_response({'error': 'Invalid date format. Expected: YYYY-MM-DD HH:MM:SS'}, 401)
                    except Exception:
                        return self._json_response({'error': 'Invalid date format. Expected: YYYY-MM-DD HH:MM:SS'}, 400)

                event = request.env['event.management.event'].with_user(user).create({
                    'name': data['name'],
                    'location': data['location'],
                    'date': data['date']
                })

                return self._json_response({
                    'id': event.id,
                    'name': event.name,
                    'location': event.location,
                    'date': event.date.strftime('%Y-%m-%d %H:%M:%S'),
                }, 201)

            elif data and data.get('id'):
                id = kwargs.get('id')
                event = request.env['event.management.event'].with_user(user).browse(int(kwargs.get('id')))
                if not event:
                    return self._json_response({'error': f'Event not found: {id}'}, 404)
                if event:
                    if data.get('id'): del data['id']
                    event.update(data)
                    return self._json_response({'message': 'Update Successful.'}, 200)
            else:
                return self._json_response({'error': f'No Data provided'}, 400)

            
        except Exception as e:
            return self._json_response({'error': str(e)}, 500)

    @http.route('/api/events/<int:id>', type='http', auth='none', methods=['GET', 'PUT'], cors='*', csrf=False)
    def get_event(self, **kwargs):
        if request.httprequest.method == 'PUT':
            return self.update_event(**kwargs)
        try:
            # Verify JWT token
            token = request.httprequest.headers.get('Authorization')
            if not token:
                return self._json_response({'error': 'No token provided'}, 401)

            payload, user = self.validate_request(request)
            expiry_datetime = datetime.fromtimestamp(payload['exp'])
            print(f"Token expires at: {expiry_datetime}")

            if datetime.now() >= expiry_datetime:
                return self._json_response({'error': 'Token expired.'}, 401)

            # Validate request and get user
            if not user:
                return self._json_response({'error': 'No user found'}, 401)
            if not user.has_group('event_custom.group_event_user') and not user.has_group('event_custom.group_event_manager'):
                return self._json_response({'error': 'User has no access'}, 401)

            if kwargs.get('id'):
                event_id = kwargs.get('id')
                events = request.env['event.management.event'].with_user(user).search_read([('id', '=', event_id)], ['id', 'name', 'location', 'date'])
                if not events:
                    return self._json_response({'error': f'No event found for id: {event_id}'}, 400)

                # Convert datetime to string in ISO format
                for event in events:
                    if event.get('date'):
                        event['date'] = fields.Datetime.to_string(event['date'])

                return self._json_response(events[0], status=200)
            
        except Exception as e:
            return self._json_response({'error': str(e)}, 500)

    @http.route(['/api/events'], type='http', auth='none', methods=['GET'], cors='*', csrf=False)
    def list_events(self, **kwargs):
        try:
            # Verify JWT token
            token = request.httprequest.headers.get('Authorization')
            if not token:
                return self._json_response({'error': 'No token provided'}, 401)

            payload, user = self.validate_request(request)
            expiry_datetime = datetime.fromtimestamp(payload['exp'])
            print(f"Token expires at: {expiry_datetime}")

            if datetime.now() >= expiry_datetime:
                return self._json_response({'error': 'Token expired.'}, 401)


            # Validate request and get user
            if not user:
                return self._json_response({'error': 'No user found'}, 401)
            if not user.has_group('event_custom.group_event_user') and not user.has_group('event_custom.group_event_manager'):
                return self._json_response({'error': 'User has no access'}, 401)

            # Get pagination parameters
            if kwargs.get('page[number]') and kwargs.get('page[size]'):
                page = int(kwargs.get('page[number]', 1))
                size = int(kwargs.get('page[size]', 5))
                
                # Get events with pagination
                offset = (page - 1) * size

                events = request.env['event.management.event'].with_user(user).search_read(
                    [], ['id', 'name', 'location', 'date'], 
                    offset=offset, limit=size
                )
            else:
                page = 1
                events = request.env['event.management.event'].with_user(user).search_read(
                    [], ['id', 'name', 'location', 'date'], 
                )
                size = len(events)
                

            # Convert datetime to string in ISO format
            for event in events:
                if event.get('date'):
                    event['date'] = fields.Datetime.to_string(event['date'])
            print(f'events ===>>> {events}')
            return self._json_response({
                'events': events,
                'meta': {
                    'page': page,
                    'size': size,
                    'total': request.env['event.management.event'].with_user(user).search_count([])
                }
            })
            
        except Exception as e:
            return self._json_response({'error': str(e)}, 500)

    def update_event(self, **kwargs):
        try:
            # Verify JWT token
            token = request.httprequest.headers.get('Authorization')
            if not token:
                return self._json_response({'error': 'No token provided'}, 401)


            payload, user = self.validate_request(request)
            expiry_datetime = datetime.fromtimestamp(payload['exp'])
            if datetime.now() >= expiry_datetime:
                return self._json_response({'error': 'Token expired.'}, 401)

            # Validate request and get user
            if not user:
                return self._json_response({'error': 'No user found'}, 401)
            if not user.has_group('event_custom.group_event_user') and not user.has_group('event_custom.group_event_manager'):
                return self._json_response({'error': 'User has no access'}, 401)

            if kwargs.get('id'):
                event_id = kwargs.get('id')
                events = request.env['event.management.event'].with_user(user).search([('id', '=', event_id)])
                if not events:
                    return self._json_response({'error': f'No event found for id: {event_id}'}, 400)

                data = json.loads(request.httprequest.data)
                if not data.get('name') and not data.get('location') and not data.get('date'):
                    return self._json_response({'error': 'Data missing: Name or Location or Date'}, 400)

                if events:
                    if data.get('id'): del data['id']
                    events.with_user(user).write(data)
            
                return self._json_response({}, 200)
            
        except Exception as e:
            return self._json_response({'error': str(e)}, 500)

    @http.route('/api/events/<int:id>', type='http', auth='none', methods=['DELETE'], cors='*', csrf=False)
    def delete_event(self, **kwargs):
        try:
            # Verify JWT token
            token = request.httprequest.headers.get('Authorization')
            if not token:
                return self._json_response({'error': 'No token provided'}, 401)

            payload, user = self.validate_request(request)
            expiry_datetime = datetime.fromtimestamp(payload['exp'])
            if datetime.now() >= expiry_datetime:
                return self._json_response({'error': 'Token expired.'}, 401)

            # Validate request and get user
            if not user:
                return self._json_response({'error': 'No user found'}, 401)
            if not user.has_group('event_custom.group_event_user') and not user.has_group('event_custom.group_event_manager'):
                return self._json_response({'error': 'User has no access'}, 401)

            if kwargs.get('id'):
                event_id = kwargs.get('id')
                events = request.env['event.management.event'].with_user(user).search([('id', '=', event_id)])
                if not events:
                    return self._json_response({'error': f'No event found for id: {event_id}'}, 400)

                if events:
                    events.with_user(user).unlink()
                    return self._json_response({}, 200)
            
        except Exception as e:
            return self._json_response({'error': str(e)}, 500)

    def _json_response(self, data, status=200):
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
            status=status
        )

    def decode_token(self, token):
        """
        Decode and validate JWT token
        Args:
            token (str): JWT token string
        Returns:
            dict: Decoded token payload if valid
        Raises:
            AccessDenied: If token is invalid or expired
        """
        if not token:
            raise AccessDenied('Token is missing')

        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        try:
            # Get secret key from system parameters
            secret_key = http.request.env['ir.config_parameter'].sudo().get_param(
                'auth_custom.secret_key', '99ba3de366b2af12eee8e4747ac874bf8403162eeb7493dd50a4ad1def2f62fa'
            )

            # Decode and verify token
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=['HS256']
            )

            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise AccessDenied('Token has expired')

            # Verify user exists and is active
            user_id = payload.get('user_id')
            if not user_id:
                raise AccessDenied('Invalid token payload')

            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists() or not user.active:
                raise AccessDenied('User not found or inactive')

            return payload

        except jwt.ExpiredSignatureError:
            raise AccessDenied('Token has expired')
        except jwt.InvalidTokenError:
            raise AccessDenied('Invalid token')
        except Exception as e:
            raise AccessDenied(str(e))

    def validate_request(self, request):
        """
        Validate request with JWT token
        Args:
            request: HTTP request object
        Returns:
            dict: Decoded token payload
            res.users: Authenticated user record
        """
        # Get token from header
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            raise AccessDenied('Authorization header missing')

        # Decode token
        payload = self.decode_token(auth_header)
        
        # Get user from payload
        user = request.env['res.users'].sudo().browse(payload.get('user_id'))
        
        return payload, user

    @http.route('/custom/events', type='json', auth='public', methods=['POST'], cors='*', csrf=False)
    def all_events(self, **kwargs):
        try:
            events = request.env['event.management.event'].sudo().search_read([], ['id', 'name', 'location', 'date'])
            return {'events' : events}
        except Exception as e:
            return self._json_response({'error': str(e)}, 500)
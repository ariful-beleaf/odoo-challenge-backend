from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EventManagementEvent(models.Model):
    _name = 'event.management.event'
    _description = 'Event Management Event'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Title', required=True, default=lambda self: _('New'), copy=False)
    location = fields.Char(string='Location', required=True)
    date = fields.Datetime(string='Date', required=True)

    _sql_constraints = [
        ('name_location_date_unique', 
         'UNIQUE(name,location,date)', 
         'Event name must be unique!'),
        
        ('check_name_length', 
         'CHECK(LENGTH(name) >= 3)', 
         'Event name must be at least 3 characters long!')
    ]

    @api.model
    def create(self, vals):
        # Check if user has create rights
        if not self.env.user.has_group('event_custom.group_event_manager'):
            raise ValidationError('Only admins can create events')
        return super(EventManagementEvent, self).create(vals)
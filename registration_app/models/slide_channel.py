# -*- coding: utf-8 -*-
import logging
from odoo.http import request
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    registration_application_ids = fields.One2many(comodel_name='registration.application', inverse_name='course_id')
    
    city_field = fields.Boolean()
    nationality_field = fields.Boolean()
    gender_field = fields.Boolean()
    hadf_support_field = fields.Boolean()
    work_field = fields.Boolean()
    student_field = fields.Boolean()
    general_abilities_field = fields.Boolean()
    high_school_percentage_field = fields.Boolean()
    name_to_url = fields.Char(string=_("Name To Url"))
    registration_application_url = fields.Char(
        string='Registration Applications URL',
        compute='_compute_registration_application_url',
    )
    @api.depends('name','name_to_url')
    def _compute_registration_application_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.name:
                name = record.with_context(self._context,lang="en_US").name.replace(' ','-')
                op = record.name_to_url.replace(' ','-') if record.name_to_url else ""
                record.registration_application_url = f"{base_url}/registration_application/{name}/{record.id}/{op}"
            else:
                record.registration_application_url = False
    current_registration_application = fields.Integer(default=0,compute="_compute_current_registration_application",store=True)
    max_registration_application = fields.Integer(default=300)

    @api.depends("registration_application_ids", "registration_application_ids.course_id")
    def _compute_current_registration_application(self):
        for record in self:
            record.current_registration_application = len(record.registration_application_ids)
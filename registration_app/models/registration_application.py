# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class RegistrationApplication(models.Model):
    _name = 'registration.application'
    _description = 'RegistrationApplication'
    _inherit = ["mail.thread","mail.activity.mixin"]
    _rec_name = "applicatian_name"

    course_id = fields.Many2one(comodel_name="slide.channel",tracking=1)
    applicatian_name = fields.Char(required=True,string="Name",tracking=1)
    acceptance_rate = fields.Float(tracking=1)
    is_accepted = fields.Boolean("Is Accepted?",tracking=1)
    age = fields.Integer("Age",compute="_compute_age",store=True)
    @api.depends('applicatian_birth_date')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.applicatian_birth_date:
                rec.age = today.year - rec.applicatian_birth_date.year - \
                    ((today.month, today.day) <
                     (rec.applicatian_birth_date.month, rec.applicatian_birth_date.day))
            else:
                rec.age = 0
    applicatian_national_id = fields.Char(required=True,string="National ID",index=True,tracking=1)
    applicatian_mobile = fields.Char(required=True, string="Mobile",tracking=1)
    applicatian_mail = fields.Char(required=True,string="Email",tracking=1)
    applicatian_city = fields.Char(string="City",tracking=1)
    applicatian_nationality = fields.Many2one('res.country',string="Nationality",tracking=1)
    applicatian_gender = fields.Selection(selection=[('male','Male'),('female','Female')],string="Gender" ,tracking=1)
    applicatian_birth_date = fields.Date(required=True,string="Birth Date",tracking=1)
    is_applicatian_hadf_support = fields.Boolean(default=False,string="hadf_support",tracking=1)
    is_applicatian_work = fields.Boolean(default=False,string="Is Working?",tracking=1)
    is_applicatian_student = fields.Boolean(default=False,string="Is Student?",tracking=1)
    percentage_of_general_abilities = fields.Float(string="General Abilities %",tracking=1)
    high_school_percentage = fields.Float(string="High School %",tracking=1)
    document_ask = fields.Boolean(default=False,string=_("Ask Document?"),tracking=1)
    document_url= fields.Char(string="URL To get Doc",compute="_compute_document_url")
    @api.depends("applicatian_name","document_ask")
    def _compute_document_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.applicatian_name and record.document_ask == True:
                name = record.applicatian_name
                record.document_url = f"{base_url}/upload-docs/{name}/{record.id}"
            else:
                record.document_url = False
    mail_sent = fields.Boolean(default=False,string=_("Email Sent?"),tracking=1)
    document = fields.Many2many('ir.attachment', string='Document',tracking=1)
    
    def set_as_ask_document(self):
        for record in self.filtered(lambda x: not x.document_ask and not x.mail_sent):
            record.document_ask = True
    
    def send_doc_mails(self):
        mail = self.sudo().env.ref(
                'registration_app.registration_application_upload_doc_mail')
        for record in self.filtered(lambda x: x.document_ask and not x.mail_sent):
            mail.send_mail(record.id,force_send=True,email_values={'email_to': record.applicatian_mail})
            record.mail_sent = True

    @api.model
    def _corn_age(self):
        today = fields.Date.today()
        for rec in self.search([]):
            if rec.applicatian_birth_date:
                rec.age = today.year - rec.applicatian_birth_date.year - \
                    ((today.month, today.day) <
                     (rec.applicatian_birth_date.month, rec.applicatian_birth_date.day))
            else:
                rec.age = 0

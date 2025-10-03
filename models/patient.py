from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HospitalPatient(models.Model):
    _name = 'hospital1.patient'
    _description = 'Patient Record'

    name = fields.Char(string="Name", required=True)
    age = fields.Integer(string="Age")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    date_of_birth = fields.Date(string="Date of Birth")
    ref = fields.Char(string="Reference", default="New Patient")
    doctor_id = fields.Many2one('hospital1.doctor', string="Doctor")
    note = fields.Text(string="Note")
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'New Patient') == 'New Patient':
                vals['ref'] = self.env['ir.sequence'].next_by_code('hospital1.patient')
        return super().create(vals_list)
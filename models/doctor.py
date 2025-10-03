from odoo import api, fields, models

class HospitalDoctor(models.Model):
    #details dans la table de modeles
    _name = "hospital1.doctor"
    _description = "Doctor"
    _inherit = ['mail.thread','mail.activity.mixin']

#champs
    name = fields.Char(string="Name", required=True)
    ref = fields.Char(string="Reference", default="New Doctor")  # Champ ajouté
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    active = fields.Boolean(string="Active", default=True)
    #
    partner_id = fields.Many2one('res.partner', string="Related Partner", required=True)

#methodes
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            #modifier les champs quon veut changer
            if vals.get('ref', 'New Doctor') == 'New Doctor':
#ir.sequence modele odoo qui gere les  sequences automatiques il est definit dans le xml dans le record
                vals['ref'] = self.env['ir.sequence'].next_by_code('hospital1.doctor')
                #creer un nouveau entite avec les valeurs modifie et la methode de creation par defaut dans le modele
        return super().create(vals_list)
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HospitalInvoice(models.Model):
    _name = 'hospital1.invoice'
    _inherit = ['mail.thread']
    _description = 'Hospital Invoice'
    _order = 'date_invoice desc'

    name = fields.Char(string="Invoice Number", default="New Invoice")

    patient_id = fields.Many2one('hospital1.patient', string="Patient", required=True)
    doctor_id = fields.Many2one('hospital1.doctor', string="Doctor", required=True)
    date_invoice = fields.Date(string="Invoice Date", default=fields.Date.today, required=True)
    date_due = fields.Date(string="Due Date", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting','waiting for confirmation'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft')


    # Lignes de facturation
    invoice_line_ids = fields.One2many('hospital1.invoice.line', 'invoice_id', string="Invoice Lines")

    # Montants calcualbles par la fonction qui existe dans compute , store veux dire
    #store veux dire sera enregistre dans la bdd  alors on pourra filtrer trier rechercher ce champs dans les vues
    subtotal = fields.Float(string="Subtotal", compute='_compute_amounts', store=True)
    tax_amount = fields.Float(string="Tax Amount", compute='_compute_amounts', store=True)
    total_amount = fields.Float(string="Total Amount", compute='_compute_amounts', store=True)

    # Informations de paiement // champs dde  plus
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance')
    ], string="Payment Method")

    notes = fields.Text(string="Notes")
#la confirmmation modifie le state et elle est faite par un groupe dutilisateurs precis (on peux le faire par un seul utilisateur cad le docteur concerne
    #et elle envoi la notification au partners

    # les methodes definies pour les bouttons sont appeles dans le ?

    def action_request_confirmation(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("Only draft invoices can request confirmation.")

            rec.state = 'waiting'

            group_doctor_users = self.env.ref('hospital1.group_doctor').users
            group_doctor_partner_ids = [user.partner_id.id for user in group_doctor_users]

            # Ajouter aussi le docteur assigné à la facture
            if rec.doctor_id and rec.doctor_id.partner_id:
                if rec.doctor_id.partner_id.id not in group_doctor_partner_ids:
                    group_doctor_partner_ids.append(rec.doctor_id.partner_id.id)

            #  Envoi de mail par admin
            emails = [user.email for user in group_doctor_users if user.email]
            if emails:
                self.env['mail.mail'].sudo().create({
                    'subject': "Demande de confirmation",
                    'body_html': "<p>📝 Une demande de confirmation a été envoyée.</p>",
                    'email_to': ','.join(emails),
                }).send()

            # Poster le message dans le fil de discussion
            rec.message_post(
                body="📝 Une demande de confirmation a été envoyée.",
                subject="Demande de confirmation",
                partner_ids=group_doctor_partner_ids,
                message_type='notification',
            )


            rec.message_subscribe(partner_ids=[rec.doctor_id.partner_id.id])

            # Abonner le docteur assigné si besoin
            rec.message_subscribe(partner_ids=[rec.doctor_id.partner_id.id])

    def action_confirm_invoice(self):
        for rec in self:
            if rec.state != 'waiting':
                raise ValidationError("Only invoices in waiting state can be confirmed.")

            rec.state = 'confirmed'

            group_accountant_users = self.env.ref('hospital1.group_accountant').users
            partner_ids = [user.partner_id.id for user in group_accountant_users]

            # ✅ Envoi de mail par admin
            emails = [user.email for user in group_accountant_users if user.email]
            if emails:
                self.env['mail.mail'].sudo().create({
                    'subject': "Confirmation de la facture",
                    'body_html': "<p>✅ La facture a été confirmée par le médecin.</p>",
                    'email_to': ','.join(emails),
                }).send()

            # Poster un message dans le thread
            rec.message_post(
                body="✅ La facture a été confirmée par le médecin.",
                subject="Confirmation de la facture",
                partner_ids=partner_ids,
                message_type='notification',
            )

    #calcul des totals de la facture
    @api.depends('invoice_line_ids.subtotal')

    def _compute_amounts(self):
        for invoice in self:
            subtotal = sum(line.subtotal for line in invoice.invoice_line_ids)
            tax_amount = subtotal * 0.19  # TVA 19%

            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = subtotal + tax_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New Invoice') == 'New Invoice':
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital1.invoice')
        return super().create(vals_list)

    def action_confirm(self):
        self.state = 'confirmed'

    def action_mark_paid(self):
        self.state = 'paid'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        self.state = 'draft'




class HospitalInvoiceLine(models.Model):
    _name = 'hospital1.invoice.line'
    _description = 'Hospital Invoice Line'
#champs dune ligne
    invoice_id = fields.Many2one('hospital1.invoice', string="Invoice", required=True, ondelete='cascade')
    description = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Unit Price", required=True)
    subtotal = fields.Float(string="Subtotal", compute='_compute_subtotal', store=True)
#calcul du cout dune ligne
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price



            #depends : depends dauttres champs , et on precise qui sont ces champs
            #onchange : reagir immediatement dans le formulaire quand le champs change mais on pourra continuer le travail
            #constrains : valider une regle metier quand on cree ou modifie un enregistrement ,
            #// : imposer une vaidation lors de la sauvegarde
            #model : methode qui sapplique au modele en general pas a un enregostrement
            #model_create_multi : pour creer plusieur record a ala fois
            #autovacuum : utilise pour les taches dauto nettoyage


# quand est ce que les methodes sont appelees :
# depends : si un change dependant est modifie
# compute : liee au champs pour remplir le champs
## via des boutton(name) ou des action serveur
# methodes liees a des evenements comme create,write , unlink etc

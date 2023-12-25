from odoo import fields, models, api, exceptions


class Member(models.Model):
    _name = "library.member"
    _description = "Library Member"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]


    member_image = fields.Binary(string='User Image', widget='image')
    email = fields.Char(string='Email')
    card_number = fields.Char(string='Card Number')
    partner_id = fields.Many2one(
        comodel_name="res.partner", delegate=True, ondelete="cascade", required=True
    )

    def action_buy_credits(self):
        checkout_action = self.env.ref('library_checkout.action_library_checkout_invoices')
        checkout_action['domain'] = [('member_id', '=', self.id),('state', '=', 'done')]
        return checkout_action.read()[0]

    @api.model_create_multi
    def create(self, vals_list):
        new_members = super().create(vals_list)
        for new_record in new_members:
            new_record['card_number'] = self.env['ir.sequence'].next_by_code('library.member')

        return new_members

    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email and not self.is_valid_email(record.email):
                raise exceptions.ValidationError("Invalid email format!")

    @staticmethod
    def is_valid_email(email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        return bool(re.match(pattern, email))

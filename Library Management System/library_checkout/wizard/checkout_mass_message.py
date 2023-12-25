
from odoo import api, exceptions, fields, models

class CheckoutMassMessage(models.TransientModel):
    _name = "library.checkout.massmessage"
    _description = "Send Message to Borrowers"

    checkout_ids = fields.Many2many(
        "library.checkout",
        string="Checkouts",
    )
    message_subject = fields.Char()
    message_body = fields.Html()

    @api.model
    def default_get(self, field_names):
        defaults_dict = super().default_get(field_names)
        checkout_ids = self.env.context.get("active_ids", [])
        defaults_dict["checkout_ids"] = [(6, 0, checkout_ids)]
        return defaults_dict

    def button_send(self):
        self.ensure_one()
        if not self.checkout_ids:
            raise exceptions.UserError("No Checkouts were selected.")
        if not self.message_subject or not self.message_body:
            raise exceptions.UserError("Subject and message body are required.")
        try:
            for checkout in self.checkout_ids:
                checkout.message_post(
                    body=self.message_body,
                    subject=self.message_subject,
                    subtype_xmlid="mail.mt_note",
                )
        except exceptions.AccessError as e:
            raise exceptions.UserError(f"Access Error: {e}")
        except Exception as e:
            raise exceptions.UserError(f"An error occurred: {e}")
        return True

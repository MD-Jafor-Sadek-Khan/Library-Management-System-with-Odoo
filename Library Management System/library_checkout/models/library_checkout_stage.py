from odoo import fields, models


class CheckoutStage(models.Model):
    _name = "library.checkout.stage"
    _description = "Checkout Stage"
    _order = "sequence"

    name = fields.Char()
    my_stage_id = fields.Many2one(comodel_name='library.checkout.stage')
    stage_number = fields.Integer()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "Requested"),
            ("open", "Borrowed"),
            ("done", "Returned"),
            ("cancel", "Canceled"),
        ],
        default="new",
    )

from odoo import models, fields

class Currency(models.Model):
    _name = 'library.currency'
    _description = 'This model describes currency type'

    name = fields.Char(string='Currency Name')

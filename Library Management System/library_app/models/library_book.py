from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Book(models.Model):

    _name = "library.book"
    _description = "Book"

    name = fields.Char("Title", required=True)
    isbn = fields.Char("ISBN")
    active = fields.Boolean("Active?", default=True)
    date_published = fields.Date()
    image = fields.Binary("Cover", widget='image')
    price = fields.Float(string='Rent/Day', default=10)
    discount_per_month = fields.Float(string='Discount/Month', default=0)
    discount_per_year = fields.Float(string='Discount/Year', default=0)
    discount_per_week = fields.Float(string='Discount/Week', default=0)

    is_available = fields.Boolean("Is Available?", compute='_compute_availability', store=True)
    available_count = fields.Integer(string='Available', default=1)

    @api.depends('available_count')
    def _compute_availability(self):
        for me in self:
            if me.available_count > 0:
                me.is_available = True
            else:
                me.is_available = False

    publisher_id = fields.Many2one("res.partner", string="Publisher")
    author_ids = fields.Many2many("res.partner", string="Authors")
    category_id = fields.Many2one(comodel_name='library.book.category', string='Category')
    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check

    def button_check_isbn(self):
        for book in self:
            if not book.isbn:
                raise ValidationError("Please provide an ISBN for %s" % book.name)
            if book.isbn and not book._check_isbn():
                raise ValidationError("%s ISBN is invalid" % book.isbn)
        return True




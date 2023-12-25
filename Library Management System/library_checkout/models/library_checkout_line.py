from odoo import api, exceptions, fields, models


class CheckoutLine(models.Model):
    _name = "library.checkout.line"
    _description = "Checkout Request Line"

    checkout_id = fields.Many2one("library.checkout", required=True)
    book_availability = fields.Integer(related='book_id.available_count', store=True)
    book_availability_bool = fields.Boolean(related='book_id.is_available', store=True)
    borrowed_count = fields.Integer(string='Borrowed')

    @api.depends('borrowed_count')
    def _compute_total_price_for_current_book(self):
        for line in self:
            line.total_price_for_current_book = line.book_id.price * line.borrowed_count

    total_price_for_current_book = fields.Float(compute='_compute_total_price_for_current_book')


    @api.depends('borrowed_count')
    def _compute_total_price_for_all_book(self):
        for line in self:
            line.total_price_for_all_book += line.book_id.price * line.borrowed_count

    total_price_for_all_books = fields.Float(string='Total')

    @api.onchange('borrowed_count')
    def onchange_change_availability(self):
        for me in self:
            if me.borrowed_count > me.book_id.available_count:
                raise exceptions.UserError("%d %s Books are Not Available at the moment" % (me.borrowed_count, me.book_id.name))
            else:
                me.book_id.available_count -= me.borrowed_count


    note = fields.Char("Notes")
    book_id = fields.Many2one("library.book", required=True, domain=[('available_count', '>', 0)])
    book_cover = fields.Binary(related="book_id.image")

from odoo import api, exceptions, fields, models
from datetime import datetime, timedelta

class Checkout(models.Model):
    _name = "library.checkout"
    _description = "Checkout Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    stage_name = fields.Char()

    total_price_for_all_books = fields.Float(related='line_ids.total_price_for_all_books')

    @api.depends('close_date', 'line_ids', 'want_to_borrow_for_days', 'request_date')
    def _compute_total_discount(self):
        for record in self:
            if record.stage_id.state == "new":
                record.discount = 0

                for book in record.line_ids:
                    if record.request_date and record.want_to_borrow_for_days:
                        difference = record.want_to_borrow_for_days - record.request_date

                        if difference.days >= 365 and book.book_id.discount_per_year > 0:
                            div_year = difference.days // 365
                            diff_year = difference.days - (365 * div_year)
                            record.discount += div_year * book.book_id.discount_per_year

                            if diff_year >= 30:
                                div_month = diff_year // 30
                                diff_month = diff_year - (30 * div_month)
                                record.discount += div_month * book.book_id.discount_per_month

                                if diff_month >= 7:
                                    div_week = diff_month // 7
                                    record.discount += div_week * book.book_id.discount_per_week

                        elif difference.days >= 30:
                            # Calculate discount for months
                            div_month = difference.days // 30
                            diff_month = difference.days - (30 * div_month)
                            record.discount += div_month * book.book_id.discount_per_month

                            if diff_month >= 7:
                                # Calculate discount for weeks
                                div_week = diff_month // 7
                                record.discount += div_week * book.book_id.discount_per_week

                        elif difference.days >= 7:
                            # Calculate discount for weeks
                            div_week = difference.days // 7
                            record.discount += div_week * book.book_id.discount_per_week
                        else:
                            record.discount = 0
                    else:
                        record.discount = 0
            elif record.stage_id.state == "done":
                record.discount = 0

                for book in record.line_ids:
                    if record.request_date and record.close_date:
                        difference = record.close_date - record.request_date

                        if difference.days >= 365 and book.book_id.discount_per_year > 0:
                            div_year = difference.days // 365
                            diff_year = difference.days - (365 * div_year)
                            record.discount += div_year * book.book_id.discount_per_year

                            if diff_year >= 30:
                                div_month = diff_year // 30
                                diff_month = diff_year - (30 * div_month)
                                record.discount += div_month * book.book_id.discount_per_month

                                if diff_month >= 7:
                                    div_week = diff_month // 7
                                    record.discount += div_week * book.book_id.discount_per_week

                        elif difference.days >= 30:
                            # Calculate discount for months
                            div_month = difference.days // 30
                            diff_month = difference.days - (30 * div_month)
                            record.discount += div_month * book.book_id.discount_per_month

                            if diff_month >= 7:
                                # Calculate discount for weeks
                                div_week = diff_month // 7
                                record.discount += div_week * book.book_id.discount_per_week

                        elif difference.days >= 7:
                            # Calculate discount for weeks
                            div_week = difference.days // 7
                            record.discount += div_week * book.book_id.discount_per_week
                        else:
                            record.discount = 0
                    else:
                        record.discount = 0

            else:
                record.discount = 0


    @api.depends('discount', 'price', 'line_ids', 'want_to_borrow_for_days', 'request_date', 'close_date')
    def onchange_calculate_total_rent_before_discount(self):
        for record in self:
            total_days = 1
            if record.stage_id.state in ['new', 'open']:
                if record.request_date and record.want_to_borrow_for_days:
                    difference = record.want_to_borrow_for_days - record.request_date
                    if difference.days == 0:
                        total_days = 1
                    else:
                        total_days = difference.days
                else:
                    total_days = 1
                record.total_rent_before_discount = record.price * total_days
            elif record.stage_id.state in ['done','cancel']:
                if record.request_date:
                    difference = record.close_date - record.request_date
                    if difference.days == 0:
                        total_days = 1
                    else:
                        total_days = difference.days
                else:
                    total_days = 1
                record.total_rent_before_discount = record.price * total_days
            else:
                record.total_rent_before_discount = 0




    @api.depends('discount', 'price', 'line_ids', 'want_to_borrow_for_days', 'request_date', 'close_date')
    def onchange_price_adjusted_after_discount(self):
        for record in self:
            record.price_adjusted_after_discount = record.total_rent_before_discount - record.discount

    price_adjusted_after_discount = fields.Float(string='Total after Discount', compute='onchange_price_adjusted_after_discount')
    total_rent_before_discount = fields.Float(string='Total Rent Before Discount', default=0, compute='onchange_calculate_total_rent_before_discount')
    want_to_borrow_for_days = fields.Date(string='Expected Returned Date', default=fields.datetime.today())
    discount = fields.Float(string='Discount', compute='_compute_total_discount', default=0, store=True, readonly= True)
    adjusted_price = fields.Float(string='Adjusted Price', compute='_compute_total_discount')
    total_temp_for_price = fields.Float(default=0)
    book_checkout_id = fields.Many2one(comodel_name='library.book')
    price_related = fields.Float(related='book_checkout_id.price', string='Rent/Day')

    @api.depends('line_ids', 'num_books', 'days_borrowed', 'close_date')
    def _compute_total_rent(self):
        for checkout in self:
            if checkout.state in ['new', 'open']:
                for book in checkout.line_ids:
                    checkout.total_temp_for_price += book.book_id.price * book.borrowed_count
                checkout.price = checkout.total_temp_for_price * checkout.days_borrowed
            else:
                checkout.price = checkout.price * checkout.days_borrowed

    price = fields.Float(compute='_compute_total_rent', string='Total Rent', store=True)

    @api.depends('close_date', 'request_date')
    def _compute_days_borrowed(self):
        for record in self:
            if record.request_date and record.close_date:
                difference = record.close_date - record.request_date
                if difference.days == 0:
                    record.days_borrowed = 1
                else:
                    record.days_borrowed = difference.days
            else:
                record.days_borrowed = 1

    days_borrowed = fields.Integer(compute='_compute_days_borrowed', string='Days Borrowed', store=True)

    active = fields.Boolean(string='Active', default=True)
    member_id = fields.Many2one("library.member", required=True)

    @api.depends('member_id')
    def _compute_request_date_onchange(self):
        today_date = fields.Date.today()
        if self.request_date != today_date:
            self.request_date = today_date
            return {
                "warning": {
                    "title": "Changed Request Date",
                    "message": "Request date changed to today!",
                }
            }

    @api.model
    def _default_stage(self):
        Stage = self.env["library.checkout.stage"]
        return Stage.search([("state", "=", "new")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string="Title")

    member_image = fields.Binary(related="member_id.image_128")

    user_id = fields.Many2one("res.users", "Librarian", default=lambda s: s.env.user.id)

    line_ids = fields.One2many(
        "library.checkout.line",
        "checkout_id",
        string="Borrowed Books",
    )

    request_date = fields.Date(
        default=lambda s: fields.Date.today(),
        compute="_compute_request_date_onchange",
        store=True,
        readonly=False,
    )

    stage_id = fields.Many2one(
        "library.checkout.stage",
        default=_default_stage,
        copy=False,
        group_expand="_group_expand_stage_id")

    state = fields.Selection(related="stage_id.state", store=True)

    kanban_state = fields.Selection(
        [("normal", "In Progress"),
         ("blocked", "Blocked"),
         ("done", "Ready for next stage")],
        "Kanban State",
        default="normal")

    color = fields.Integer()

    priority = fields.Selection(
        [("0", "High"),
         ("1", "Very High"),
         ("2", "Critical")],
        default="0")

    checkout_date = fields.Date(readonly=True)

    close_date = fields.Date(readonly=True)

    def action_buy_credits(self):
        checkout_action = self.env.ref('library_checkout.action_library_checkout_invoices')
        checkout_action['domain'] = [('member_id', '=', self.member_id.id)]
        return checkout_action.read()[0]


    def _compute_count_checkouts(self):
        for checkout in self:
            domain = [
                ("member_id", "=", checkout.member_id.id),
                ("state", "not in", ["done", "cancel"]),
            ]
            checkout.count_checkouts = self.search_count(domain)

    def _compute_count_checkouts_DISABLED(self):
        members = self.mapped("member_id")
        domain = [
            ("member_id", "in", members.ids),
            ("state", "not in", ["done", "cancel"]),
        ]
        raw = self.read_group(domain, ["id:count"], ["member_id"])
        data = {x["member_id"][0]: x["member_id_count"] for x in raw}
        for checkout in self:
            checkout.count_checkouts = data.get(checkout.member_id.id, 0)

    count_checkouts = fields.Integer(compute="_compute_count_checkouts")

    num_books = fields.Integer(compute="_compute_num_books", store=True, string='Total Books')
    total_borrowed_books = fields.Integer(compute="_compute_total_borrowed_books", store=True, string='Total Books')

    @api.depends('line_ids')
    def _compute_total_borrowed_books(self):
        for checkout in self:
            for book in checkout.line_ids:
                checkout.total_borrowed_books += book.borrowed_count

    @api.depends("line_ids")
    def _compute_num_books(self):
        for book in self:
            book.num_books = len(book.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        new_records = super().create(vals_list)
        for new_record in new_records:
            new_record['name'] = self.env['ir.sequence'].next_by_code('library.checkout')
            if new_record.stage_id.state in ("open", "done"):
                raise exceptions.UserError(
                    "State not allowed for new checkouts."
                )
        return new_records
    def write(self, vals):


        if "stage_id" in vals and "kanban_state" not in vals:
            vals["kanban_state"] = "normal"
        old_state = self.stage_id.state
        old_stage_name = self.stage_id.name

        super().write(vals)
        new_state = self.stage_id.state
        new_stage_name = self.stage_id.name
        if old_state == 'done' and new_state in ['open', 'new', 'cancel']:
            raise exceptions.ValidationError("Cant go back from 'Returned' state")
        if old_state == 'open' and new_state in ['new']:
            raise exceptions.ValidationError("Cant go to 'Requested' state from 'Borrowed' state")
        if old_stage_name == 'Paid' and new_stage_name == 'Returned/Due':
            raise exceptions.UserError("Cant go from %s state to %s state"% (old_stage_name,new_stage_name))
        if not self.env.context.get("_checkout_write"):
            if new_state != old_state and new_state == "open":
                self.with_context(_checkout_write=True).write(
                    {"checkout_date": fields.Date.today()})
            if new_state != old_state and new_state == "done":
                self.with_context(_checkout_write=True).write(
                    {"close_date": fields.Date.today()})

        if self.stage_id.stage_number == 3:
            if self.stage_id.state in ['done', 'cancel']:
                for book in self.line_ids:
                    if book.borrowed_count == 1:
                        book.book_id.available_count += 1
                    else:
                        book.book_id.available_count += (book.borrowed_count/2)

        if new_stage_name == 'Paid':
            pass


        return True

    def button_done(self):
        Stage = self.env["library.checkout.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        if not done_stage:
            raise exceptions.UserError("Done stage not found. Please configure the stages.")

        return True


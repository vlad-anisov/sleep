from odoo import models, fields


class Article(models.Model):
    _name = "article"

    name = fields.Char(string="Name")
    text = fields.Html(string="Text")
    user_ids = fields.Many2many("res.users", string="Users")
    is_available = fields.Boolean(string="Is available", compute="_compute_is_available")

    def _compute_is_available(self):
        for record in self:
            record.is_available = self.env.user in record.user_ids

from odoo import models, fields


class Article(models.Model):
    _name = "article"

    name = fields.Char(string="Name", translate=True)
    text = fields.Html(string="Text", translate=True)
    user_ids = fields.Many2many("res.users", string="Users")
    is_available = fields.Boolean(string="Is available", compute="_compute_is_available")

    def _compute_is_available(self):
        for record in self:
            record.is_available = self.env.user in record.user_ids

    def read(self, fields=None, load='_classic_read'):
        step_id = self.env.user.script_id.step_ids.filtered(lambda s: s.type == "article" and s.state == "waiting")[:1]
        step_id.type = "nothing"
        step_id.run()
        return super().read(fields=fields, load=load)

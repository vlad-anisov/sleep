from odoo import models, fields, api


class Ritual(models.Model):
    _name = "ritual"

    name = fields.Char(string="Name", default="Ritual")
    line_ids = fields.One2many("ritual.line", "ritual_id", string="Lines")
    line_name = fields.Char(string="Line name")
    user_id = fields.Many2one("res.users", string="User", required=True)
    is_edit = fields.Boolean(string="Is edit")

    @api.model
    def open(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Ritual",
            "res_model": "ritual",
            "view_mode": "form",
            "res_id": self.env.user.ritual_id.id,
        }

    def add_line(self):
        self.ensure_one()
        if self.line_name:
            self.env["ritual.line"].create({
                "ritual_id": self.id,
                "name": self.line_name,
            })
            self.line_name = ""

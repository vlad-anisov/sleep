from odoo import models, fields, api


class Ritual(models.Model):
    _name = "ritual"

    name = fields.Char(string="Name", default="Ritual")
    line_ids = fields.Many2many("ritual.line", string="Lines")
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

    @api.onchange("line_ids")
    def _onchange_line_ids(self):
        self.env["ritual.line"].browse(list(set(self._origin.line_ids.ids) - set(self.line_ids.ids))).unlink()

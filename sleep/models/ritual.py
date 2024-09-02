from odoo import models, fields, api


class Ritual(models.Model):
    _name = "ritual"

    name = fields.Char(string="Name", default="Ritual", translate=True)
    line_ids = fields.Many2many("ritual.line", string="Lines")
    user_id = fields.Many2one("res.users", string="User", required=True)
    is_check = fields.Boolean(string="Check", compute="_compute_is_check", store=True)

    @api.depends("line_ids.is_check")
    def _compute_is_check(self):
        for record in self:
            if all(record.line_ids.mapped("is_check")):
                record.is_check = True
                step_id = self.env.user.script_id.step_ids.filtered(lambda s: s.type == "ritual" and s.state == "waiting")[:1]
                if step_id:
                    step_id.type = "nothing"
                    step_id.run()
            else:
                record.is_check = False


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

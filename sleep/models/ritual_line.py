from odoo import models, fields, _, api


class RitualLine(models.Model):
    _name = "ritual.line"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence")
    is_check = fields.Boolean(string="Check")
    is_base = fields.Boolean(string="Base")

    def unlink(self):
        self.is_check = False
        return super(RitualLine, self.filtered(lambda line: not line.is_base)).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        record_ids.add_to_ritual()
        return record_ids


    def add_line(self):
        line_ids = self.env["ritual.line"].search([("id", "not in", self.env.user.ritual_id.line_ids.ids)])
        if line_ids:
            return {
                "type": "ir.actions.act_window",
                "name": "Add line",
                "res_model": "ritual.line",
                "view_mode": "tree",
                "target": "new",
                "domain": [("id", "in", line_ids.ids)],
            }
        return self.create_custom_line()

    # @api.model
    def create_custom_line(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Create custom line"),
            "res_model": "ritual.line",
            "view_mode": "form",
            "target": "new",
        }

    def add_to_ritual(self):
        self.env.user.ritual_id.line_ids += self

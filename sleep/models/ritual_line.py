from odoo import models, fields, _


class RitualLine(models.Model):
    _name = "ritual.line"

    name = fields.Char(
        string="Name",
    )
    ritual_id = fields.Many2one(
        comodel_name="ritual",
        string="Ritual",
    )
    sequence = fields.Integer(
        string="Sequence"
    )
    is_done = fields.Boolean(
        string="Is done",
    )

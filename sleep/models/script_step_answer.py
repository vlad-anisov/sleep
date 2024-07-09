from odoo import models, fields


class ScriptStepAnswer(models.Model):
    _name = "script.step.answer"

    name = fields.Char(string="Name")
    step_id = fields.Many2one("script.step", string="Step")
    sequence = fields.Integer(string="Sequence")

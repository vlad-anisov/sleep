from odoo import models, fields


class Script(models.Model):
    _name = "script"

    name = fields.Char(string="Name")
    step_ids = fields.One2many("script.step", "script_id", string="Steps")

    def run(self):
        for step_id in self.step_ids.sorted(key=lambda s: (s.sequence, s.id)):
            step_id.run()


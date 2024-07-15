from odoo import models, fields


class Script(models.Model):
    _name = "script"

    name = fields.Char(string="Name")
    step_ids = fields.One2many("script.step", "script_id", string="Steps")

    def run(self):
        self.step_ids.is_running = False
        self.step_ids.sorted(key=lambda s: (s.sequence, s.id))[:1].run()

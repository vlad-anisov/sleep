from odoo import models, fields, api

STATE_TYPES = [
    ("pending", "Pending"),
    ("started", "Started"),
    ("wait_dependencies", "Wait Dependencies"),
    ("done", "Done"),
    ("failed", "Failed"),
]


class Script(models.Model):
    _name = "script"

    name = fields.Char(string="Name")
    step_ids = fields.One2many("script.step", "script_id", string="Steps")
    state = fields.Selection(STATE_TYPES, string="State", required=True, default="pending")
    data = fields.Json(string="Data")

    def run(self):
        self.env.user.script_id = self
        self.step_ids.is_running = False
        self.step_ids.sorted(key=lambda s: (s.sequence, s.id))[:1].run()

    @api.depends()
    def _compute_state(self):
        for record in self:
            fi

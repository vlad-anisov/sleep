from odoo import models, fields

STATE_TYPES = [
    ("not_running", "Not running"),
    ("running", "Running"),
    ("done", "Done"),
    ("failed", "Failed"),
]


class Script(models.Model):
    _name = "script"

    name = fields.Char(string="Name")
    step_ids = fields.One2many("script.step", "script_id", string="Steps")
    state = fields.Selection(STATE_TYPES, string="State", compute="_compute_state")
    data = fields.Json(string="Data")
    user_id = fields.Many2one("res.users", string="User")

    def run(self):
        self.step_ids.state = "not_running"
        self.step_ids.sorted(key=lambda s: (s.sequence, s.id))[:1].run()

    def _compute_state(self):
        for record in self:
            if record.step_ids.filtered(lambda s: s.state == "failed"):
                record.state = "failed"
            elif record.step_ids.filtered(lambda s: s.state in ("running", "waiting")):
                record.state = "running"
            elif record.step_ids.filtered(lambda s: s.state == "done"):
                record.state = "done"
            else:
                record.state = "not_running"

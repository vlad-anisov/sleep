from odoo import models, fields, api
from odoo.exceptions import UserError

STATE_TYPES = [
    ("not_running", "Not running"),
    ("running", "Running"),
    ("done", "Done"),
    ("failed", "Failed"),
]


class Script(models.Model):
    _name = "script"

    name = fields.Char(string="Name", required=True)
    step_ids = fields.One2many("script.step", "script_id", string="Steps")
    state = fields.Selection(STATE_TYPES, string="State", compute="_compute_state")
    data = fields.Json(string="Data")
    user_id = fields.Many2one("res.users", string="User")
    next_script_id = fields.Many2one("script", string="Next script")
    is_main = fields.Boolean(string="Is main")
    main_script_id = fields.Many2one("script", string="Main script")

    ritual_line_id = fields.Many2one("ritual.line", string="Ritual line", domain=[("is_base", "=", True)])
    article_id = fields.Many2one("article", string="Article")

    @api.constrains("is_main", "main_script_id", "user_id", "next_script_id")
    def _check_script(self):
        for record in self:
            if record.is_main and not record.main_script_id:
                continue
            elif not record.is_main and record.main_script_id and record.user_id and record.next_script_id.is_main:
                continue
            else:
                raise UserError("Invalid script")

    def run(self):
        self.ensure_one()
        user_id = self.user_id

        if self.is_main:
            main_script_id = self
            self.user_id = False
        else:
            main_script_id = self.sudo().main_script_id
            self.unlink()

        if user_id:
            script_id = main_script_id.create_script(user_id)
            user_id.script_id.unlink()
            user_id.script_id = script_id
            script_id.with_user(user_id).step_ids.sorted(key=lambda s: (s.sequence, s.id))[:1].run()

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

    def unlink(self):
        return super(Script, self.filtered(lambda s: not s.is_main)).unlink()

    def create_script(self, user_id):
        if not self.is_main:
            raise UserError("Cannot create script from a subscript")

        script_id = self.copy({
            "name": self.name + f" ({user_id.name})",
            "is_main": False,
            "user_id": user_id.id,
            "main_script_id": self.id,
        })

        previous_step_id = False
        for step_id in self.step_ids.sorted(key=lambda s: (s.sequence, s.id)):
            new_step_id = step_id.copy({
                "script_id": script_id.id,
                "next_step_ids": False,
            })
            if previous_step_id:
                previous_step_id.next_step_ids = [(4, new_step_id.id)]
            previous_step_id = new_step_id
        return script_id

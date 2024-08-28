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
            elif not record.is_main and record.main_script_id and record.user_id:
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
            main_script_id = self.next_script_id or self.main_script_id
            self.unlink()

        if user_id:
            script_id = main_script_id.create_script(user_id)
            if user_id.script_id:
                user_id.script_id.unlink()
            user_id.script_id = script_id
            user_id.with_user(user_id).sudo().ritual_id.line_ids.is_check = False
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
            "next_script_id": False,
        })
        return script_id

    def copy(self, default=None):
        record_id = super().copy(default)

        def create_next_step_ids(step_id, script_id):
            next_step_ids = self.env["script.step"]
            for next_step_id in step_id.next_step_ids:
                next_step_ids += create_next_step_ids(next_step_id, script_id)
            return step_id.copy({
                "script_id": script_id.id,
                "next_step_ids": next_step_ids.ids,
            })

        create_next_step_ids(self.step_ids.sorted(key=lambda s: (s.sequence, s.id))[:1], record_id)

        return record_id

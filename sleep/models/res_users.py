from odoo import models, fields, api
from odoo.tools import format_duration
from datetime import timedelta


class ResUsers(models.Model):
    _inherit = "res.users"

    script_id = fields.Many2one("script", string="Script")
    sleepy_chat_id = fields.Many2one("discuss.channel", string="Sleepy Chat", required=True)
    ritual_id = fields.Many2one("ritual", string="Ritual", required=True)
    time = fields.Float(string="Time")
    action_id = fields.Many2one(default=lambda self: self.env.ref("sleep.page_sleepy_chat_action"))
    test_script_count = fields.Integer(string="Test Script Count", default=0)

    @api.constrains("time")
    def _constrains_time(self):
        for record in self.filtered(lambda u: u.time):
            self.env["ir.cron"].search([("name", "=", "Daily script"), ("user_id", "=", self.env.user.id)]).unlink()
            time = format_duration(record.time)
            self.env["ir.cron"].create({
                "name": "Daily script",
                "interval_number": 1,
                "interval_type": "days",
                "model_id": self.env.ref("sleep.model_script").id,
                "state": "code",
                "code": "env.user.script_id.run()",
                "user_id": self.env.user.id,
                "nextcall": (fields.Datetime.now() + timedelta(hours=1)).strftime(f"%Y-%m-%d {time}:00"),
                "doall": True,
                "numbercall": -1,
                "active": True,
            })
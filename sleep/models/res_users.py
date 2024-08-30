from odoo import models, fields, api
from odoo.tools import format_duration
from datetime import timedelta
import pytz


class ResUsers(models.Model):
    _inherit = "res.users"

    script_id = fields.Many2one("script", string="Script")
    sleepy_chat_id = fields.Many2one("discuss.channel", string="Sleepy Chat", required=True)
    ritual_id = fields.Many2one("ritual", string="Ritual", required=True)
    time = fields.Float(string="Time", default=23, required=True)
    action_id = fields.Many2one(default=lambda self: self.env.ref("sleep.page_sleepy_chat_action"))
    test_script_count = fields.Integer(string="Test Script Count", default=0)

    @api.constrains("time")
    def _constrains_time(self):
        for record in self:
            self.env["ir.cron"].search([("name", "=", "Daily script"), ("user_id", "=", record.id)]).unlink()
            hour, minute = format_duration(record.time).split(":")
            tz = pytz.timezone(record.tz) if record.tz else pytz.utc
            nextcall_datetime = fields.Datetime.now().astimezone(tz).replace(hour=int(hour), minute=int(minute), second=0).astimezone(pytz.utc)
            nextcall_datetime = nextcall_datetime.astimezone(pytz.utc)
            if nextcall_datetime < fields.Datetime.now().replace(tzinfo=pytz.utc):
                nextcall_datetime = nextcall_datetime + timedelta(days=1)
            nextcall_datetime = nextcall_datetime.strftime(f"%Y-%m-%d %H:%M:%S")
            self.env["ir.cron"].create({
                "name": "Daily script",
                "interval_number": 1,
                "interval_type": "days",
                "model_id": self.env.ref("sleep.model_script").id,
                "state": "code",
                "code": "env.user.script_id.run()",
                "user_id": record.id,
                "nextcall": nextcall_datetime,
                "doall": True,
                "numbercall": -1,
                "active": True,
            })
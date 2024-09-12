from odoo import models, fields, api
from datetime import timedelta
import pytz


class ResUsers(models.Model):
    _inherit = "res.users"

    script_id = fields.Many2one("script", string="Script")
    chat_id = fields.Many2one("discuss.channel", string="Chat", required=True)
    ritual_id = fields.Many2one("ritual", string="Ritual", required=True)
    time = fields.Char(string="Time", default="23:00", required=True)
    action_id = fields.Many2one(default=lambda self: self.env.ref("sleep.chat_action"))
    test_script_count = fields.Integer(string="Test Script Count", default=0)

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        eva_id = self.env.ref("sleep.eva")
        for record_id in record_ids:
            record_id.ritual_id = self.sudo().env["ritual"].create({
                "user_id": record_id.id,
            })
            partner_ids = self.env["res.partner"].browse([eva_id.partner_id.id, record_id.partner_id.id])
            record_id.chat_id = self.with_user(record_id).env["discuss.channel"].create({
                "channel_member_ids": [
                    (0, 0, {"partner_id": partner_id.id}) for partner_id in partner_ids
                ],
                "channel_type": "chat",
                "name": ", ".join(partner_ids.mapped("name")),
            })
            self.env["script"].browse(1).with_user(record_id).run()
        return record_ids

    @api.constrains("time")
    def _constrains_time(self):
        for record in self:
            self.env["ir.cron"].search([("name", "=", "Daily script"), ("user_id", "=", record.id)]).unlink()
            hour, minute = record.time.split(":")
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
from odoo import models, fields, api
from datetime import timedelta
import pytz


class ResUsers(models.Model):
    _inherit = "res.users"

    name = fields.Char(translate=True)
    script_id = fields.Many2one("script", string="Script")
    chat_id = fields.Many2one("discuss.channel", string="Chat", required=True, ondelete="cascade")
    ritual_id = fields.Many2one("ritual", string="Ritual", required=True, ondelete="cascade")
    time = fields.Char(string="Time", default="23:00", required=True)
    # action_id = fields.Many2one(default=lambda self: self.env["ir.actions.actions"]._for_xml_id("sleep.chat_action")["id"])
    not_active_days = fields.Integer(string="Not active days")

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        eva_id = self.env.ref("sleep.eva")
        for record_id in record_ids:
            record_id.write({
                "action_id": self.env["ir.actions.actions"]._for_xml_id("sleep.chat_action")["id"],
                "lang": "ru_RU",
            })
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

    def ggg(self):
        eva_id = self.env.ref("sleep.eva")
        for record_id in self.env.user:
            # record_id.ritual_id = self.sudo().env["ritual"].create({
            #     "user_id": record_id.id,
            # })
            partner_ids = self.env["res.partner"].browse([eva_id.partner_id.id, record_id.partner_id.id])
            record_id.chat_id = self.with_user(record_id).env["discuss.channel"].create({
                "channel_member_ids": [
                    (0, 0, {"partner_id": partner_id.id}) for partner_id in partner_ids
                ],
                "channel_type": "chat",
                "name": ", ".join(partner_ids.mapped("name")),
            })
            # self.env["script"].browse(1).with_user(record_id).run()

    @api.constrains("time")
    def _constrains_time(self):
        for record in self:
            self.env["ir.cron"].search([("name", "like", "daily script"), ("user_id", "=", record.id)]).unlink()
            hour, minute = record.time.split(":")
            tz = pytz.timezone(record.tz) if record.tz else pytz.utc
            nextcall_datetime = fields.Datetime.now().astimezone(tz).replace(hour=int(hour), minute=int(minute), second=0).astimezone(pytz.utc)
            nextcall_datetime = nextcall_datetime.astimezone(pytz.utc)
            if nextcall_datetime < fields.Datetime.now().replace(tzinfo=pytz.utc):
                nextcall_datetime = nextcall_datetime + timedelta(days=1)
            nextcall_datetime = nextcall_datetime.strftime(f"%Y-%m-%d %H:%M:%S")
            self.env["ir.cron"].create({
                "name": f"{record.name} daily script",
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
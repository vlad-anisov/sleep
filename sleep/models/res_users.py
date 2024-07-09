from odoo import models
import time


class ResUsers(models.Model):
    _inherit = "res.users"

    def start_first_communication(self):
        sleepy_id = self.env.ref("sleep.sleepy")
        partner_ids = self.env.user.partner_id + sleepy_id.partner_id
        channel_id = self.env["discuss.channel"].search(
            [("channel_partner_ids", "=", partner_ids.ids)], order="id desc", limit=1)
        channel_id = channel_id.browse(3).with_user(sleepy_id)
        member_id = self.env["discuss.channel.member"].search([("channel_id", "=", channel_id.id), ("partner_id", "=", sleepy_id.partner_id.id)]).with_user(sleepy_id)
        member_id._notify_typing(True)
        self.send_first_message(channel_id, member_id)

    def send_first_message(self, channel_id, member_id):
        channel_id.message_post(body='''Hello World <button type="button" onclick="alert('Hello world!')">Click Me!</button>''', subject="Test", message_type="comment", subtype_xmlid="mail.mt_comment", body_is_html=True)
        member_id._notify_typing(False)


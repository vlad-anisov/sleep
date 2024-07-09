from odoo import models, fields

STEP_TYPES = [
    ("send_message", "Send message"),
    ("wait_answer", "Wait answer"),
]


class ScriptStep(models.Model):
    _name = "script.step"

    name = fields.Char(string="Name")
    script_id = fields.Many2one("script", string="Script")
    sequence = fields.Integer(string="Sequence")
    type = fields.Selection(STEP_TYPES, string="Type", required=True)
    message = fields.Html(string="Message")
    answer_ids = fields.One2many("script.step.answer", "step_id", string="Answers")

    def get_channel(self):
        sleepy_id = self.env.ref("sleep.sleepy")
        partner_ids = self.env.user.partner_id + sleepy_id.partner_id
        channel_id = self.env["discuss.channel"].search(
            [("channel_partner_ids", "=", partner_ids.ids)], order="id desc", limit=1)
        channel_id = channel_id.browse(3).with_user(sleepy_id)
        return channel_id

    def send_message(self):
        channel_id = self.get_channel()
        channel_id.message_post(
            body=self.message, message_type="comment", subtype_xmlid="mail.mt_comment", body_is_html=True
        )

    def run(self):
        if self.type == "send_message":
            self.send_message()
        elif self.type == "wait_answer":
            pass

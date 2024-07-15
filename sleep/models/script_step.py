from odoo import models, fields, _

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
    is_running = fields.Boolean(string="Running")
    next_step_id = fields.Many2one("script.step", string="Next step", compute="_compute_next_step")

    def _compute_next_step(self):
        for record in self:
            step_ids = record.script_id.step_ids.sorted(key=lambda s: (s.sequence, s.id))
            record.next_step_id = step_ids.filtered(lambda s: (s.sequence, s.id) > (record.sequence, record.id))[:1]

    def get_channel(self):
        sleepy_id = self.env.ref("sleep.sleepy")
        partner_ids = self.env.user.partner_id + sleepy_id.partner_id
        channel_id = self.env["discuss.channel"].search(
            [("channel_partner_ids", "=", partner_ids.ids)], order="id desc", limit=1)
        channel_id = channel_id.browse(3).with_user(sleepy_id)
        return channel_id

    def send_message(self, message):
        channel_id = self.get_channel()
        channel_id.message_post(
            body=message, message_type="comment", subtype_xmlid="mail.mt_comment", body_is_html=True
        )

    def run(self, **kwargs):
        if not self:
            return
        self.ensure_one()
        self.is_running = True
        if self.type == "send_message":
            self.send_message(self.message)
        elif self.type == "wait_answer":
            answer = kwargs.get("answer")
            if answer and answer in self.answer_ids.mapped("name"):
                pass
            elif answer and answer not in self.answer_ids.mapped("name"):
                self.send_message(_("Unknown answer"))
                return
            elif not answer:
                return
        self.is_running = False
        self.next_step_id.run()

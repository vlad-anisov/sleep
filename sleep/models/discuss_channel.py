from odoo import models, api


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _notify_thread_by_web_push(self, message, recipients_data, msg_vals=False, **kwargs):
        if not self.env.context.get("skip_notify_thread_by_web_push"):
            return super()._notify_thread_by_web_push(message, recipients_data, msg_vals=msg_vals, **kwargs)

    def message_post(self, **kwargs):
        result = super().message_post(**kwargs)
        if self == self.env.user.sleepy_chat_id:
            step_id = self.env.user.script_id.step_ids.filtered(lambda s: s.state == "waiting")[:1]
            if step_id:
                step_id.user_answer = kwargs.get("body")
                step_id.run()
        return result

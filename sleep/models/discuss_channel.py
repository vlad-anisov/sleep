from odoo import models, fields, api


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def message_post(self, **kwargs):
        result = super().message_post(**kwargs)
        step_id = self.env.user.script_id.step_ids.filtered(lambda s: s.is_running and s.type == "process_answer")[:1]
        if step_id:
            step_id.run(user_answer=kwargs.get("body"))
        return result

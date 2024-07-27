from odoo import models


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def message_post(self, **kwargs):
        result = super().message_post(**kwargs)
        script_ids = self.env.user.script_ids.filtered(lambda s: s.state == "running")
        step_id = script_ids.step_ids.filtered(lambda s: s.state == "waiting")[:1]
        if step_id:
            step_id.user_answer = kwargs.get("body")
            step_id.run()
        return result

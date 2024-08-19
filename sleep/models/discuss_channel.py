from odoo import models, api


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _notify_thread_by_web_push(self, message, recipients_data, msg_vals=False, **kwargs):
        if not self.env.context.get("skip_notify_thread_by_web_push"):
            return super()._notify_thread_by_web_push(message, recipients_data, msg_vals=msg_vals, **kwargs)

    def message_post(self, **kwargs):
        result = super().message_post(**kwargs)
        step_id = self.env.user.script_id.step_ids.filtered(lambda s: s.state == "waiting")[:1]
        if step_id:
            step_id.user_answer = kwargs.get("body")
            step_id.run()
        return result

    # @api.model
    # def open_sleepy_chat(self):
    #     self = self.browse(9)
    #     domain = [('partner_id', '=', self.env.user.partner_id.id), ('channel_id', 'in', self.ids)]
    #     for session_state in self.env['discuss.channel.member'].search(domain):
    #         self.env['bus.bus']._sendone(self.env.user.partner_id, 'discuss.Thread/open', {
    #             'foldStateCount': 0,
    #             'id': session_state.channel_id.id,
    #             'model': 'discuss.channel',
    #             'fold_state': "open",
    #         })
    #
    # def close_sleepy_chat(self):
    #     self = self.browse(9)
    #     domain = [('partner_id', '=', self.env.user.partner_id.id), ('channel_id', 'in', self.ids)]
    #     for session_state in self.env['discuss.channel.member'].search(domain):
    #         self.env['bus.bus']._sendone(self.env.user.partner_id, 'discuss.Thread/closed', {
    #             'foldStateCount': 0,
    #             'id': session_state.channel_id.id,
    #             'model': 'discuss.channel',
    #             'fold_state': "closed",
    #         })

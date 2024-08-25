from odoo import http
from odoo.http import request
from odoo.addons.mail.controllers.discuss.channel import ChannelController
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context


class ChannelControllerInherit(ChannelController):

    @http.route("/discuss/channel/notify_typing", methods=["POST"], type="json", auth="public")
    @add_guest_to_context
    def discuss_channel_notify_typing(self, channel_id, is_typing, is_sleepy=False):
        if is_sleepy:
            sleepy_id = request.env.ref("sleep.sleepy")
            request.update_env(user=sleepy_id)
        return super().discuss_channel_notify_typing(channel_id, is_typing)

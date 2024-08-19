from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super().session_info()
        result["sleepy_chat_id"] = self.env.user.sleepy_chat_id.id
        return result

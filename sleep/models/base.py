from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def read(self, fields=None, load="_classic_read"):
        self.env["discuss.channel"].close_sleepy_chat()
        return super().read(fields, load)
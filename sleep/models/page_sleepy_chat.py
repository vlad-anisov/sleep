from odoo import models, fields


class PageSleepyChat(models.Model):
    _name = "page.sleepy.chat"

    name = fields.Char(string="Name", default="Sleepy chat")

    def read(self, fields=None, load="_classic_read"):
        result = super().read(fields, load)
        self.env["discuss.channel"].open_sleepy_chat()
        return result

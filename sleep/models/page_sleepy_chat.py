from odoo import models, fields


class PageSleepyChat(models.Model):
    _name = "page.sleepy.chat"

    name = fields.Char(string="Name", default="Sleepy chat")

    def read(self, fields=None, load="_classic_read"):
        self.env["discuss.channel"].open_sleepy_chat()
        return super().read(fields, load)

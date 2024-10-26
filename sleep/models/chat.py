from odoo import models, fields


class Chat(models.Model):
    _name = "chat"

    name = fields.Char(string="Name", default="Chat")

    def read(self, fields=None, load='_classic_read'):
        step_id = self.env.user.script_id.step_ids.filtered(lambda s: s.type in ("article", "ritual") and s.state == "waiting" and s.user_answer)[:1]
        if step_id:
            step_id.type = "nothing"
            step_id.run()
        return super().read(fields=fields, load=load)
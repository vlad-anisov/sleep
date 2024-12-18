from odoo import models, fields


class Article(models.Model):
    _name = "article"

    name = fields.Char(string="Name", translate=True)
    text = fields.Html(string="Text", translate=True)
    user_ids = fields.Many2many("res.users", string="Users")
    is_available = fields.Boolean(string="Is available", compute="_compute_is_available")
    image = fields.Image(string="Image")
    short_name = fields.Char(string="Short name")
    emoji = fields.Char(string="Emoji")
    color = fields.Char(string="Color")
    first_color = fields.Char(string="First color")
    second_color = fields.Char(string="Second color", compute="_compute_second_color")
    description = fields.Char(string="Description")

    def _compute_is_available(self):
        for record in self:
            record.is_available = self.env.user in record.user_ids

    def _compute_second_color(self):
        for record in self:
            if record.first_color:
                colors = [int(x) for x in record.first_color.split(",")]
                record.second_color = ",".join([str(x/3) for x in colors])
            else:
                record.second_color = "0,0,0,0"

    def read(self, fields=None, load='_classic_read'):
        step_id = self.env.user.script_id.step_ids.filtered(lambda s: s.type == "article" and s.state == "waiting")[:1]
        if step_id:
            step_id.user_answer = "ready"
            step_id.message_id.body = step_id.message
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'discuss.channel/fetch', {'id': self.env.user.chat_id.id})
        return super().read(fields=fields, load=load)

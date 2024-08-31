from odoo import models, fields, api, _
from odoo.http import request
from odoo.addons.base.models.res_partner import _lang_get, _tz_get

COLOR_SCHEME_TYPES = [
    ("light", _("Light")),
    ("dark", _("Dark")),
]


class Settings(models.Model):
    _name = "settings"

    name = fields.Char(default="Settings")
    color_scheme = fields.Selection(COLOR_SCHEME_TYPES, string="Theme", compute="_compute_settings", readonly=False, required=True)
    lang = fields.Selection(_lang_get, string="Language", compute="_compute_settings", readonly=False, required=True)
    tz = fields.Selection(_tz_get, string="Timezone", compute="_compute_settings", readonly=False, required=True)
    time = fields.Char(string="Time", compute="_compute_settings", readonly=False, required=True)

    @api.onchange("color_scheme", "lang", "tz", "time")
    def _onchange_settings(self):
        request.future_response.set_cookie("color_scheme", self.color_scheme)
        if self.lang:
            self.env.user.lang = self.lang
        if self.tz:
            self.env.user.tz = self.tz
        if self.time:
            self.env.user.time = self.time
        return {
            "action": {
                "type": "ir.actions.client",
                "tag": "reload"
            }
        }

    def _compute_settings(self):
        for record in self:
            record.color_scheme = request.httprequest.cookies.get("color_scheme", "light")
            record.lang = self.env.user.lang
            record.tz = self.env.user.tz
            record.time = self.env.user.time

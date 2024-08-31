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
    lang = fields.Selection(_lang_get, string="Language", compute="_compute_lang", readonly=False, required=True)
    color_scheme = fields.Selection(COLOR_SCHEME_TYPES, string="Theme", compute="_compute_color_scheme", readonly=False, required=True)
    tz = fields.Selection(_tz_get, string="Timezone", compute="_compute_tz", readonly=False, required=True)
    time = fields.Float(string="Time", compute="_compute_time", readonly=False, required=True)

    @api.onchange("color_scheme", "lang", "tz")
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

    def _compute_lang(self):
        for record in self:
            record.lang = self.env.user.lang

    def _compute_color_scheme(self):
        for record in self:
            record.color_scheme = request.httprequest.cookies.get("color_scheme", "light")

    def _compute_tz(self):
        for record in self:
            record.tz = self.env.user.tz

    def _compute_time(self):
        for record in self:
            record.time = self.env.user.time

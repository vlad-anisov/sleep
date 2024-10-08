from odoo import models, fields, api

MOOD_TYPES = [
    ("👍", "👍"),
    ("👌", "👌"),
    ("👎", "👎"),
]


class Statistic(models.Model):
    _name = "statistic"

    mood = fields.Selection(MOOD_TYPES, required=True)
    date = fields.Datetime(required=True)
    count = fields.Integer(compute="_compute_count", store=True)
    date_string = fields.Char(compute="_compute_date_string", store=True)

    @api.depends("mood")
    def _compute_count(self):
        mood_to_count = {
            "👍": 1,
            "👌": 0,
            "👎": -1,
        }
        for record in self:
            record.count = mood_to_count[record.mood]

    @api.depends("date")
    def _compute_date_string(self):
        for record in self:
            record.date_string = record.date.strftime("%d/%m/%Y %H:%M")


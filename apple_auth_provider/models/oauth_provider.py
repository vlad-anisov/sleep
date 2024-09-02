# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import base64
import jwt
import logging
import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AuthOauthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    apple_team_id = fields.Char("Apple Team ID")
    apple_key_id = fields.Char("Apple Key ID")
    apple_key_file = fields.Binary("Apple Key File")
    apple_provider = fields.Boolean()

    @api.onchange('data_endpoint')
    def _onchange_apple_provider(self):
        for provider in self:
            provider.apple_provider = False
            if provider.data_endpoint:
                if "appleid.apple.com" in provider.data_endpoint:
                    provider.apple_provider = True

    def get_apple_client_secret(self):
        private_key = base64.b64decode(self.apple_key_file.translate(None, delete=b'\r\n'), validate=True).decode()
        timestamp = int(fields.Datetime.now().timestamp())
        data = {
            "iss": self.apple_team_id,
            "iat": timestamp,
            "exp": timestamp + (60 * 30),  # 30 minutes
            "aud": self.data_endpoint,
            "sub": self.client_id
        }
        client_secret = jwt.encode(payload=data, key=private_key, algorithm="ES256", headers={"kid": self.apple_key_id})
        return client_secret

    def get_apple_auth_token(self, code=None, refresh_token=None, context=None):
        try:
            requests.get("https://appleid.apple.com", timeout=5)
        except (requests.ConnectionError, requests.Timeout) as exception:
            _logger.error("Your internet connenction is very slow or off: %s" % str(exception))

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        data = dict(
            grant_type="authorization_code" if not refresh_token else "refresh_token",
            redirect_uri=base_url + "/auth_oauth/apple/signin",
            client_id=self.client_id,
            client_secret=self.get_apple_client_secret(),
        )
        if code:
            data.update({
                "code": code
            })
        elif refresh_token:
            data.update({
                "refresh_token": refresh_token
            })

        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }

        response = requests.post(self.validation_endpoint, data=data, headers=headers)
        return response.json()

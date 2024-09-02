# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import jwt

from odoo import api, models
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import AccessDenied, UserError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _apple_generate_signup_values(self, provider_id, params):
        payload_data = jwt.decode(params.get('id_token'), algorithms=['RS256'], options={"verify_signature": False})
        email = payload_data.get("email")
        name = payload_data.get("name")
        if not name:
            name = payload_data.get("email").split("@")[0].upper()
        return {
            "name": name,
            "login": email,
            "email": email,
            "oauth_provider_id": provider_id,
            "oauth_access_token": params["access_token"],
            "oauth_uid": payload_data['sub'],
            "active": True
        }

    @api.model
    def _apple_auth_oauth_signin(self, provider_id, params):
        try:
            data = jwt.decode(params.get('id_token'), algorithms=['RS256'], options={"verify_signature": False})
            users = self.sudo().search([("oauth_uid", "=", data.get('sub')), ("oauth_provider_id", "=", provider_id)], limit=1)
            if not users:
                users = self.sudo().search([("login", "=", data.get("email"))], limit=1)
            if not users:
                raise AccessDenied()

            assert len(users.ids) == 1

            users.sudo().write({
                "oauth_access_token": params["access_token"]
            })
            return users.login
        except AccessDenied as access_denied_exception:
            if self._context and self._context.get("no_user_creation"):
                return None
            values = self._apple_generate_signup_values(provider_id, params)
            try:
                login, _ = self.signup(values)
                return login
            except (SignupError, UserError):
                raise access_denied_exception

    @api.model
    def apple_auth_oauth(self, provider_id, params):
        access_token = params.get("access_token")
        login = self._apple_auth_oauth_signin(provider_id, params)
        if not login:
            raise AccessDenied()
        return (self.env.cr.dbname, login, access_token)

# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import json
import logging
import werkzeug.utils
from werkzeug import urls
from werkzeug.exceptions import BadRequest

from odoo import http, SUPERUSER_ID
from odoo.addons.auth_oauth.controllers.main import OAuthLogin as Home, fragment_to_query_string
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.tools.misc import clean_context

_logger = logging.getLogger(__name__)


class OAuthLogin(Home):

    def list_providers(self):
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:
            providers = []

        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if not base_url:
            base_url = request.httprequest.url_root

        for provider in providers:
            return_url = urls.url_join(base_url, '/auth_oauth/signin')
            if provider['apple_provider']:
                return_url = urls.url_join(base_url, '/auth_oauth/apple/signin')
            auth_endpoint = provider['auth_endpoint']
            state = self.get_state(provider)
            params = dict(
                response_type='code' if provider['apple_provider'] else 'token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state)
            )
            if provider['apple_provider']:
                params.update({
                    'usePopup': True,
                    'response_mode': 'form_post',
                })
            provider['auth_link'] = "%s?%s" % (auth_endpoint, werkzeug.urls.url_encode(params))
        return providers


class AppleLogin(http.Controller):

    @http.route('/auth_oauth/apple/signin', type='http', auth='none', csrf=False)
    @fragment_to_query_string
    def apple_signin(self, **kw):
        state = json.loads(kw['state'])
        dbname = state['d']
        if not http.db_filter([dbname]):
            return BadRequest()
        ensure_db(db=dbname)

        provider_id = state['p']
        request.update_context(**clean_context(state.get('c', {})))
        try:
            provider = request.env['auth.oauth.provider'].sudo().browse(provider_id)

            authorization_data = provider.sudo().get_apple_auth_token(kw.get("code"), refresh_token=None)
            kw.update(authorization_data)

            _, login, key = request.env['res.users'].with_user(SUPERUSER_ID).apple_auth_oauth(provider_id, kw)
            request.env.cr.commit()

            action = kw.get('a')
            menu = kw.get('m')
            redirect = werkzeug.urls.url_unquote_plus(kw.get('r')) if kw.get('r') else False
            url = '/web'
            if redirect:
                url = redirect
            elif action:
                url = '/web#action=%s' % action
            elif menu:
                url = '/web#menu_id=%s' % menu

            pre_uid = request.session.authenticate(dbname, login, key)
            resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303)
            resp.autocorrect_location_header = False

            # Since /web is hardcoded, verify user has right to land on it
            if werkzeug.urls.url_parse(resp.location).path == '/web' and not request.env.user._is_internal():
                resp.location = '/'
            return resp
        except AttributeError:
            # auth_signup is not installed
            _logger.error("auth_signup not installed on database %s: oauth sign up cancelled.", dbname)
            url = "/web/login?oauth_error=1"
        except AccessDenied:
            # oauth credentials not valid, user could be on a temporary session
            _logger.info('OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
            url = "/web/login?oauth_error=3"
            redirect = request.redirect(url, 303)
            redirect.autocorrect_location_header = False
            return redirect
        except Exception:
            # signup error
            _logger.exception("Exception during request handling")
            url = "/web/login?oauth_error=2"

        redirect = request.redirect(url, 303)
        redirect.autocorrect_location_header = False
        return redirect

# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Sign in with Apple',
    'version': '17.0.1.0',
    'description': '"Sign in with Apple" authentication provider app allows to login via apple account',
    'license': 'OPL-1',
    'category': "Extra Tools",
    'summary': """
        Apple Authentication provider
        Apple auth provider
        Authenticate using apple
        Authenticate Using Apple ID
        login in with apple id
        sign in with apple id
        sign in with apple accounts
        iphone authenticate user
        app useauthentication
        apple developer sign in
        sign in with apple ios
        apple connect sign in
        apple id login
        apple authentication token
        apple authentication check
        Login with OAuth providers for odoo
        setup the OAuth Providers
        OAuth Single Sign On in odoo
        Odoo SSO using apple id
        sign in with apple id in odoo
        Apple Single Sign On OAuth
        login with app id in odoo
        sign up using apple id
        Apple Social Login Configuration in odoo """,
    'website': 'https://kanakinfosystems.com',
    'author': 'Kanak Infosystems LLP.',
    'depends': ["auth_oauth"],
    'data': [
        "views/auth_oauth_views.xml",
        "data/apple_auth_data.xml",
    ],
    'external_dependencies': {
        'python': ['PyJWT'],
    },
    'images': ["static/description/banner.gif"],
    'application': False,
    'auto_install': False,
    'price': 69,
    'currency': 'EUR'
}

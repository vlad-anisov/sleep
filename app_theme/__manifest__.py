{
    "name": "App theme",
    "version": "17.0",
    "category": "",
    "summary": "Summary",
    "description": """ Description """,
    "depends": [
        "base",
        "muk_web_enterprise_theme",
        "web",
        "web_enterprise",
    ],
    "data": [
    ],
    "assets": {
        "web.assets_backend": [
            "app_theme/static/src/js/app_theme.js",
            "app_theme/static/src/xml/app_theme.xml",
            "app_theme/static/src/css/app_theme.scss",
            "app_theme/static/src/css/app_theme.css",
        ],
        'web._assets_primary_variables': [
            ('after', 'web_enterprise/static/src/scss/primary_variables.scss', "app_theme/static/src/css/primary_variables.scss"),
        ],
    },
    "application": True,
}

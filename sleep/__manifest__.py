{
    "name": "Sleep",
    "version": "17.0.3.0",
    "category": "",
    "summary": "Summary",
    "description": """ Description """,
    "depends": [
        "base",
        "muk_web_enterprise_theme",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_users_data.xml",
        "data/ir_actions_server_data.xml",
        "data/ir_rule_data.xml",
        "views/script_views.xml",
        "views/menuitems.xml",
        "views/page_sleepy_chat_views.xml",
        "views/page_about_views.xml",
        "views/article_views.xml",
        "views/ritual_views.xml",
        "views/ritual_line_views.xml",
        "views/settings_views.xml",
        "views/statistic_views.xml",
        "views/web.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sleep/static/src/js/*.js",
            "sleep/static/src/xml/*.xml",
            "sleep/static/src/css/*.scss",
            "sleep/static/src/css/*.css",
        ],
    },
    "application": True,
}

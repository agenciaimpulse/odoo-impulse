# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Module: Odoo Redis Session (odoo_redis_session)
# File Identity: odoo_redis_session/__manifest__.py
# Author: Gilvanilson <webmaster.gvsantos@gmail.com>
# Created: 2026/08/17
# Copyright: 2026
# License: AGPL-3
# -----------------------------------------------------------------------------
#
{
    "name": "Odoo Redis Session",
    "summary": "Store Odoo HTTP sessions in Redis",
    "description": "Store Odoo 19 HTTP sessions in Redis.",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "author": "Impulse Team",
    "website": "https://github.com/impulseops/odoo-addons/tree/19.0/odoo_redis_session",
    "license": "AGPL-3",
    "depends": ["base"],
    "external_dependencies": {
        "python": ["redis"],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_load": "_post_load",
}

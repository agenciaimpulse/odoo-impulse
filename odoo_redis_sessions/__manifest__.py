# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Module: Odoo Redis Sessions (odoo_redis_sessions)
# File Identity: odoo_redis_sessions/__manifest__.py
# Author: Gilvanilson <webmaster.gvsantos@gmail.com>
# Created: 11/08/2026
# Copyright: 2026
# License: AGPL-3
# -----------------------------------------------------------------------------
#
{
    "name": "Odoo Redis Sessions",
    "summary": "Docker Secret support for Odoo Redis sessions",
    "description": """
Odoo Redis Sessions
==================

Extends the Redis Session Store module with Docker Secret support.

Adds support for reading the Redis password from REDIS_PASSWORD_FILE
while preserving the original redis_session_store implementation.
""",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "author": "Impulse Team",
    "website": "https://github.com/impulseops/odoo-addons/tree/19.0/odoo_redis_sessions",
    "license": "AGPL-3",
    "depends": ["base", "redis_sessions_store"],
    "external_dependencies": {
        "python": ["redis"],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_load": "_post_load_redis",
}
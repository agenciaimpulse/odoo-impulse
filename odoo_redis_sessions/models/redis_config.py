# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Module: Odoo Redis Sessions (odoo_redis_sessions)
# File Identity: odoo_redis_sessions/models/redis_config.py
# Author: Gilvanilson <webmaster.gvsantos@gmail.com>
# Created: 11/08/2026
# Copyright: 2026
# License: AGPL-3
# -----------------------------------------------------------------------------
#

import os

from odoo.addons.redis_session_store import redis_config


_original_create_config = redis_config.RedisConfig.create_config


def _create_config(cls, odoo_config=None):
    config = _original_create_config.__func__(cls, odoo_config)

    if not os.environ.get("REDIS_PASSWORD"):
        password_file = os.environ.get("REDIS_PASSWORD_FILE")

        if password_file:
            try:
                with open(password_file, encoding="utf-8") as secret_file:
                    password = secret_file.read().strip()
            except OSError:
                password = None

            if password:
                config.password = password

    return config


def _post_load_redis():
    redis_config.RedisConfig.create_config = classmethod(_create_config)
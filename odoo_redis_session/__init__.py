# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Module: Odoo Redis Session (odoo_redis_session)
# File Identity: odoo_redis_session/__init__.py
# Author: Gilvanilson <webmaster.gvsantos@gmail.com>
# Created: 2026/08/17
# Copyright: 2026
# License: AGPL-3
# -----------------------------------------------------------------------------
#
from . import models
from .models.redis_session import post_load as _post_load

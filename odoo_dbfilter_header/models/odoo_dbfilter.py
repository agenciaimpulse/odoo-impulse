# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Module: Odoo dbfilter from header (odoo_dbfilter_header)
# File: odoo_dbfilter_header/models/odoo_dbfilter.py
# Author: Gilvanilson <webmaster.gvsantos@gmail.com>
# Created: 2026/08/08
# Copyright: 2026
# License: AGPL-3
# -----------------------------------------------------------------------------
#
import logging
import re

from odoo import http
from odoo.tools import config

_logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Original Odoo database filter
# -----------------------------------------------------------------------------

_original_db_filter = http.db_filter


def _normalize_hostname(hostname: str) -> str:
    """Convert an HTTP hostname into the corresponding Odoo database name."""
    hostname = hostname.lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname.replace(".", "_")


def db_filter(dbs, host=None):
    """Filter Odoo databases according to the request hostname."""
    dbs = _original_db_filter(dbs, host)
    dbs_available = list(dbs)

    # Se houver apenas 1 banco no servidor, não bloqueia o acesso
    if len(dbs_available) == 1:
        return dbs_available

    # Tenta obter o httprequest de forma segura
    httprequest = getattr(http.request, "httprequest", None) if http.request else None
    hostname = httprequest.host if httprequest else None

    if not hostname:
        return dbs_available

    # Remove a porta do cabeçalho Host
    hostname = hostname.split(":", 1)[0]

    # Bypass para acessos via IP ou localhost (evita falso alerta em healthchecks/desenvolvimento)
    if hostname in ("127.0.0.1", "localhost") or re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
        return dbs_available

    normalized_db_name = _normalize_hostname(hostname)
    database_regex = re.compile(rf"^{re.escape(normalized_db_name)}$")

    filtered_dbs = [
        db
        for db in dbs_available
        if database_regex.fullmatch(db)
    ]

    if not filtered_dbs:
        _logger.warning(
            "No Odoo database matches hostname '%s' "
            "(normalized database name: '%s'). "
            "Available databases: %s",
            hostname,
            normalized_db_name,
            ", ".join(dbs_available) if dbs_available else "none",
        )
        # Retorna todas as bases disponíveis como fallback para permitir ao usuário escolher na tela /web/database/selector
        return dbs_available

    return filtered_dbs

# -----------------------------------------------------------------------------
# Monkey patch
# -----------------------------------------------------------------------------
#
# The override is applied only when:
#
#   1. Odoo is running in proxy mode; and
#   2. this addon is loaded as a server-wide module.
#
# This prevents the override from being applied when the addon is installed
# but not explicitly configured as a server-wide module.
# -----------------------------------------------------------------------------

if (
    config.get("proxy_mode")
    and "odoo_dbfilter_header" in config.get("server_wide_modules", [])
):
    _logger.info(
        "Enabling hostname-based database filtering for odoo_dbfilter_header."
    )
    http.db_filter = db_filter
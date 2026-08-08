# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Module: Odoo dbfilter from header (odoo_dbfilter_header)
# File: odoo_dbfilter_header/models/odoo_dbfilter.py
# Author: Gilvanilson <webmaster.gvsantos@gmail.com>
# Created: 08/08/2026
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


def _normalize_hostname(hostname):
    """Convert an HTTP hostname into the corresponding Odoo database name.

    The normalization follows the database naming convention used by this addon:

        empresa.com       -> empresa_com
        www.empresa.com   -> empresa_com
        empresa.com.br    -> empresa_com_br

    The hostname is converted to lowercase, the optional ``www.`` prefix is
    removed, and dots are replaced with underscores.
    """
    hostname = hostname.lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname.replace(".", "_")


def db_filter(dbs, host=None):
    """Filter Odoo databases according to the request hostname.

    The original Odoo database filter is applied first. The resulting list is
    then restricted to the database corresponding to the HTTP Host received by Odoo.

    This implementation is intended for Odoo deployments behind Traefik.
    Traefik forwards the request hostname to Odoo through the standard HTTP Host header.

    Args:
        dbs: Iterable containing the available database names.
        host: Host value supplied to the original Odoo db_filter function.

    Returns:
        list: Databases matching the normalized request hostname.
    """
    # Preserve the original Odoo database filtering behavior.
    dbs = _original_db_filter(dbs, host)

    # Keep a copy for diagnostics before applying the hostname filter.
    dbs_available = list(dbs)

    # Obtain the hostname from the current HTTP request.
    hostname = http.request.httprequest.host

    if not hostname:
        _logger.warning(
            "Unable to filter database by hostname: HTTP Host is empty."
        )
        return dbs

    # Remove the port when the Host header contains one.
    #
    # Examples:
    #   empresa.com:443 -> empresa.com
    #   empresa.com:8069 -> empresa.com
    hostname = hostname.split(":", 1)[0]

    normalized_db_name = _normalize_hostname(hostname)

    # Match the complete database name.
    database_regex = re.compile(
        rf"^{re.escape(normalized_db_name)}$"
    )

    _logger.info(
        "Filtering Odoo databases by hostname: %s -> %s",
        hostname,
        normalized_db_name,
    )

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
    and "odoo_dbfilter_header" in config.get("server_wide_modules")
):
    _logger.info(
        "Enabling hostname-based database filtering "
        "for odoo_dbfilter_header."
    )

    http.db_filter = db_filter

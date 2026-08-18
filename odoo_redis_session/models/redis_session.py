# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Module: Odoo Redis Session (odoo_redis_session)
# File Identity: odoo_redis_session/models/redis_session.py
# Author: Gilvanilson <webmaster.gvsantos@gmail.com>
# Created: 2026/08/17
# Copyright: 2026
# License: AGPL-3
# -----------------------------------------------------------------------------
#
"""Redis-backed HTTP session store for Odoo 19."""

from __future__ import annotations

import base64
import functools
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from hashlib import sha512
from typing import Any, Iterable

import redis

import odoo.http
from odoo import tools
from odoo.service import security


_logger = logging.getLogger(__name__)

DEFAULT_EXPIRATION = 60 * 60 * 24 * 7
DEFAULT_ANONYMOUS_EXPIRATION = 60 * 2
DEFAULT_IGNORED_URLS = ("/longpolling", "/calendar/notify")
SESSION_IDENTIFIER_LENGTH = 42
SESSION_DELETION_TIMER = 120


class RedisSessionError(RuntimeError):
    """Raised when Redis cannot serve an HTTP session operation."""


def _environment_or_config(
    name: str, config_name: str, config: dict[str, Any], default: Any
) -> Any:
    return os.environ.get(name, config.get(config_name, default))


def _as_positive_integer(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _as_boolean(value: Any, default: bool) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _read_password(config: dict[str, Any]) -> str | None:
    password = os.environ.get("REDIS_PASSWORD")
    if password:
        return password

    password_file = os.environ.get("REDIS_PASSWORD_FILE")
    if password_file:
        try:
            with open(password_file, encoding="utf-8") as secret_file:
                password = secret_file.read().strip()
        except OSError:
            _logger.warning("Unable to read the Redis password file")
        else:
            if password:
                return password

    configured_password = config.get("password")
    return configured_password or None


@dataclass(frozen=True)
class RedisSessionConfig:
    host: str
    port: int
    prefix: str
    ssl: bool
    password: str | None
    expiration: int
    anonymous_expiration: int
    timeout_on_inactivity: bool
    ignored_urls: tuple[str, ...]

    @classmethod
    def from_odoo_config(cls) -> "RedisSessionConfig":
        misc = tools.config.misc.get("odoo_redis_session", {})
        ignored_urls = list(DEFAULT_IGNORED_URLS)
        configured_urls = _environment_or_config(
            "ODOO_SESSION_REDIS_TIMEOUT_IGNORED_URLS", "ignored_urls", misc, ""
        )
        if configured_urls:
            ignored_urls.extend(
                url.strip() for url in str(configured_urls).split(",") if url.strip()
            )
        return cls(
            host=str(_environment_or_config("REDIS_HOST", "host", misc, "localhost")),
            port=_as_positive_integer(
                _environment_or_config("REDIS_PORT", "port", misc, 6379), 6379
            ),
            prefix=str(
                _environment_or_config("REDIS_PREFIX", "prefix", misc, "odoo")
            ).strip(":"),
            ssl=_as_boolean(
                _environment_or_config("REDIS_SSL", "ssl", misc, False), False
            ),
            password=_read_password(misc),
            expiration=_as_positive_integer(
                _environment_or_config(
                    "ODOO_SESSION_REDIS_EXPIRATION",
                    "expiration",
                    misc,
                    DEFAULT_EXPIRATION,
                ),
                DEFAULT_EXPIRATION,
            ),
            anonymous_expiration=_as_positive_integer(
                _environment_or_config(
                    "ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS",
                    "anonymous_expiration",
                    misc,
                    DEFAULT_ANONYMOUS_EXPIRATION,
                ),
                DEFAULT_ANONYMOUS_EXPIRATION,
            ),
            timeout_on_inactivity=_as_boolean(
                _environment_or_config(
                    "ODOO_SESSION_REDIS_TIMEOUT_ON_INACTIVITY",
                    "timeout_on_inactivity",
                    misc,
                    True,
                ),
                True,
            ),
            ignored_urls=tuple(dict.fromkeys(ignored_urls)),
        )

    def connect(self) -> redis.Redis:
        return redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            ssl=self.ssl,
            socket_connect_timeout=5,
            socket_timeout=5,
        )


class RedisSessionStore:
    """Session store implementing the Odoo 19 ``Application`` contract."""

    def __init__(self, config: RedisSessionConfig, session_class: type) -> None:
        self.session_class = session_class
        self.config = config
        namespace = config.prefix or "odoo"
        self.key_prefix = f"{namespace}:session:"
        self.redis = config.connect()
        self._ensure_connection()

    def _ensure_connection(self) -> None:
        try:
            self.redis.ping()
        except redis.RedisError:
            raise RedisSessionError("Redis session store is unavailable") from None

    def _run(self, operation):
        try:
            return operation()
        except redis.RedisError:
            _logger.error("Redis session operation failed")
            raise RedisSessionError("Redis session operation failed") from None

    def build_key(self, sid: str) -> str:
        return f"{self.key_prefix}{sid}"

    def generate_key(self, salt: bytes | None = None) -> str:
        entropy = (salt or b"") + str(time.time()).encode() + os.urandom(64)
        return base64.urlsafe_b64encode(sha512(entropy).digest()[:-1]).decode()

    def is_valid_key(self, sid: str | None) -> bool:
        return isinstance(sid, str) and bool(re.fullmatch(r"[A-Za-z0-9_-]{84}", sid))

    def new(self):
        return self.session_class({}, self.generate_key(), True)

    def _expiration(self, session: Any) -> int:
        return self.config.expiration if session.uid else self.config.anonymous_expiration

    def _current_path_is_ignored(self) -> bool:
        try:
            path = odoo.http.request.httprequest.path
        except RuntimeError:
            return False
        return any(path.startswith(prefix) for prefix in self.config.ignored_urls)

    def _refresh_expiration(self, session: Any) -> None:
        if not self.config.timeout_on_inactivity or self._current_path_is_ignored():
            return
        self._run(
            lambda: self.redis.expire(
                self.build_key(session.sid), self._expiration(session)
            )
        )

    def save(self, session: Any) -> bool:
        try:
            data = json.dumps(dict(session), separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError) as error:
            raise RedisSessionError("Session data is not JSON serializable") from error
        return bool(
            self._run(
                lambda: self.redis.set(
                    self.build_key(session.sid), data, ex=self._expiration(session)
                )
            )
        )

    def delete(self, session: Any) -> int:
        return int(self._run(lambda: self.redis.delete(self.build_key(session.sid))))

    def get(self, sid: str):
        if not self.is_valid_key(sid):
            return self.new()
        saved = self._run(lambda: self.redis.get(self.build_key(sid)))
        if saved is None:
            return self.session_class({}, sid, True)
        try:
            data = json.loads(saved)
        except (TypeError, ValueError):
            _logger.warning("Discarding invalid Redis session data")
            self._run(lambda: self.redis.delete(self.build_key(sid)))
            return self.session_class({}, sid, True)
        session = self.session_class(data, sid, False)
        self._refresh_expiration(session)
        return session

    def rotate(self, session: Any, env: Any, soft: bool = False) -> None:
        if soft:
            static_identifier = session.sid[:SESSION_IDENTIFIER_LENGTH]
            recent_session = self.get(session.sid)
            if "next_sid" in recent_session:
                session.sid = recent_session["next_sid"]
                return
            next_sid = static_identifier + self.generate_key()[SESSION_IDENTIFIER_LENGTH:]
            session["next_sid"] = next_sid
            session["deletion_time"] = time.time() + SESSION_DELETION_TIMER
            self.save(session)
            session["gc_previous_sessions"] = True
            session.sid = next_sid
            del session["deletion_time"]
            del session["next_sid"]
        else:
            self.delete(session)
            session.sid = self.generate_key()
        if session.uid:
            session.session_token = security.compute_session_token(session, env)
        session.should_rotate = False
        session["create_time"] = time.time()
        self.save(session)

    def get_missing_session_identifiers(self, identifiers: Iterable[str]) -> set[str]:
        missing_identifiers = set(identifiers)
        for identifier in missing_identifiers.copy():
            if not isinstance(identifier, str) or len(identifier) != SESSION_IDENTIFIER_LENGTH:
                raise ValueError("Session identifier format is invalid")
            pattern = f"{self.key_prefix}{identifier}*"
            if self._run(lambda: next(self.redis.scan_iter(match=pattern), None)):
                missing_identifiers.discard(identifier)
        return missing_identifiers

    def delete_from_identifiers(self, identifiers: Iterable[str]) -> int:
        deleted = 0
        for identifier in identifiers:
            if not isinstance(identifier, str) or len(identifier) != SESSION_IDENTIFIER_LENGTH:
                raise ValueError("Session identifier format is invalid")
            keys = list(
                self._run(
                    lambda: self.redis.scan_iter(
                        match=f"{self.key_prefix}{identifier}*"
                    )
                )
            )
            if keys:
                deleted += int(self._run(lambda: self.redis.delete(*keys)))
        return deleted

    def delete_old_sessions(self, session: Any) -> None:
        if "gc_previous_sessions" not in session:
            return
        if session["create_time"] + SESSION_DELETION_TIMER >= time.time():
            return
        self.delete_from_identifiers([session.sid[:SESSION_IDENTIFIER_LENGTH]])
        del session["gc_previous_sessions"]
        self.save(session)

    def vacuum(self, *args: Any, **kwargs: Any) -> None:
        """Redis expires session keys without filesystem garbage collection."""


def _session_store(_application: odoo.http.Application) -> RedisSessionStore:
    return RedisSessionStore(RedisSessionConfig.from_odoo_config(), odoo.http.Session)


def post_load() -> None:
    """Install the session store factory when loaded as a server-wide addon."""
    odoo.http.root.__dict__.pop("session_store", None)
    session_store = functools.cached_property(_session_store)
    session_store.__set_name__(odoo.http.Application, "session_store")
    odoo.http.Application.session_store = session_store

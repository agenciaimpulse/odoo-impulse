---
name: Odoo Redis Sessions
author: Gilvanilson <webmaster.gvsantos@gmail.com>
date: 2026/08/11
copyright: 2026
license: AGPL-3
---

# Odoo Redis Sessions

Odoo Redis Sessions extends the `redis_sessions_store` Odoo module with Docker Secret support for Redis authentication.

This module is based on [`mangono-odoo-redis-session`](https://pypi.org/project/mangono-odoo-redis-session) 1.4.1.

## Architecture

This module depends on:

- `redis_sessions_store`

The upstream module provides the Redis-backed Odoo session implementation.

This module only extends its configuration layer to support Docker Secrets.

## Redis configuration

```ini
[redis_sessions_store]
host = redis
port = 6379
prefix = odoo19_sess
ssl = False
```

## Docker Secret

The Redis password is provided through a Docker Secret:

```yaml
environment:
  REDIS_PASSWORD_FILE: /run/secrets/redis_passwd

secrets:
  - redis_passwd
```

The module reads the secret directly from the file.

The precedence is:

1. `REDIS_PASSWORD`
2. `REDIS_PASSWORD_FILE`
3. `[redis_sessions_store] password`
4. No password

The secret is not exported to the process environment.

## Security

`REDIS_PASSWORD_FILE` is intended for environments using Docker Secrets.

The module does not copy the secret into another file and does not export it as an environment variable.

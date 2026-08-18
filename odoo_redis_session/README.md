# Odoo Redis Session

`odoo_redis_session` stores Odoo 19 HTTP sessions in Redis instead of the filesystem. It is a server-wide infrastructure addon and does not depend on `redis_session_store`.

## Requirements and loading

Install the Python dependency in the Odoo environment:

```bash
pip install redis
```

To install directly in the running container:

```bash
docker exec -u root <container-name> pip3 install --no-cache-dir redis

docker restart <container-name>
```

Check:

```bash
docker exec <container-name> python3 -c "import redis; print(redis.__version__)"   
```

**This is temporary:** the installation will be lost if the container is recreated. To persist it across future deployments, the image must be derived using a `Dockerfile` that runs `pip3 install redis`.

Add `odoo_redis_session` to Odoo's `server_wide_modules`. The addon must be loaded when the server starts; installing it in a database is not required for the session store to be active.

## Environment

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_PREFIX` | `odoo` | Redis key namespace |
| `REDIS_SSL` | `false` | Enable TLS (`true` or `1`) |
| `REDIS_PASSWORD` | unset | Redis password |
| `REDIS_PASSWORD_FILE` | unset | File containing the Redis password |
| `ODOO_SESSION_REDIS_EXPIRATION` | `604800` | Authenticated session TTL, in seconds |
| `ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS` | `120` | Anonymous session TTL, in seconds |
| `ODOO_SESSION_REDIS_TIMEOUT_ON_INACTIVITY` | `true` | Refresh TTL when a session is used |
| `ODOO_SESSION_REDIS_TIMEOUT_IGNORED_URLS` | unset | Comma-separated URL prefixes excluded from TTL refresh |

The default ignored URL prefixes are `/longpolling` and `/calendar/notify`.

## Docker Secrets

Set `REDIS_PASSWORD_FILE` to the mounted secret path, commonly `/run/secrets/redis_passwd`. The module reads that file at runtime and keeps the value only in memory. Password resolution priority is:

1. `REDIS_PASSWORD`
2. `REDIS_PASSWORD_FILE`
3. the optional `[odoo_redis_session] password` Odoo configuration value

Passwords are never logged or written by the module.

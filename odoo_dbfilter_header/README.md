# odoo_dbfilter_header

[![Odoo 19.0](https://img.shields.io/badge/Odoo-19.0-714B67.svg)](https://github.com/odoo/odoo/tree/19.0)
[![License: AGPL-3](https://img.shields.io/badge/license-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Maintained by Impulse Ops](https://img.shields.io/badge/maintained%20by-Impulse%20Ops-lightgrey.svg)](https://github.com/impulseops)

Filter Odoo databases by request hostname.

This addon extends Odoo's database filtering mechanism to select the database associated with the hostname of the incoming HTTP request.

It was developed for **Odoo 19 Community Edition** deployments running behind **Traefik**.

The addon is particularly useful for multi-database Odoo deployments where each database follows a hostname-based naming convention.

For example:

```text
company.com
    ↓
company_com

company.com.br
    ↓
company_com_br

store.company.com.br
    ↓
store_company_com_br
```

## Features

* Uses the standard HTTP `Host` value received by Odoo.
* Normalizes the hostname into an Odoo database name.
* Removes the `www.` prefix when present.
* Removes the port from the hostname when present.
* Converts the hostname to lowercase.
* Replaces dots (`.`) with underscores (`_`).
* Preserves Odoo's original database filtering before applying the hostname-based filter.
* Requires no custom `X-Odoo-dbfilter` header.
* Designed for deployments behind a reverse proxy.
* Tested with **Odoo 19 Community Edition and Traefik**.

## How it works

When a request reaches Odoo through Traefik, the addon reads the hostname from the standard HTTP `Host` value.

The hostname is normalized according to the following rules:

1. Convert the hostname to lowercase.
2. Remove the `www.` prefix when present.
3. Remove the port when present.
4. Replace every dot (`.`) with an underscore (`_`).
5. Use the resulting value as the exact database name to match.

For example:

```text
www.company.com:443
        ↓
company.com
        ↓
company_com
```

The addon then filters the databases available to Odoo and keeps only the database whose name exactly matches the normalized hostname.

## Database naming convention

The database name must correspond to the normalized hostname.

| Request hostname       | Database name         |
| ---------------------- | --------------------- |
| `company.com`          | `company_com`         |
| `www.company.com`      | `company_com`         |
| `company.com.br`       | `company_com_br`      |
| `www.company.com.br`   | `company_com_br`      |
| `store.company.com.br` | `store_company_com_br` |

The hostname is normalized to lowercase before the database name is matched.

### Why use underscores?

The purpose of this addon is to allow a hostname such as:

```text
company.com.br
```

to correspond to a database named:

```text
company_com_br
```

This avoids using dots directly in the database name while preserving a predictable relationship between the public hostname and the Odoo database.

## Requirements

* **Odoo 19 Community Edition**
* Odoo running with `proxy_mode = True`
* A reverse proxy in front of Odoo
* **Traefik** as the supported and tested reverse proxy
* The addon loaded as a server-wide module

## Installation

Copy the `odoo_dbfilter_header` directory into an Odoo addons path.

Then add the addon to Odoo's `server_wide_modules` configuration.

For example:

```ini
server_wide_modules = base,web,odoo_dbfilter_header
```

Enable proxy mode:

```ini
proxy_mode = True
```

Restart the Odoo server after changing these settings.

Finally, make sure the database name follows the hostname normalization convention described above.

## Server-wide module

This addon modifies Odoo's `http.db_filter` function when it is loaded as a server-wide module.

Therefore, adding the addon to `server_wide_modules` is required.

Example:

```ini
server_wide_modules = base,web,odoo_dbfilter_header
```

Do not load this addon together with another module that replaces the same `http.db_filter` function, as the implementations may conflict.

## Proxy mode

The addon is intended for Odoo deployments behind a reverse proxy.

Enable Odoo's proxy mode:

```ini
proxy_mode = True
```

This allows Odoo to correctly interpret requests when it is running behind the proxy.

The reverse proxy remains responsible for TLS termination, routing, and forwarding the HTTP request to Odoo.

## Traefik

**Traefik is the reverse proxy used to develop and test this addon.**

No custom database-filter header is required.

The addon reads the standard HTTP `Host` value from the request received by Odoo.

A typical request flow is:

```text
Browser
   │
   │ HTTPS
   ▼
Traefik
   │
   │ HTTP
   │ Host: company.com
   ▼
Odoo
   │
   ▼
odoo_dbfilter_header
   │
   ▼
company_com
   │
   ▼
PostgreSQL database
```

The exact Traefik configuration is deployment-specific and is therefore not part of this addon.

HTTPS, TLS certificates, routers, middlewares, security headers, and other reverse-proxy settings should be configured according to the requirements of the Odoo deployment.

## Docker

The addon is designed to work with containerized Odoo deployments.

The development and test environment for this addon uses Odoo running in Docker with Traefik as the reverse proxy.

A typical architecture is:

```text
Internet / Browser
       │
       │ HTTPS
       ▼
   Traefik
       │
       │ HTTP
       ▼
Odoo container
       │
       ▼
PostgreSQL
```

Multiple databases can then be associated with different hostnames:

```text
company.com       → company_com
store.com         → store_com
client.com.br     → client_com_br
```

## Compatibility

This addon targets:

* Odoo 19 Community Edition
* Traefik as reverse proxy

Other reverse proxies may work when they provide the expected HTTP `Host` value to Odoo, but they have **not been tested as part of this project**.

Therefore, compatibility with other reverse proxies should not be assumed.

## Security considerations

The database selected by the addon is determined by the HTTP hostname.

Therefore:

* DNS and reverse-proxy routing must be configured correctly.
* Requests should only reach Odoo through trusted routing infrastructure.
* Odoo should be configured with `proxy_mode = True` when operating behind a reverse proxy.
* Database names should follow the documented naming convention.
* This addon is **not** an authentication or authorization mechanism.

The hostname-based filter determines which database is selected. Access control must still be handled by Odoo and the surrounding infrastructure.

## Credits

This addon was developed by **Impulse Ops** and is based on the concept of the [`dbfilter_from_header`](https://github.com/OCA/server-tools/tree/19.0/dbfilter_from_header) addon.

Original project and related work:

* [Therp BV — dbfilter_from_header](https://apps.odoo.com/apps/modules/19.0/dbfilter_from_header)
* [Odoo Community Association — dbfilter_from_header](https://github.com/OCA/server-tools/tree/19.0/dbfilter_from_header)

The implementation in this repository is adapted for hostname-based database selection in the Impulse Ops Odoo infrastructure, with Traefik as the tested reverse proxy.

## Author

**Gilvanilson**

* GitHub: [@devgilvieira](https://github.com/devgilvieira)
* Email: [webmaster.gvsantos@gmail.com](mailto:webmaster.gvsantos@gmail.com)

## Maintainer

**Impulse Ops**

* GitHub: [impulseops](https://github.com/impulseops)
* Repository: [odoo-addons](https://github.com/impulseops/odoo-addons)
* Addon: [odoo_dbfilter_header](https://github.com/impulseops/odoo-addons/tree/19.0/odoo_dbfilter_header)

## License

This addon is licensed under the **GNU Affero General Public License version 3 (AGPL-3)**.

See the [GNU AGPL-3 license](https://www.gnu.org/licenses/agpl-3.0.html) for details.

# Contributing to Odoo Addons

This document describes the development workflow used to maintain the **Impulse Ops Odoo Addons** repository.

## Repository structure

Odoo addons are organized by Odoo version using dedicated Git branches.

```text
odoo-addons/
├── main/
│   ├── README.md
│   └── CONTRIBUTING.md
│
├── 18.0/
│   ├── README.md
│   └── addons...
│
└── 19.0/
    ├── README.md
    └── addons...
```

The `main` branch contains repository-level documentation.

Version branches contain the addons compatible with their respective Odoo releases.

For example:

* `18.0` → Odoo 18 Community Edition
* `19.0` → Odoo 19 Community Edition

Do not mix addons from different Odoo versions in the same branch.

## Development environment

The recommended development environment is **Linux/WSL with VS Code**.

Clone the repository:

```bash
git clone https://github.com/impulseops/odoo-addons.git
cd odoo-addons
```

Fetch all remote branches:

```bash
git fetch --all
```

To work with a specific Odoo version:

```bash
git switch 19.0
```

or:

```bash
git switch 18.0
```

## Working with multiple Odoo versions

When development for multiple Odoo versions is required simultaneously, use separate working directories or Git worktrees.

For example:

```bash
git worktree add ../odoo-addons-18 18.0
git worktree add ../odoo-addons-19 19.0
```

This keeps each Odoo version in an isolated working directory while using the same Git repository.

Example:

```text
~/Projetos/impulseops/
├── odoo-addons/
├── odoo-addons-18/
└── odoo-addons-19/
```

This approach is preferable to manually initializing separate Git repositories for each version.

## Odoo addon structure

Each addon should follow the standard Odoo module structure appropriate to its functionality.

A typical addon may look like:

```text
19.0/
└── module_name/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    ├── views/
    ├── security/
    ├── data/
    ├── static/
    └── README.md
```

Only directories and files required by the addon should be included.

## Version compatibility

Each addon must be developed and tested against the Odoo version represented by its branch.

For example:

```text
18.0/ → Odoo 18
19.0/ → Odoo 19
```

When an addon is migrated to a new Odoo release, the migration should be performed in the corresponding version branch.

Do not assume that an addon developed for one Odoo version is compatible with another version without testing.

## Module naming

Addon technical names should:

* use lowercase letters;
* use underscores as word separators;
* be concise and descriptive;
* avoid unnecessary vendor or infrastructure-specific names;
* clearly represent the functionality provided by the addon.

Example:

```text
odoo_dbfilter_header
```

## Documentation

Each addon should provide its own documentation when appropriate.

At minimum, documentation should explain:

* what the addon does;
* supported Odoo versions;
* dependencies;
* installation requirements;
* configuration;
* important limitations;
* compatibility considerations;
* licensing.

The version branch `README.md` should serve as an index of the addons available for that Odoo release.

## Git workflow

Before making changes, ensure that you are working on the correct version branch:

```bash
git branch --show-current
```

Example:

```text
19.0
```

Review the changes:

```bash
git status
git diff
```

Stage the changes:

```bash
git add .
```

Create a descriptive commit:

```bash
git commit -m "refactor(odoo_dbfilter_header): improve hostname database filtering"
```

Push the branch:

```bash
git push origin 19.0
```

## Commit messages

Use concise commit messages that describe the purpose of the change.

Examples:

```text
feat(module): add new functionality
fix(module): correct database filtering
refactor(module): simplify implementation
docs(module): update documentation
chore(repo): update repository configuration
```

The module name should be included when the change is specific to an addon.

## Pull requests

Before submitting a pull request:

1. Confirm that the correct Odoo version branch is being used.
2. Review the complete Git diff.
3. Verify the module manifest.
4. Verify dependencies.
5. Test the addon in the target Odoo version.
6. Update the addon documentation when necessary.
7. Ensure that no unrelated files or changes are included.

## Testing

Every addon should be tested according to its functionality.

For addons that modify Odoo server behavior, testing should include the relevant deployment architecture.

For example, `odoo_dbfilter_header` is tested with:

```text
Odoo 19 CE
    +
Docker
    +
Traefik
    +
PostgreSQL
```

Compatibility with other environments should only be documented after appropriate testing.

## Licensing

Licensing is defined at the addon level through its `__manifest__.py`.

Contributors must preserve the existing license information unless a deliberate licensing change has been reviewed and approved.

Do not assume that every addon in this repository uses the same license.

## Maintainer

[**Impulse Ops**](https://github.com/impulseops)

=========================
dbfilter_header_traefik
=========================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! Este arquivo é gerado por oca-gen-addon-readme !!
   !! As alterações serão sobrescritas.              !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-your_github_org%2Fdbfilter--header--traefik-lightgray.png?logo=github
    :target: https://github.com/your_github_org/dbfilter_header_traefik
    :alt: your_github_org/dbfilter_header_traefik
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/server-tools-18-0/server-tools-18-0-dbfilter_from_header # Manter ou mudar para o seu projeto de tradução, se houver.
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/server-tools&target_branch=18.0 # Manter ou mudar para o seu runboat, se houver.
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

Este addon permite filtrar bancos de dados com base no cabeçalho HTTP `X-Odoo-dbfilter`, adaptado especificamente para uso com Traefik. Ele formata o nome do host (domínio) enviado pelo Traefik para corresponder ao padrão esperado dos nomes de banco de dados do Odoo (substituindo pontos por sublinhados).

**Sumário**

.. contents::
   :local:

Instalação
==========

Para instalar este módulo, siga os passos abaixo:

1.  Clone este repositório ou baixe o módulo e adicione a pasta `dbfilter_header_traefik` à sua pasta de `addons` do Odoo.
2.  Adicione o módulo `dbfilter_header_traefik` ao parâmetro `server_wide_modules` no seu arquivo `odoo.conf`. Certifique-se de remover qualquer configuração anterior de `dbfilter_from_header` para evitar conflitos:

    ``server_wide_modules = base,web,dbfilter_header_traefik``

3.  Certifique-se de que o `proxy_mode` esteja habilitado em seu `odoo.conf`:

    ``proxy_mode = True``

Configuração do Traefik
=======================

Este módulo espera que o Traefik envie o cabeçalho `X-Odoo-dbfilter` contendo o **nome do host completo** (ex: `seudominio.com.br` ou `www.seudominio.com.br`). O módulo Odoo irá processar este valor para encontrar o banco de dados correspondente.

Para o Traefik, utilize a seguinte configuração no seu middleware de cabeçalhos (`odoo[VERSÃO]-headers` no seu exemplo `odoo[VERSÃO]_dynamic_conf.yml`):

```yaml
# Exemplo de configuração no seu /opt/stacks/portainer/config/odoo[VERSÃO]_dynamic_conf.yml
http:
  # ... (seus routers e outros middlewares) ...
  middlewares:
    odoo[VERSÃO]-headers:
      headers:
        # ... outras configurações de cabeçalho (STS, X-Forwarded-Proto, Cache-Control) ...
        customRequestHeaders:
          X-Forwarded-Proto: "https"
          # Envia o nome do host exato para o Odoo.
          # O módulo 'dbfilter_header_traefik' fará a formatação necessária.
          X-Odoo-dbfilter: "{Host}"
        # ... outras configurações de cabeçalho ...
```

Uso
===

Após a instalação e configuração, as requisições direcionadas ao Odoo através do Traefik terão o banco de dados selecionado automaticamente com base no nome do host da requisição.

Créditos
========

Autores
-------

* `Gilvanilson <https://github.com/gilvanilson-gil>`_
* `Therp BV <https://apps.odoo.com/apps/modules/18.0/dbfilter_from_header>`_ (Base do módulo original)
* `Odoo Community Association <https://github.com/OCA/server-tools/tree/18.0/dbfilter_from_header>`_ (Base do módulo original)

Mantenedores
------------

Este módulo é mantido pela `Agência Impulse <https://github.com/agenciaimpulse>`_.
.. image:: https://agenciaimpulse.com.br/logo-impulse
:alt: Agência Impulse
:target: https://agenciaimpulse.com.br

Este módulo faz parte do projeto `agenciaimpulse/odoo-impulse <https://github.com/agenciaimpulse/odoo-impulse/dbfilter_header_traefik>`_ no GitHub.

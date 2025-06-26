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

Este módulo não requer configurações específicas de cabeçalhos personalizados no Traefik para o filtro de banco de dados. Ele lê diretamente o cabeçalho padrão ``Host`` da requisição HTTP (ex: ``seudominio.com.br`` ou ``www.seudominio.com.br``) para determinar o nome do banco de dados.

Você deve garantir que o Traefik esteja configurado para rotear o tráfego para seu serviço Odoo e que os cabeçalhos essenciais para ambientes de proxy estejam presentes. Por exemplo, é fundamental que o Traefik envie o cabeçalho ``X-Forwarded-Proto: "https"`` para informar ao Odoo que a conexão original do cliente é segura (HTTPS), mesmo que a comunicação entre o Traefik e o Odoo seja via HTTP.

Um exemplo de configuração de middleware de cabeçalhos no Traefik (geralmente em um arquivo de configuração dinâmica como ``odoo[VERSÃO]_dynamic_conf.yml``):

.. code:: yaml

   # Exemplo de configuração no seu /opt/stacks/portainer/config/odoo[VERSÃO]_dynamic_conf.yml
   http:
     # ... (seus routers e outros middlewares) ...

     middlewares:
       odoo[VERSÃO]-headers:
         headers:
           # Configurações de segurança e cabeçalhos padrão
           stsSeconds: 31536000
           stsIncludeSubdomains: true
           stsPreload: true
           customRequestHeaders:
             # Informa ao Odoo que a conexão original do cliente é HTTPS.
             # Essencial para que o Odoo gere URLs corretamente (ex: redirecionamentos para HTTPS).
             X-Forwarded-Proto: "https"
           customResponseHeaders:
             # Define cache para assets estáticos no navegador e proxies.
             Cache-Control: "public, max-age=31536000"


**Observação:** O cabeçalho ``Host`` é automaticamente enviado pelo Traefik ao Odoo. O módulo ``dbfilter_header_traefik`` processará este cabeçalho padrão para filtrar o banco de dados sem a necessidade de uma configuração ``X-Odoo-dbfilter`` explícita no Traefik.

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
.. image:: https://agenciaimpulse.com.br/web/binary/company_logo
:alt: Agência Impulse
:target: https://agenciaimpulse.com.br

Este módulo faz parte do projeto `agenciaimpulse/odoo-impulse <https://github.com/agenciaimpulse/odoo-impulse/tree/18.0/dbfilter_header_traefik>`_ no GitHub.

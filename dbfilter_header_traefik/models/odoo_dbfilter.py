# dbfilter_header_traefik/override.py
import logging
import re

from odoo import http
from odoo.tools import config

_logger = logging.getLogger(__name__)

# Mantém a função original db_filter do Odoo
db_filter_org = http.db_filter


def db_filter(dbs, host=None):
    # Primeiro, aplica o filtro original do Odoo
    dbs = db_filter_org(dbs, host)

    # Em vez de ler um cabeçalho customizado, lemos o host diretamente da requisição.
    # O Traefik já encaminha isso corretamente.
    httprequest = http.request.httprequest
    db_filter_hdr = httprequest.host

    if db_filter_hdr:
        # Remove a porta do host, se houver (ex: meusite.com:443 -> meusite.com)
        db_filter_hdr = db_filter_hdr.split(':')[0]

        _logger.info(f"Filtering database based on host: {db_filter_hdr}")

        # Se o cabeçalho for recebido (deve ser o hostname completo, ex: seudominio.com.br)
        # Formata o nome do host para corresponder ao nome do banco de dados (ex: seudominio_com_br)
        # Remove "www." se presente, e substitui todos os pontos por sublinhados
        # Certifica-se de que a string está em minúsculas para consistência
        formatted_db_name_regex = db_filter_hdr.lower().replace('www.', '').replace('.', '_')
        
        # Constrói a expressão regular para buscar o banco de dados
        # Usamos ^ e $ para garantir uma correspondência exata
        final_db_regex = f"^{formatted_db_name_regex}$"
        _logger.info(f"Formatted database name regex: {final_db_regex}")

        # Filtra os bancos de dados disponíveis com a nova expressão regular
        # dbs_available = list(dbs) # Para debug, se quiser ver os dbs antes do filtro
        dbs = [db for db in dbs if re.match(final_db_regex, db)]
        
        if not dbs:
            _logger.warning(
                f"No database found matching the formatted filter: '{final_db_regex}'. "
                f"Header value was: '{db_filter_hdr}'. "
                f"Available databases (before this filter): {', '.join(dbs_available if 'dbs_available' in locals() else ['N/A'])}" # type: ignore
            )
    return dbs


# Aplica o monkey patch apenas se proxy_mode estiver ativado e o módulo estiver nos server_wide_modules
# ATENÇÃO: O nome do módulo abaixo deve corresponder ao 'name' em __manifest__.py
if config.get("proxy_mode") and "dbfilter_header_traefik" in config.get(
    "server_wide_modules"
):
    _logger.info("Monkey patching http.db_filter for dbfilter_header_traefik")
    http.db_filter = db_filter

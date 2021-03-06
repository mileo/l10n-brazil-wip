# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia - Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#


from __future__ import division, print_function, unicode_literals

import logging
_logger = logging.getLogger(__name__)

try:
    from pybrasil.valor import formata_valor

except (ImportError, IOError) as err:
    _logger.debug(err)

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
from ..constante_tributaria import *


class AliquotaPISCOFINS(models.Model):
    _description = 'Alíquota do PIS-COFINS'
    _name = 'sped.aliquota.pis.cofins'
    _rec_name = 'descricao'
    _order = 'al_pis, al_cofins'

    al_pis = fields.Float('Alíquota do PIS', required=True, digits=(5, 2))
    al_cofins = fields.Float('Alíquota da COFINS', required=True, digits=(5, 2))
    md_pis_cofins = fields.Selection(MODALIDADE_BASE_PIS, 'Modalidade da base de cálculo', required=True,
                                     default=MODALIDADE_BASE_PIS_ALIQUOTA)
    cst_pis_cofins_entrada = fields.Selection(ST_PIS_ENTRADA, 'Situação tributária nas entradas', required=True,
                                              default=ST_PIS_CRED_EXCL_TRIB_MERC_INTERNO)
    cst_pis_cofins_saida = fields.Selection(ST_PIS_SAIDA, 'Situação tributária nas saída', required=True,
                                            default=ST_PIS_TRIB_NORMAL)
    codigo_justificativa = fields.Char('Código da justificativa', size=10)
    descricao = fields.Char(string='Alíquota do PIS-COFINS', compute='_compute_descricao', store=True)

    @api.depends('al_pis', 'al_cofins', 'md_pis_cofins', 'cst_pis_cofins_entrada', 'cst_pis_cofins_saida',
                 'codigo_justificativa')
    def _compute_descricao(self):
        for al_pis_cofins in self:
            if al_pis_cofins.al_pis == -1:
                al_pis_cofins.descricao = 'Não tributado'
            else:
                if al_pis_cofins.md_pis_cofins == MODALIDADE_BASE_PIS_ALIQUOTA:
                    al_pis_cofins.descricao = 'PIS ' + formata_valor(al_pis_cofins.al_pis or 0) + '%'
                    al_pis_cofins.descricao += '; COFINS ' + formata_valor(al_pis_cofins.al_cofins or 0) + '%'

                elif al_pis_cofins.md_pis_cofins == MODALIDADE_BASE_PIS_QUANTIDADE:
                    al_pis_cofins.descricao = 'por quantidade, PIS a R$ ' + formata_valor(al_pis_cofins.al_pis)
                    al_pis_cofins.descricao += '; COFINS a R$ ' + formata_valor(al_pis_cofins.al_cofins)

                al_pis_cofins.descricao += ' - CST ' + al_pis_cofins.cst_pis_cofins_entrada
                al_pis_cofins.descricao += ' entrada, ' + al_pis_cofins.cst_pis_cofins_saida
                al_pis_cofins.descricao += ' saída'

                if al_pis_cofins.codigo_justificativa:
                    al_pis_cofins.descricao += ' - justificativa '
                    al_pis_cofins.descricao += al_pis_cofins.codigo_justificativa

    @api.depends('al_pis', 'al_cofins', 'md_pis_cofins', 'cst_pis_cofins_entrada', 'cst_pis_cofins_saida',
                 'codigo_justificativa')
    def _check_al_pis(self):
        for al_pis_cofins in self:
            busca = [
                ('al_pis', '=', al_pis_cofins.al_pis),
                ('al_cofins', '=', al_pis_cofins.al_cofins),
                ('md_pis_cofins', '=', al_pis_cofins.md_pis_cofins),
                ('cst_pis_cofins_entrada', '=', al_pis_cofins.cst_pis_cofins_entrada),
                ('cst_pis_cofins_saida', '=', al_pis_cofins.cst_pis_cofins_saida),
                ('codigo_justificativa', '=', al_pis_cofins.codigo_justificativa),
            ]

            if al_pis_cofins.id or al_pis_cofins._origin.id:
                busca.append(('id', '!=', al_pis_cofins.id or al_pis_cofins._origin.id))

            al_pis_cofins_ids = self.search(busca)

            if al_pis_cofins_ids:
                raise ValidationError('Alíquotas de PIS e COFINS já existem!')

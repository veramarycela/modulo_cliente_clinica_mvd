# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import re
import logging
_logger = logging.getLogger(__name__)

class Clientes(models.Model):
     _name = 'clinica.cliente'
     _description ='clinica.cliente'
     identification  = fields.Char("Cedula")
     name = fields.Char("Nombre")     
     phone = fields.Char("Telefono")
     direccion = fields.Char("Dirección")
     gender = fields.Selection(selection=[("femenino", "Femenino"), ("masculino","Masculino")])
     aseguradora = fields.Many2one("res.partner")          


     @api.constrains('identification')
     def _check_identification_format(self):
        for record in self:
            if record.identification:
                pattern = re.compile(r"^(V|E)-\d{1,9}$")
                if not pattern.match(record.identification):
                    raise UserError("Formato de cédula inválido. Debe ser V-123456789 o E-123456789.")


class Facturas(models.Model):
    _name='account.move'
    _inherit = 'account.move'

      
    x_id_paciente_clinica = fields.Many2one("clinica.cliente")
    
    direccion_ci_paciente = fields.Char(compute="_compute_direccion_ci_paciente", store=True)

    x_clinica_total_dolares = fields.Float(compute='_dolarizar_total', store=True)

    x_clinica_tasa_dolar = fields.Float(compute='_compute_tasa_dolar', store=True, string='Tasa de Cambio USD')

    @api.depends('date', 'currency_id')
    def _compute_tasa_dolar(self):
        for move in self:
            if move.currency_id and move.currency_id.id != self.env.ref('base.USD').id:
                # Buscar la tasa de cambio para la moneda de la factura (currency_id) en res.currency.rate
                currency_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', 2),
                    ('name', '=', move.date),  # Puedes ajustar esto según tus necesidades
                ], limit=1)

                if currency_rate:
                    # Almacenar el valor de la tasa de cambio en el campo x_clinica_tasa_dolar
                    move.x_clinica_tasa_dolar = currency_rate.rate
                else:
                    # Si no se encuentra una tasa de cambio, dejar x_clinica_tasa_dolar como 0.0
                    move.x_clinica_tasa_dolar = 0.0
            else:
                # Si la moneda es USD, x_clinica_tasa_dolar es igual a 1.0
                move.x_clinica_tasa_dolar = 1.0

    @api.depends('amount_total', 'currency_id')
    def _dolarizar_total(self):
        for record in self:
            if record.currency_id and record.currency_id.id != self.env.ref('base.USD').id:
                # Buscar el tipo de cambio para la moneda de la factura (currency_id) en res.currency.rate
                currency_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', 2),
                    ('name', '<=', record.date),  # Puedes ajustar esto según tus necesidades
                ], order='name desc', limit=1)
                print(record.date)
                if currency_rate:
                    # Calcular el total en dólares usando el tipo de cambio y amount_total
                    record.x_clinica_total_dolares = record.amount_total / currency_rate.rate
                else:
                    # Si no se encuentra un tipo de cambio, dejar x_clinica_total_dolares como 0.0
                    record.x_clinica_total_dolares = 0.0
            else:
                # Si la moneda es USD, x_clinica_total_dolares es igual a amount_total
                record.x_clinica_total_dolares = record.amount_total

    @api.depends('x_id_paciente_clinica')
    def _compute_direccion_ci_paciente(self):
        for record in self:
            if record.x_id_paciente_clinica:
                direccion = record.x_id_paciente_clinica.direccion
                identificacion = record.x_id_paciente_clinica.identification
                record.direccion_ci_paciente = f"{direccion} {identificacion}"
            else:
                record.direccion_ci_paciente = ''
    

class DetalleFactura(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    x_clinica_precio_dolares = fields.Float(compute='_dolarizar', store=True)
    x_clinica_subtotal_dolares = fields.Float(compute='_dolarizar_subtotal', store=True)
    
    @api.depends('price_unit', 'currency_id')
    def _dolarizar(self):
        for record in self:
            if record.currency_id and record.currency_id.id != self.env.ref('base.USD').id:
                # Buscar el tipo de cambio para la moneda de la factura (currency_id) en res.currency.rate
                currency_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', 2),
                    ('name', '<=', record.move_id.date),  # Puedes ajustar esto según tus necesidades
                ], order='name desc', limit=1)
                print(record.move_id.date)
                print(record.currency_id.id)
                if currency_rate:
                    # Calcular el precio en dólares usando el tipo de cambio y price_unit
                    record.x_clinica_precio_dolares = record.price_unit / currency_rate.rate
                    print(currency_rate)
                else:
                    # Si no se encuentra un tipo de cambio, dejar x_clinica_precio_dolares como 0.0
                    record.x_clinica_precio_dolares = 0.0
            else:
                # Si la moneda es USD, x_clinica_precio_dolares es igual a price_unit
                record.x_clinica_precio_dolares = record.price_unit
    
    @api.depends('price_subtotal', 'currency_id')
    def _dolarizar_subtotal(self):
        for record in self:
            if record.currency_id and record.currency_id.id != self.env.ref('base.USD').id:
                # Buscar el tipo de cambio para la moneda de la factura (currency_id) en res.currency.rate
                currency_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', 2),
                    ('name', '<=', record.move_id.date), #Puedes ajustar esto según tus necesidades
                ], order='name desc', limit=1)

                if currency_rate:
                    # Calcular el subtotal en dólares usando el tipo de cambio y price_subtotal
                    record.x_clinica_subtotal_dolares = record.price_subtotal / currency_rate.rate                    
                else:
                    # Si no se encuentra un tipo de cambio, dejar x_clinica_subtotal_dolares como 0.0
                    record.x_clinica_subtotal_dolares = 0.0
            else:
                # Si la moneda es USD, x_clinica_subtotal_dolares es igual a price_subtotal
                record.x_clinica_subtotal_dolares = record.price_subtotal
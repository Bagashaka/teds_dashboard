# -*- coding: utf-8 -*-
from openerp import models, fields, api

class DashboardReportPenjualan(models.Model):
    _name = 'dashboard.report.penjualan'

    branch_code = fields.Char()
    branch_name = fields.Char()
    qty = fields.Float()
    nett_sales = fields.Float()
    categ_name = fields.Char()

    @api.model
    def get_sales_data(self, start_date, end_date):
        query = """
            SELECT 
                b.code as branch_code, 
                b.name as branch_name, 
                sol.product_uom_qty as qty,
                sol.price_unit * (1 - COALESCE(sol.discount, 0) / 100) / (1 + COALESCE(tax.amount, 0)) * sol.product_uom_qty as nett_sales,
                COALESCE(prod_category.name, '') as categ_name
            FROM sale_order so
                INNER JOIN sale_order_line sol on so.id = sol.order_id
                LEFT JOIN sale_order_tax as dsot on dsot.order_line_id = sol.id
                LEFT JOIN account_tax as tax on tax.id = dsot.tax_id
                LEFT JOIN wtc_branch b on so.branch_id = b.id
                LEFT JOIN product_product product on sol.product_id = product.id
                LEFT JOIN product_template prod_template ON product.product_tmpl_id = prod_template.id
                LEFT JOIN product_category prod_category ON prod_template.categ_id = prod_category.id
            WHERE so.date_order >= %s AND so.date_order <= %s AND b.code = 'MML'
        """
        self.env.cr.execute(query, (start_date, end_date))
        result = self.env.cr.dictfetchall()
        return result
    
    @api.model
    def get_sales_no_date(self):
        query = """
            SELECT 
                b.code as branch_code, 
                b.name as branch_name, 
                sol.product_uom_qty as qty,
                sol.price_unit * (1 - COALESCE(sol.discount, 0) / 100) / (1 + COALESCE(tax.amount, 0)) * sol.product_uom_qty as nett_sales,
                COALESCE(prod_category.name, '') as categ_name
            FROM sale_order so
                INNER JOIN sale_order_line sol on so.id = sol.order_id
                LEFT JOIN sale_order_tax as dsot on dsot.order_line_id = sol.id
                LEFT JOIN account_tax as tax on tax.id = dsot.tax_id
                LEFT JOIN wtc_branch b on so.branch_id = b.id
                LEFT JOIN product_product product on sol.product_id = product.id
                LEFT JOIN product_template prod_template ON product.product_tmpl_id = prod_template.id
                LEFT JOIN product_category prod_category ON prod_template.categ_id = prod_category.id
            WHERE b.code = 'MML'
        """
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        return result

# This file is part of sale_payment_type_cost module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta


__all__ = ['Sale', 'SaleLine']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    @classmethod
    def quote(cls, sales):
        pool = Pool()
        Line = pool.get('sale.line')

        super(Sale, cls).quote(sales)

        for sale in sales:
            if sale.payment_type and sale.payment_type.has_cost:
                lines = Line.search([
                        ('sale', '=', sale),
                        ('product', '=', sale.payment_type.cost_product),
                        ])
                if lines:
                    Line.delete(lines)
                line = Line()
                line.sale = sale
                line.update_payment_type_cost_line()
                line.save()


class SaleLine:
    __name__ = 'sale.line'

    def update_payment_type_cost_line(self):
        pool = Pool()
        Line = pool.get('sale.line')
        for key, value in Line.default_get(Line._fields.keys(),
                with_rec_name=False).iteritems():
            if value is not None:
                setattr(self, key, value)
        self.quantity = 1
        self.product = self.sale.payment_type.cost_product
        for key, value in self.on_change_product().iteritems():
            if 'rec_name' in key:
                continue
            setattr(self, key, value)
        self.unit_price = (self.sale.total_amount *
            self.sale.payment_type.cost_percent)
        return self

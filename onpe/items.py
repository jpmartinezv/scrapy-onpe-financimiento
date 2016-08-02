# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OnpeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class AporteItem(scrapy.Item):
    tipo = scrapy.Field()
    ruc = scrapy.Field()
    anio = scrapy.Field()
    periodo = scrapy.Field()
    tipoOrganizacion = scrapy.Field()
    partido = scrapy.Field()
    fecha = scrapy.Field()
    procesoElectoral = scrapy.Field()
    apellidoPaterno = scrapy.Field()
    apellidoMaterno= scrapy.Field()
    nombres = scrapy.Field()
    tipoDoc = scrapy.Field()
    numDoc = scrapy.Field()
    tipoAporte = scrapy.Field()
    naturaleza = scrapy.Field()
    importe = scrapy.Field()

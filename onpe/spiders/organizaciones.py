# -*- coding: utf-8 -*-
import scrapy
from onpe.items import AporteItem
import re
import pymongo

client = pymongo.MongoClient()
db = client.onpe
collection = db.personasJuridicas

TIPO_ORGANIZACION = ["PARTIDO POLITICO", "ALIANZA ELECTORAL", "MOVIMIENTO REGIONAL", "ORGANIZACION POLITICA PROVINCIAL", "ORGANIZACION POLITICA DISTRITAL"]

class OrganizacionesSpider(scrapy.Spider):
    name = "organizaciones"
    allowed_domains = []


    def start_requests(self):
        page_url = 'https://www.onpe.gob.pe/loadSelect/'

        for tipo in range(1, 6):

            params = {
                'vType': 'aportes',
                'vValu': str(tipo),
            }

            meta = {
                'tipoOrganizacion': TIPO_ORGANIZACION[tipo - 1],
            }

            yield scrapy.FormRequest(url=page_url, formdata=params, meta=meta,
                callback=self.load_select_request)

    def load_select_request(self, response):

        page_url = 'https://www.onpe.gob.pe/loadDetail/'

        options = response.xpath("//option")

        for option in options:

            if(option.xpath('@value').extract_first()):
                print(option.xpath('@value').extract_first())
                obj = {
                    'id':  int(option.xpath('@value').extract_first()),
                    'tipoDoc': "RUC",
                    'numDoc':  str(option.xpath('@value').extract_first()),
                    'razonSocial': option.xpath('./text()').extract_first(),
                    'tipoOrg': "Organización Política",
                    'tipoOrgPol': response.meta['tipoOrganizacion'],
                }
                collection.update({'id': int(option.xpath('@value').extract_first())}, obj, upsert=True)

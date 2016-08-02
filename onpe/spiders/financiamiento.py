# -*- coding: utf-8 -*-
import scrapy
from onpe.items import AporteItem
import re
import pymongo

client = pymongo.MongoClient()
db = client.onpe
collection = db.aportantes

class FinanciamientoSpider(scrapy.Spider):
    name = "financiamiento"
    allowed_domains = []

    TIPO_ORGANIZACION = ["PARTIDO POLITICO", "ALIANZA ELECTORAL", "MOVIMIENTO REGIONAL", "ORGANIZACION POLITICA PROVINCIAL", "ORGANIZACION POLITICA DISTRITAL"]

    def start_requests(self):
        page_url = 'https://www.onpe.gob.pe/loadSelect/'

        for tipo in range(1, 5):

            params = {
                'vType': 'aportes',
                'vValu': str(tipo),
            }

            print(str(params))

            meta = {
                'tipoOrganizacion': str(tipo),
            }

            yield scrapy.FormRequest(url=page_url, formdata=params, meta=meta,
                callback=self.load_select_request)

    def load_select_request(self, response):

        page_url = 'https://www.onpe.gob.pe/loadDetail/'

        options = response.xpath("//option")

        for option in options:

            params = {
                'txtID': 'PorOrgPolitica',
                'cboTipo': response.meta['tipoOrganizacion'],
                'cboOrga': str(option.xpath('@value').extract_first()),
            }

            meta = {
                'tipoOrganizacion': response.meta['tipoOrganizacion'],
                'partido' : option.xpath('./text()').extract_first(),
            }

            yield scrapy.FormRequest(url=page_url, formdata=params, meta=meta,
                callback=self.load_detail_request)

    def load_detail_request(self, response):

        page_url = 'https://www.onpe.gob.pe/loadDetailAll/'

        rows = response.xpath("//tr")

        for row in rows:
            tds = row.xpath('./td')
            if len(tds) == 4 and tds[3].xpath('./a/@href') :
                href = tds[3].xpath('./a/@href').extract_first()
                if href.startswith('javascript:verDetalleAportesCampaniaOrg'):

                    plist = re.search(r'javascript:verDetalleAportesCampaniaOrg\((.*)\)', href).group(1)
                    plist = plist.replace('\'', '').replace(' ', '').split(',')

                    params = {
                        'txtID': 'aporCampElec',
                        'ruc': str(plist[0]),
                        'ani': str(plist[1]),
                        'per': str(plist[2]),
                        'pag': '1',
                    }

                    meta = {
                        'txtID': 'aporCampElec',
                        'ruc': str(plist[0]),
                        'ani': str(plist[1]),
                        'per': str(plist[2]),
                        'pag': '1',
                        'tipoOrganizacion': response.meta['tipoOrganizacion'],
                        'partido': response.meta['partido'],
                    }

                    yield scrapy.FormRequest(url=page_url, formdata=params, meta=meta,
                        callback=self.make_detail_all_request)

                elif href.startswith('javascript:verDetalleAportesSemestralOrg'):

                    plist = re.search(r'javascript:verDetalleAportesSemestralOrg\((.*)\)', href).group(1)
                    plist = plist.replace('\'', '').replace(' ', '').split(',')

                    params = {
                        'txtID': 'aporSemesOrg',
                        'ruc': str(plist[0]),
                        'ani': str(plist[1]),
                        'per': str(plist[2]),
                        'pag': '1',
                    }

                    meta = {
                        'txtID': 'aporSemesOrg',
                        'ruc': str(plist[0]),
                        'ani': str(plist[1]),
                        'per': str(plist[2]),
                        'pag': '1',
                        'tipoOrganizacion': response.meta['tipoOrganizacion'],
                        'partido': response.meta['partido'],
                    }

                    yield scrapy.FormRequest(url=page_url, formdata=params, meta=meta,
                        callback=self.make_detail_all_request)

    def make_detail_all_request(self, response):

        page_url = 'https://www.web.onpe.gob.pe/loadDetailAll/'

        number_of_pages = response.xpath("//input[@id = 'total']/@value")
        number_of_pages = int(number_of_pages.extract_first())

        for pag in range(1, number_of_pages + 1):

            params = {
                'txtID': response.meta['txtID'],
                'ruc': response.meta['ruc'],
                'ani': response.meta['ani'],
                'per': response.meta['per'],
                'pag': str(pag),
            }

            meta = {
                'txtID': response.meta['txtID'],
                'ruc': response.meta['ruc'],
                'ani': response.meta['ani'],
                'per': response.meta['per'],
                'pag': str(pag),
                'tipoOrganizacion': response.meta['tipoOrganizacion'],
                'partido': response.meta['partido'],
            }

            yield scrapy.FormRequest(url=page_url, formdata=params, meta=meta,
                callback=self.load_detail_all_request)

    def load_detail_all_request(self, response):

        trs = response.xpath("//table[@class = 'display dtable06 tabla99']//tr")

        for tr in trs:

            tds = tr.xpath('./td')
            nf = len(tds)

            item = {}

            item['tipo'] = response.meta['txtID']
            item['ruc'] = response.meta['ruc']
            item['anio'] = response.meta['ani']
            item['periodo'] = response.meta['per']
            item['tipoOrganizacion'] = response.meta['tipoOrganizacion']
            item['partido'] = response.meta['partido']

            if response.meta['txtID'] == 'aporCampElec':
                if nf == 10:

                    item['fecha'] = tds[0].xpath('./text()').extract_first()
                    item['procesoElectoral'] = tds[1].xpath('./text()').extract_first()
                    item['apellidoPaterno'] = tds[2].xpath('./text()').extract_first()
                    item['apellidoMaterno'] = tds[3].xpath('./text()').extract_first()
                    item['nombres'] = tds[4].xpath('./text()').extract_first()
                    item['tipoDoc'] = tds[5].xpath('./text()').extract_first()
                    item['numDoc'] = tds[6].xpath('./text()').extract_first()
                    item['tipoAporte'] = tds[7].xpath('./text()').extract_first()
                    item['naturaleza'] = tds[8].xpath('./text()').extract_first()
                    item['importe'] = tds[9].xpath('./text()').extract_first()

                elif nf == 8:

                    item['fecha'] = tds[0].xpath('./text()').extract_first()
                    item['procesoElectoral'] = tds[1].xpath('./text()').extract_first()
                    item['apellidoPaterno'] = tds[2].xpath('./text()').extract_first()
                    item['tipoDoc'] = tds[3].xpath('./text()').extract_first()
                    item['numDoc'] = tds[4].xpath('./text()').extract_first()
                    item['tipoAporte'] = tds[5].xpath('./text()').extract_first()
                    item['naturaleza'] = tds[6].xpath('./text()').extract_first()
                    item['importe'] = tds[7].xpath('./text()').extract_first()
            else:
                if nf == 9:

                    item['fecha'] = tds[0].xpath('./text()').extract_first()
                    item['apellidoPaterno'] = tds[1].xpath('./text()').extract_first()
                    item['apellidoMaterno'] = tds[2].xpath('./text()').extract_first()
                    item['nombres'] = tds[3].xpath('./text()').extract_first()
                    item['tipoDoc'] = tds[4].xpath('./text()').extract_first()
                    item['numDoc'] = tds[5].xpath('./text()').extract_first()
                    item['tipoAporte'] = tds[6].xpath('./text()').extract_first()
                    item['naturaleza'] = tds[7].xpath('./text()').extract_first()
                    item['importe'] = tds[8].xpath('./text()').extract_first()

                elif nf == 7:

                    item['fecha'] = tds[0].xpath('./text()').extract_first()
                    item['apellidoPaterno'] = tds[1].xpath('./text()').extract_first()
                    item['tipoDoc'] = tds[2].xpath('./text()').extract_first()
                    item['numDoc'] = tds[3].xpath('./text()').extract_first()
                    item['tipoAporte'] = tds[4].xpath('./text()').extract_first()
                    item['naturaleza'] = tds[5].xpath('./text()').extract_first()
                    item['importe'] = tds[6].xpath('./text()').extract_first()

            if 6 < nf and nf < 11:
                collection.insert(item)

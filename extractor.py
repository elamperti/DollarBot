#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from datetime import date
import requests
from urllib import request, parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv('.env.local' if (os.path.isfile('.env.local')) else '.env')

regex_dolar = re.compile('(\d+)[.,](\d+)')
dolar_values = {}


def parse_dolar(val):
    groups = regex_dolar.search(val)
    if (not groups):
        return False
    else:
        dolar = float(groups[1] + '.' + groups[2])
        return dolar

def get_santander():
    with request.urlopen('https://banco.santanderrio.com.ar/exec/cotizacion/index.jsp') as rq:
        soup = BeautifulSoup(rq.read(), 'html.parser')
        tmp = soup.find('td', string = 'Dólar').find_next_siblings()[1].string
        return parse_dolar(tmp)

def get_nacion_historico(): # not tested
    today = '{d.day}/{d.month}/{d.year}'.format(d = date.today())
    with request.urlopen('http://www.bna.com.ar/Cotizador/HistoricoPrincipales?id=billetes&FiltroDolar=1&fecha=' + today) as rq:
        soup = BeautifulSoup(rq.read(), 'html.parser')
        hits = soup.find('table', 'cotizador').find_all('td', string = 'Dolar U.S.A')
        for hit in hits:
            siblings = hit.find_next_siblings()
            if (siblings[2].string == str(today)):
                return parse_dolar(siblings[1].string)

def get_nacion():
    rq = requests.get('http://www.bna.com.ar/Personas/')
    soup = BeautifulSoup(rq.text, 'html.parser')
    tmp = soup.find('table', 'cotizacion').find('td', string = 'Dolar U.S.A').find_next_siblings()[1].string
    return parse_dolar(tmp)

def get_bbva():
    with request.urlopen('https://hb.bbv.com.ar/fnet/mod/inversiones/NL-dolareuro.jsp') as rq:
        soup = BeautifulSoup(rq.read(), 'html.parser')
        tmp = soup.find('td', string = 'Dolar').find_next_siblings()[1].string
        return parse_dolar(tmp)

def get_bolsa():
    url = 'https://www.invertironline.com/mercado/cotizaciones?pais=Argentina&instrumento=Monedas&panel=Principales%20divisas&actualizar=true'
    with request.urlopen(url) as rq:
        soup = BeautifulSoup(rq.read(), 'html.parser')
        dolar = soup.find('table', id='cotizaciones').find('strong', string='Dolar Bolsa (AO20D)').parent.find_next_siblings()[1].string
        # euro = soup.find('table', id='cotizaciones').find('strong', string='Euros').parent.find_next_siblings()[1].string
        return parse_dolar(dolar)

def get_galicia():
    url = 'https://www.bancogalicia.com/cotizacion/cotizar?currencyId=02&quoteType=SU&quoteId=999'
    rs = json.loads(request.urlopen(url).read())
    return parse_dolar(rs['sell'])

def get_patagonia():
    with request.urlopen('https://ebankpersonas.bancopatagonia.com.ar/eBanking/usuarios/cotizacionMonedaExtranjera.htm') as rq:
        soup = BeautifulSoup(rq.read(), 'html.parser')
        tmp = soup.find('td', string='DOLARES').find_next_siblings()[1].string
        return parse_dolar(tmp)


bancos = [
    ('santander', get_santander),
    ('nacion', get_nacion),
    ('bbva', get_bbva),
    ('bolsa', get_bolsa),
    ('galicia', get_galicia),
    ('patagonia', get_patagonia),
]

def dolar_average():
    sum_values = 0
    for banco, getter in bancos: 
        try:
            value = getter()
            sum_values += value
            dolar_values[banco] = value
            print('Dolar {nombre}: $ {value}'.format(nombre=banco, value=value))
        except:
            print('Error obteniendo {nombre}'.format(nombre=banco))

    if (sum_values > 0):
        promedio = sum_values / len(dolar_values)
        print('Promedio: $ {prom}'.format(prom=str(promedio)))
        return promedio
    else:
        return False
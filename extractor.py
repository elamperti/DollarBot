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
    match = regex_dolar.search(val)
    if (not match):
        return False
    else:
        dolar = float(match.group(1) + '.' + match.group(2))
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
    rs = json.loads(requests.get(url).text)
    return parse_dolar(rs['sell'])

def get_patagonia():
    with request.urlopen('https://ebankpersonas.bancopatagonia.com.ar/eBanking/usuarios/cotizacionMonedaExtranjera.htm') as rq:
        soup = BeautifulSoup(rq.read(), 'html.parser')
        tmp = soup.find('td', string='DOLARES').find_next_siblings()[1].string
        return parse_dolar(tmp)


bancos = [
    ('santander', 'Banco Santander', get_santander, re.compile('santander|rio', flags=re.IGNORECASE)),
    ('nacion', 'Banco Nación', get_nacion, re.compile('naci[oó]n|bna', flags=re.IGNORECASE)),
    ('frances', 'Banco Francés', get_bbva, re.compile('franc[eé]s|bbva?', flags=re.IGNORECASE)),
    ('bolsa', 'Bolsa', get_bolsa, re.compile('bolsa|bonar', flags=re.IGNORECASE)),
    ('galicia', 'Banco Galicia', get_galicia, re.compile('galicia', flags=re.IGNORECASE)),
    ('patagonia', 'Banco Patagonia', get_patagonia, re.compile('patagonia|bp', flags=re.IGNORECASE)),
]

def detailed_list():
    message = '```'
    for ugly_name, banco, getter, alias in bancos: 
        try:
            value = getter()
            message += "\n{}: ${:,.2f}".format(banco, value)
        except:
            print('Error obteniendo {nombre}'.format(nombre=banco))
    if (len(message) == 3):
        message += "\nNo se pudo obtener ningún valor"
    message += "\n```"
    return message

def dolar_average():
    sum_values = 0
    for ugly_name, banco, getter, alias in bancos: 
        try:
            value = getter()
            if value and value > 0:
                sum_values += value
                dolar_values[ugly_name] = value
            # print('Dólar {nombre}: $ {value}'.format(nombre=banco, value=value))
        except:
            print('Error obteniendo {nombre}'.format(nombre=banco))

    if (sum_values > 0):
        promedio = sum_values / len(dolar_values)
        # print('Promedio: $ {prom}'.format(prom=str(promedio)))
        return promedio
    else:
        return False

def get_one(name):
    for ugly_name, banco, getter, alias in bancos:
        matches = alias.match(name)
        if (matches):
            value = getter()
            if value:
                return ':bank: {}: ${:,.2f}'.format(banco, value)
            else:
                return ':x: No se pudo obtener un valor para {nombre}'.format(banco)
    return ':grey_question: Banco desconocido'

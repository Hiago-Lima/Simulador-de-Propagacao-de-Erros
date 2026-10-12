"""
erros.py  |  Raioni Felix

Cálculo dos erros e função central calcular(), que junta tudo.
Usa as funções do nucleo.py .
"""

from dataclasses import dataclass
from decimal import Decimal

import nucleo


@dataclass
class Resultado:
    """Guarda em um objeto todas as informações necessarias para 
    que o usuario identifique os valores aproximados, reais e 
    erro de maquina(bin)
    ."""
    x: Decimal
    y: Decimal
    op: str
    n: int
    metodo: str
    exato: Decimal
    aproximado: Decimal
    erro_abs: Decimal
    erro_rel: Decimal | None   # None quando o valor aproximado é 0


def erro_absoluto(exato, aprox):
    # Ea = |exato - aprox|
    return abs(exato-aprox)

def erro_relativo(exato, aprox):
   # Er = |exato - aprox|/|aprox|
    if aprox == 0:
        return None
    return abs(exato-aprox)/abs(aprox)



def calcular(x, y, op, n, metodo, aproximar_entradas=False):

    #Calcula tudo que a operação precisa e armazena no objeto Resultado

    exato=nucleo.operar_exato(x,y,op)
    aproximado=nucleo.operar_aproximado(x,y,op,n,metodo,aproximar_entradas)
    erro_abs=erro_absoluto(exato,aproximado)
    erro_rel=erro_relativo(exato,aproximado)

    return Resultado(x,y,op,n,metodo,exato,aproximado,erro_abs,erro_rel)



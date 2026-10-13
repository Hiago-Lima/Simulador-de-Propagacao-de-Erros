"""
nucleo.py | Arthur Lincoln (Pessoa 1)
AVISO:
REQUER PYTHON 3.10+ (match case)


Motor do simulador, tem normalização, truncamento,
arredondamento e as quatro operações básicas

Regras (Do md):
-Todo numero é Decimal (criar com texto: Decimal("0.1"))
-n = numero de dígitos significativos
-Arredondamento: 0.5 para cima, truncamento: descarta
"""


#Decimal é o numero exato sem erro de soma de float
# Round_Down corta oq sobra -> Truncamento
# Round_Half_Up arredonda 0.5 para cima -> Arredondamento
#N dá pra usar o round() do py pq arredonda o meio para o par
from decimal import Decimal, getcontext, ROUND_DOWN, ROUND_HALF_UP


#Precisão usada pro valor exato
#as contas do decimal respeitam esse valor
PRECISAO_MAXIMA = 50
getcontext().prec = PRECISAO_MAXIMA

#tuplas pra manter a ordem ao mostrar no menu
OPERACOES_VALIDAS = ("+", "-", "*", "/")
METODOS_VALIDOS = ("truncamento", "arredondamento")

#Como interpretar o n em truncar() e arredondar():
#"significativos" -> n digitos significativos (como diz o texto do enunciado), eh o padrao
#"casas" -> n casas decimais (como mostram os passos do Exemplo 3)
#IMPORTANTE:
#Pra mudar de fora: nucleo.MODO_PRECISAO = "casas" / "significativos"
MODOS_PRECISAO_VALIDOS = ("significativos", "casas")
MODO_PRECISAO = "significativos"


def normalizar(valor):
    """
    Coloca em notação científica normalizada 0.1 <= |mantissa| < 1

    ex: 123.45 -> (Decimal("0.12345"), 3) pq 123.45 = 0.12345 * 10^3
    Caso de exceção: 0 -> (Decimal("0"), 0)

    Retorna uma tupla (mantissa, expoente)
    """
    if valor == 0:
        return (Decimal("0"), 0)

    #adjusted() dá o expoente da forma 1.xxx x 10^e (123.45 -> 2
    #pq 1.2345 x 10^2 = 123.45)
    #Na forma 0.xxx x 10^e, o expoente é +1
    expoente = valor.adjusted() + 1

    #scaleb(k) multiplica por 10^k.
    #Multiplicar por 10^-expoente empurra a virgula pra frente do
    #primeiro dígito: 123.45 * 10^-3 = 0.12345
    #O sinal acompanha a mantissa (-123.45 * 10^-3 = -0.12345)
    mantissa = valor.scaleb(-expoente)
    return (mantissa, expoente)

def _reduzir(valor, n, modo):
    """
    Func auxiliar (o "_" avisa que é de uso interno):
    mantem n digitos significativos ou casas decimais dependendo do MODO_PRECISAO usando o modo de arredondamento
    recebido
    truncar() e arredondar() só mudam o modo
    """
    if valor ==0:
        return Decimal("0")

    #passo = valor da ultima casa que fica
    if MODO_PRECISAO == "casas":
        #n casas decimais: passo = 10^-n, independe do tamanho do numero
        #Ex: 1.13572 n=4 -> passo = 10^-4 = 0.0001 -> 1.1357
        passo = Decimal(1).scaleb(-n)
    elif MODO_PRECISAO == "significativos":
        #O expoente diz onde esta a virgula em relação aos dígitos
        _, expoente = normalizar(valor)

        #n digitos significativos: passo = 10^(expoente - n)
        #Ex: 123.45 n=4 -> expoente=3 -> passo = 10^(3-4) = 10^-1 = 0.1
        #Ex: 0.012345 n=4 -> expoente=-1 -> passo = 10^(-1-4) = 10^-5 = 0.00001
        #Ex: 1.13572 n=4 -> expoente=1 -> passo = 10^-3 -> 1.135
        passo = Decimal(1).scaleb(expoente - n)
    else:
        raise ValueError(f"Modo de precisão inválido: {MODO_PRECISAO!r}. "
                         f"Use 'significativos' ou 'casas'.")

    #quantize força o num  ter exatamente a precisão do passo
    #cortando ou arredondando conforme o modo
    return  valor.quantize(passo, rounding=modo)

def truncar(valor, n):
    """
    Mantem n digitos (conforme o MODO_PRECISAO) CORTANDO o resto, sem arredondar

    ex: truncar(Decimal("123.456"), 4) -> Decimal("123.4")
    """
    return _reduzir(valor, n, ROUND_DOWN)

def arredondar(valor, n):
    """
    Mantem n digitos (conforme o MODO_PRECISAO) ARREDONDANDO (0.5 pra cima)

    ex: arredondar(Decimal("123.456"), 4) -> Decimal("123.5")
        arredondar(Decimal("0.76545"), 4) -> Decimal("0.7655")
    """
    return _reduzir(valor, n, ROUND_HALF_UP)

def ajustar_precisao(valor, n, metodo):
    """
    Escolhe entre truncar ou arredondar conforme o metodo recebido
    metodo invalido -> ValueError
    """
    if metodo == "truncamento":
        return truncar(valor, n)
    elif metodo == "arredondamento":
        return arredondar(valor, n)
    raise ValueError(f"Método inválido: {metodo!r}")

def operar_exato(x, y, op):
    """
    Faz a conta (+, -, *, /) com a precisao maxima (PRECISAO_MAXIMA = 50 digitos)
    divisao por zero -> ZeroDivisionError
    operacao invalida -> ValueError

    ex: operar_exato(Decimal("0.76545"), Decimal("0.76541"), "-") -> Decimal("0.00004")
    """
    #match/case funciona como o switch do C, o "case _" eh o default
    match op:
        case "+":
            return x+y
        case "-":
            return x-y
        case "*":
            return x*y
        case "/":
            if y == 0:
                raise ZeroDivisionError("Divisão por zero")
            return x/y
        case _:
            raise ValueError(f"Operação inválida: {op!r}")

def operar_aproximado(x, y, op, n, metodo, aproximar_entradas=True):
    """
    Faz a operação como a "máquina hipotética" de n dígitos faria.

    Passos:
      1. Se aproximar_entradas for True, reduz x e y para n dígitos.
      2. Faz a operação exata com os valores do passo 1.
      3. Reduz o resultado para n dígitos.

    aproximar_entradas=True  -> Exemplo 2 (cancelamento subtrativo)
    aproximar_entradas=False -> Exemplo 3 (soma sequencial)

    Retorna: Decimal
    """

    #A maquina só enxerga n digitos, inclusive nos dados de entrada
    if aproximar_entradas:
        x = ajustar_precisao(x, n, metodo)
        y = ajustar_precisao(y, n, metodo)
    #A conta em si (com mtos digitos ainda)
    resultado = operar_exato(x, y, op)

    #O resultado final é reduzido pra n digitos
    return ajustar_precisao(resultado, n, metodo)
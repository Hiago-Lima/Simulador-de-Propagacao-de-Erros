"""
main.py  | Raioni Felix

Interface no terminal criada para:
- facilitar a entrada dos dados,
- clareza na apresentação dos resultados,
- opção de fazer novo cálculo ou sair sem reiniciar o programa.

Como executar:  python main.py
"""

from decimal import Decimal, InvalidOperation

import nucleo
from erros import calcular

def ler_numero(mensagem):
    while True:
        entrada = input(mensagem).strip().replace(",", ".") # garante que mesmo se o usuario por espaços ou "," no lugar do ponto o programa funciona
        try:
            valor = Decimal(entrada) #garante que a string vai ser convertida para decimal e trata o erro
        except InvalidOperation:
            print("Valor inválido. Tente novamente (ex: 0.76545 ou 0,76545).")
            continue
        if not valor.is_finite(): #recusa NaN e Infinity, que o Decimal aceita como texto
            print("Valor inválido. Use apenas números (ex: 0.76545 ou 0,76545).")
            continue
        return valor


def ler_operacao():
    while True:
        op = input("Operação (+, -, *, /): ").strip()
        if op in nucleo.OPERACOES_VALIDAS: #executa ser por uma das 4 operações basicas listadas no nucleo.py
            return op
        print(f"Operação inválida. Use uma de: {nucleo.OPERACOES_VALIDAS}")


def ler_n():
    while True: #executa até o numero de digitos significativos ser valido
        try:
            n = int(input("Dígitos significativos (n >= 1): ").strip())
            if n >= 1:
                return n
            print("n deve ser >= 1.")
        except ValueError:
            print("Digite um inteiro válido.")


def ler_metodo(): #escolha do metodo
    while True:
        escolha = input("Método: [1] - truncamento  [2] - arredondamento: ").strip()
        if escolha == "1":
            return "truncamento"
        if escolha == "2":
            return "arredondamento"
        print("Escolha 1 ou 2.")


def formatar(valor): #formata para a notação cientifica os valores de entrada
    mantissa, expoente = nucleo.normalizar(valor)
    return f"{valor}  ({mantissa} x 10^{expoente})"


def mostrar_resultado(r): # "r" é o objeto Resultado que guarda as informações importantes do nosso simulador
    print("\n" + "=" * 60)
    print(f"Operação: {r.x} {r.op} {r.y}")
    print(f"n = {r.n} dígitos significativos   método = {r.metodo}")
    print("-" * 60)     #Função estetica
    print(f"Valor exato      : {formatar(r.exato)}")
    print(f"Valor aproximado : {formatar(r.aproximado)}")
    print(f"Erro absoluto Ea : {formatar(r.erro_abs)}")
    if r.erro_rel is None:
        print("Erro relativo Er : indefinido (aproximado = 0)")
    else:
        print(f"Erro relativo Er : {r.erro_rel:.6g}  ({r.erro_rel * 100:.4f}%)")
    print("=" * 60)

def main():
    print("Simulador de Propagação de Erros Numéricos")
    while True:
        try:
            x = ler_numero("x = ")
            y = ler_numero("y = ")
            op = ler_operacao()
            n = ler_n()
            metodo = ler_metodo()
            r = calcular(x, y, op, n, metodo, aproximar_entradas=True)
            mostrar_resultado(r)
        except ZeroDivisionError:
            print("Erro: divisão por zero. Tente novamente.")
        
        if input("\nNovo cálculo? (s/n): ").strip().lower() != "s":
            print("Encerrando. Até logo!")
            break

if __name__ == "__main__":
    main()
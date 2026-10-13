"""
testes_exemplos.py  |  Hiago Lima (Pessoa 3)
Executa os três exemplos do enunciado (t = 4 dígitos) e gera tabelas com pandas.
Usa estritamente o contrato: erros.calcular() e erros.Resultado.
"""

from decimal import Decimal, InvalidOperation
import pandas as pd
from erros import Resultado, calcular
import nucleo

# Parâmetros da máquina hipotética fixada no enunciado (PDF página 2)
T = 4  # Mantém t = 4 dígitos significativos
METODOS = ("truncamento", "arredondamento")
MODOS = ("significativos", "casas")  # modos do nucleo.MODO_PRECISAO


def pedir_valor(mensagem, padrao):
    #Lê número decimal do usuário; se teclar Enter vazio, assume o valor padrão.
    while True:
        entrada = input(f"{mensagem} [{padrao}]: ").strip()
        if not entrada:
            return Decimal(str(padrao))
        try:
            # Aceita tanto vírgula quanto ponto decimal
            valor = Decimal(entrada.replace(",", "."))
        except InvalidOperation:
            print("Valor inválido. Tente novamente.")
            continue
        if valor.is_finite():  # recusa NaN e Infinity
            return valor
        print("Valor inválido. Use apenas números.")


def pedir_inteiro(mensagem, padrao):
    #Lê inteiro >= 1 para contadores (ex: quantidade de repetições da soma).
    while True:
        entrada = input(f"{mensagem} [{padrao}]: ").strip()
        if not entrada:
            return int(padrao)
        if entrada.isdigit() and int(entrada) >= 1:
            return int(entrada)
        print("Digite um inteiro válido >= 1.")


def resultado_para_dataframe(lista_resultados, modos=None):
    #Mapeia os atributos dos objetos Resultado em um DataFrame do Pandas.
    #modos (opcional): lista com o modo de precisão de cada resultado (coluna "Modo").
    linhas = []
    for i, r in enumerate(lista_resultados):
        # Erro relativo indefinido quando valor aproximado é zero (divisão por zero)
        if r.erro_rel is None:
            er_fmt = "Indefinido (aprox = 0)"
        else:
            pct = r.erro_rel * Decimal(100)
            er_fmt = f"{r.erro_rel:.6g} ({pct:.4f}%)"

        # Operações simples mostram "x op y"; rótulos livres (ex.: "10 somas de 0.56786") aparecem como estão
        operacao = f"{r.x} {r.op} {r.y}" if r.op in ("+", "-", "*", "/") else r.op

        linha = {}
        if modos:
            linha["Modo"] = modos[i]
        linha.update({
            "Método": r.metodo,
            "Operação": operacao,
            "Valor Exato": str(r.exato),
            "Valor Aprox": str(r.aproximado),
            "Erro Abs (Ea)": str(r.erro_abs),
            "Erro Rel (Er)": er_fmt,
        })
        linhas.append(linha)
    return pd.DataFrame(linhas)


def imprimir_tabela(lista_resultados, titulo="", modos=None):
    # Renderiza a tabela via Pandas no console e em Markdown para o relatório.
    df = resultado_para_dataframe(lista_resultados, modos)
    if titulo:
        print(f"\n>>> {titulo} <<<")
    # Tabela alinhada para leitura no terminal
    print(df.to_string(index=False))
    # Tabela pronta para copiar e colar diretamente no relatório em Markdown/PDF
    print("\nTabela em Markdown:")
    # disable_numparse=True: sem isso o tabulate converte "0.0001000" em 0.0001 e "0.00004" em 4e-05
    print(df.to_markdown(index=False, disable_numparse=True))


def exemplo_1():
    #Exemplo 1: Soma simples de dois números com 5 casas decimais.
    print("\n=== EXEMPLO 1: Soma Simples (5 casas decimais) ===")
    x = pedir_valor("Digite x", "0.12345")
    y = pedir_valor("Digite y", "0.67891")
    # aproximar_entradas=False: apenas o resultado final da soma é reduzido a t dígitos
    resultados = [calcular(x, y, "+", T, m, aproximar_entradas=False) for m in METODOS]
    imprimir_tabela(resultados, "Exemplo 1: Soma Simples")
    return resultados


def exemplo_2():
    #Exemplo 2: Cancelamento subtrativo com números muito próximos.
    print("\n=== EXEMPLO 2: Cancelamento Subtrativo (x - y) ===")
    x = pedir_valor("Digite x", "0.76545")
    y = pedir_valor("Digite y", "0.76541")
    # aproximar_entradas=True: x e y são reduzidos na máquina a 4 dígitos ANTES de subtrair
    resultados = [calcular(x, y, "-", T, m, aproximar_entradas=True) for m in METODOS]
    imprimir_tabela(resultados, "Exemplo 2: Cancelamento Subtrativo")
    print("\nNota: Com arredondamento Er = 60%; com truncamento o resultado é 0 (anulação total).")
    return resultados


def exemplo_3(metodo=None, modos=MODOS):
    #Exemplo 3: Propagação e acúmulo contínuo de erro em somas sequenciais.
    #Roda nos dois modos de precisão do nucleo.py, porque os passos do enunciado
    #(1.1357, 1.7035, 2.2713) só saem com 4 CASAS DECIMAIS, enquanto o texto
    #do enunciado fala em 4 DÍGITOS SIGNIFICATIVOS (1.135, 1.702, 2.269).
    print("\n=== EXEMPLO 3: Propagação de Erro em Sequência de Somas ===")
    val = pedir_valor("Parcela a somar", "0.56786")
    vezes = pedir_inteiro("Quantidade de somas", 10)
    metodos = [metodo] if metodo in METODOS else METODOS
    resumo_resultados = []
    rotulos_modo = []

    modo_original = nucleo.MODO_PRECISAO
    try:
        for modo in modos:
            nucleo.MODO_PRECISAO = modo
            for m in metodos:
                acum = val
                passos_resultado = []
                # Laço sequencial: a cada soma, reduz o resultado para t dígitos e propaga para a próxima
                for i in range(1, vezes):
                    r = calcular(acum, val, "+", T, m, aproximar_entradas=False)
                    passos_resultado.append(r)
                    acum = r.aproximado

                # Exibe como o erro vai crescendo passo a passo (Soma 1 até n-1)
                print(f"\n--- Evolução Passo a Passo ({m.upper()} | modo: {modo}) ---")
                df_passos = pd.DataFrame([{
                    "Passo": f"Soma {idx + 1}",
                    "Operação": f"{r.x} + {r.y}",
                    "Resultado Aprox": str(r.aproximado),
                    "Ea do Passo": str(r.erro_abs),
                } for idx, r in enumerate(passos_resultado)])
                print(df_passos.to_string(index=False))

                # Balanço consolidado final comparando com o valor exato (vezes * parcela)
                exato_total = val * vezes
                ea_total = abs(exato_total - acum)
                er_total = (ea_total / abs(acum)) if acum != 0 else None

                resumo_resultados.append(Resultado(
                    x=val,
                    y=val,
                    op=f"{vezes} somas de {val}",
                    n=T,
                    metodo=m,
                    exato=exato_total,
                    aproximado=acum,
                    erro_abs=ea_total,
                    erro_rel=er_total,
                ))
                rotulos_modo.append(modo)
    finally:
        nucleo.MODO_PRECISAO = modo_original  # sempre devolve o modo original

    # Tabela comparativa final: truncamento x arredondamento, em cada modo
    imprimir_tabela(resumo_resultados, f"Exemplo 3: Comparação Final ({vezes} somas)", rotulos_modo)
    return resumo_resultados


def main():
    #Menu interativo permitindo novos testes sem reiniciar (requisito do PDF).
    while True:
        print(" SIMULADOR DE PROPAGAÇÃO DE ERROS - Exemplos")
        print(f" Máquina Hipotética: t = {T} dígitos significativos")
        print("1 - Exemplo 1: Soma simples")
        print("2 - Exemplo 2: Cancelamento subtrativo")
        print("3 - Exemplo 3: Sequência de somas")
        print("4 - Executar TODOS os exemplos")
        print("0 - Sair")

        opcao = input("Opção (0-4): ").strip()
        if opcao == "1": exemplo_1()
        elif opcao == "2": exemplo_2()
        elif opcao == "3": exemplo_3()
        elif opcao == "4":
            exemplo_1(); exemplo_2(); exemplo_3()
        elif opcao == "0":
            print("Encerrando. Até logo!")
            break
        else:
            print("Opção inválida.")
            continue

        # Permite realizar novo teste sem sair do programa
        if input("\nRealizar outro teste? (s/n): ").strip().lower() != "s":
            break


if __name__ == "__main__":
    main()
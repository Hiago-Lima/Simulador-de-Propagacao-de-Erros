# Simulador de Propagação de Erros Numéricos

Projeto da Unidade 1 (Erros) de Cálculo Numérico, UNIVASF, 2026.2, turma do prof. Jorge Cavalcanti.

Um computador não guarda os números inteiros: ele guarda uma quantidade fixa de dígitos e descarta o resto. Esse descarte parece pequeno, mas se acumula a cada conta e, em alguns casos, destrói o resultado. Este programa simula uma máquina com `n` dígitos para a gente ver isso acontecendo.

Você escolhe dois números, uma operação (`+`, `-`, `*`, `/`), o `n` e o método de corte (truncamento ou arredondamento). O programa mostra o valor exato, o valor que a máquina obteria, o erro absoluto e o erro relativo.

## Exemplo

Subtração de dois números quase iguais, com 4 dígitos e arredondamento:

```
Operação: 0.76545 - 0.76541
n = 4 dígitos significativos   método = arredondamento
------------------------------------------------------------
Valor exato      : 0.00004  (0.4 x 10^-4)
Valor aproximado : 0.0001000  (0.1000 x 10^-3)
Erro absoluto Ea : 0.0000600  (0.600 x 10^-4)
Erro relativo Er : 0.6  (60.0000%)
```

O resultado certo é 0,00004 e a máquina devolveu 0,0001. Um erro de 60% numa conta de subtração. É o cancelamento subtrativo. Com truncamento é pior: os dois números viram 0,7654, a diferença dá zero e o erro relativo nem existe.

## Como rodar

Precisa de Python 3.10 ou mais novo (o `nucleo.py` usa `match/case`). Para as tabelas dos exemplos, instale as dependências:

```bash
pip install -r requirements.txt
```

Depois:

```bash
python main.py              # calculadora: você digita x, y, operação, n e método
python testes_exemplos.py   # Exemplos 1, 2 e 3 do enunciado, com tabelas
```

Os dois programas deixam repetir o cálculo sem reabrir. Dá para digitar `0,76545` ou `0.76545`.

## O que cada arquivo faz

- `nucleo.py`: normalização, truncamento, arredondamento e as operações (exata e com `n` dígitos).
- `erros.py`: erro absoluto, erro relativo e a função `calcular()`, que junta tudo num `Resultado`.
- `main.py`: o menu de terminal.
- `testes_exemplos.py`: os três exemplos do enunciado, montados com pandas.

## Decisões que tomamos

**Decimal em vez de float.** O `float` do Python já comete erro de representação, e isso se misturaria com o erro que queremos simular. Todos os números são `decimal.Decimal`, criados a partir de texto. O valor exato é calculado com 50 dígitos.

**Arredondamento meio para cima.** Usamos `ROUND_HALF_UP`. O `round()` nativo do Python arredonda o meio para o par (2,5 vira 2), o que não é o arredondamento que a disciplina ensina.

**Normalização.** Todo número é escrito como `±0,d₁d₂d₃... × 10^e` com `0,1 ≤ |mantissa| < 1`. É a partir do expoente `e` que se decide em qual casa cortar.

**Aproximar as entradas ou não.** Por padrão, `x` e `y` também são cortados para `n` dígitos antes da conta, como numa máquina de verdade. É isso que produz o cancelamento do Exemplo 2. No Exemplo 1 só o resultado final é cortado (`aproximar_entradas=False`).

**Dígitos significativos ou casas decimais.** O texto do enunciado diz dígitos significativos, mas os passos mostrados no Exemplo 3 (1.1357, 1.7035, 2.2713) só saem se forem 4 casas decimais. Como não ficou claro qual é a intenção, o `nucleo.py` aceita os dois, com a variável `MODO_PRECISAO`:

```python
import nucleo
nucleo.MODO_PRECISAO = "significativos"   # padrão
nucleo.MODO_PRECISAO = "casas"
```

O Exemplo 3 (dez somas de 0,56786, exato 5,6786) roda nos dois modos e mostra a diferença:

| Modo | Truncamento | Arredondamento |
|---|---|---|
| significativos | 5.671 | 5.680 |
| casas | 5.6781 | 5.6789 |

## Equipe

- Arthur Lincoln: `nucleo.py`, teoria do relatório
- Raioni Felix: `erros.py`, `main.py`, repositório
- Hiago Lima: `testes_exemplos.py`, tabelas e análise dos resultados
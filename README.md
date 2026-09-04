# Crypto Sinais — EMA 20

Monitor experimental de **BTC/USDT** desenvolvido em Python. O projeto consulta candles públicos da Binance e compara o último candle fechado no gráfico de 15 minutos com a média móvel exponencial de 20 períodos (EMA 20) para classificar o sinal como compra ou venda. O resultado é exibido diretamente no terminal.

> [!WARNING]
> Este é um projeto educacional e experimental. Os sinais não constituem recomendação de investimento e ainda não foram validados por um backtest completo. Não use o projeto como única base para decisões financeiras.

## Estratégia atual

A estratégia principal usa somente a **EMA 20**:

1. consulta 100 candles de 15 minutos de BTC/USDT;
2. calcula a EMA 20 sobre os preços de fechamento;
3. ignora o candle atual, que pode ainda estar em formação;
4. compara o fechamento do último candle encerrado com a EMA 20;
5. gera sinal de compra quando o fechamento está acima da média ou sinal de venda para abertura de posição vendida quando está abaixo.

A regra é:

```text
Fechamento do último candle encerrado > EMA 20 = COMPRA
Fechamento do último candle encerrado < EMA 20 = VENDA (abrir posição vendida)
Fechamento do último candle encerrado = EMA 20 = NEUTRO
```

Cada execução gera novamente a classificação correspondente enquanto o preço permanecer acima ou abaixo da EMA 20. Esse comportamento é intencional. O resultado inclui o horário de Brasília do candle encerrado para permitir a conferência dos dados.

No gráfico de 15 minutos, 20 candles representam aproximadamente cinco horas de mercado. Por ser exponencial, a EMA dá mais peso aos preços recentes.

O projeto apenas consulta dados de mercado e gera alertas. Ele **não abre, altera ou encerra ordens**.

## Estrutura do repositório

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | fluxo principal com a estratégia EMA 20 |
| `pares_usdt.txt` | ativo analisado; atualmente, somente BTC/USDT |
| `requirements.txt` | dependências Python |
| `legacy/` | experimentos antigos, preservados como histórico e fora do fluxo principal |

## Requisitos

- Python 3.11 ou superior;
- acesso à internet;
As consultas públicas de candles não exigem chave de API da Binance.

## Instalação

Clone o repositório e entre na pasta:

```bash
git clone https://github.com/gabrielmgsales/Crypto_Sinais_PriceAction.git
cd Crypto_Sinais_PriceAction
```

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Execução

Para executar a análise e mostrar o resultado no terminal:

```bash
python main.py
```

O programa consulta apenas dados públicos e não realiza operações.

Um resultado válido informa:

- classificação como COMPRA, VENDA ou NEUTRO;
- preço de fechamento;
- valor da EMA 20;
- horário de Brasília do candle analisado.

Se a consulta falhar, o programa diferencia erro de conexão, rejeição da Binance, dados insuficientes e falha inesperada.


## Limitações conhecidas

- a EMA 20 isolada pode gerar sinais falsos em mercados laterais;
- alertas de compra ou venda podem se repetir enquanto o fechamento permanecer do mesmo lado da média;
- não existe backtest incluído;
- não há regras de stop-loss, alvo ou tamanho de posição;
- não há prevenção de alertas duplicados;
- não há testes automatizados;

## Próximas melhorias

- [x] limitar a análise a BTC/USDT;
- [x] remover a integração antiga com o Telegram;
- [x] usar somente candles fechados;
- [x] simplificar a estratégia principal para EMA 20;
- [ ] adicionar testes automatizados;
- [ ] implementar backtest e métricas de desempenho;
- [ ] adicionar logs estruturados;
- [x] diferenciar falhas de conexão, da Binance e de dados;
- [x] separar os scripts experimentais antigos em `legacy/`;
- [x] remover dependências não utilizadas e fixar as versões testadas.

## Licença

Distribuído sob a licença MIT. Consulte o arquivo `LICENSE`.

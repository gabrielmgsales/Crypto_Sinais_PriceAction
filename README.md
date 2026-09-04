# Crypto Sinais — Price Action

Monitor experimental de **BTC/USDT** desenvolvido em Python. O projeto consulta candles públicos da Binance, calcula indicadores técnicos e identifica possíveis mudanças de direção. Quando configurado, o resultado pode ser enviado para um chat do Telegram.

> [!WARNING]
> Este é um projeto educacional e experimental. Os sinais não constituem recomendação de investimento e ainda não foram validados por um backtest completo. Não use o projeto como única base para decisões financeiras.

## O que o projeto faz

O fluxo principal:

1. lê o ativo definido em `pares_usdt.txt`;
2. consulta 100 candles de 15 minutos na Binance por meio do CCXT;
3. calcula ATR, DMI e DPO;
4. verifica cruzamentos que podem indicar reversão;
5. reúne os sinais encontrados;
6. envia o resultado pelo Telegram, quando o serviço está configurado.

O projeto apenas consulta dados de mercado e gera alertas. Ele **não abre, altera ou encerra ordens**.

## Estratégia atual

O arquivo `main.py` compara os dois últimos candles encerrados, ignorando o candle ainda em formação, e procura os seguintes eventos:

| Indicador | Possível sinal de alta | Possível sinal de baixa |
| --- | --- | --- |
| DMI | `+DI` cruza acima de `-DI` | `+DI` cruza abaixo de `-DI` |
| DPO | cruza o nível zero de baixo para cima | cruza o nível zero de cima para baixo |

O ATR é usado no cálculo do DMI como medida de volatilidade.

Os arquivos `rsi.py` e `volume.py` são experimentos separados e não fazem parte do fluxo principal. Seus cálculos ainda precisam de revisão antes de serem considerados parte da estratégia.

## Estrutura do repositório

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | fluxo principal com ATR, DMI e DPO |
| `telegram_notifier.py` | envio das notificações |
| `pares_usdt.txt` | ativo analisado; atualmente, somente BTC/USDT |
| `dmi.py` | experimento isolado com DMI |
| `dpo.py` | experimento isolado com DPO e DMI |
| `rsi.py` | experimento isolado com RSI |
| `volume.py` | experimento isolado com volume |
| `config_api.py` | espaço reservado para configuração da exchange |
| `requirements.txt` | dependências Python conhecidas |

## Requisitos

- Python 3.10 ou superior
- acesso à internet
- uma conta e um bot do Telegram, caso queira receber notificações

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

Instale as dependências disponíveis:

```bash
pip install -r requirements.txt
```

## Configuração do Telegram

Copie `.env.example` para `.env` e preencha as variáveis:

```dotenv
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Nunca publique o arquivo `.env` ou credenciais reais no GitHub.

## Execução

Para testar a análise e exibir o resultado somente no terminal:

```bash
python main.py --dry-run
```

Esse modo não exige configuração do Telegram e não envia mensagens.

Para analisar e enviar o resultado ao Telegram:

```bash
python main.py
```

Nesse caso, as duas variáveis do Telegram precisam estar configuradas no arquivo `.env`.

## Limitações conhecidas

- não existe backtest incluído;
- não há regras de stop-loss, alvo ou tamanho de posição;
- o candle mais recente pode ainda estar em formação;
- a implementação do RSI precisa de correção;
- o analisador de volume mistura operações síncronas e assíncronas;
- o módulo do Telegram executa código durante sua importação;
- não há prevenção de alertas duplicados;
- não há testes automatizados;
- algumas dependências precisam ser revisadas.

## Próximas melhorias

- [x] mover credenciais para variáveis de ambiente;
- [x] criar um modo de diagnóstico sem Telegram;
- [x] corrigir o módulo de notificação;
- [x] usar somente candles fechados;
- [ ] revisar os cálculos dos indicadores;
- [ ] remover código duplicado;
- [ ] adicionar logs e tratamento de falhas;
- [ ] criar testes automatizados;
- [ ] implementar backtest e métricas de desempenho.

## Licença

Distribuído sob a licença MIT. Consulte o arquivo `LICENSE`.

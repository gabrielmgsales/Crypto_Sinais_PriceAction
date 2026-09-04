import ccxt
import pandas as pd


STRATEGY_ID = 'ema-20'
STRATEGY_NAME = 'Estratégia EMA 20'
SYMBOL = 'BTCUSDT'
TIMEFRAME = '15m'
EMA_PERIOD = 20
CANDLE_LIMIT = 100


def calculate_ema(df, period=EMA_PERIOD):
    column_name = f'ema_{period}'
    df[column_name] = df['close'].ewm(span=period, adjust=False).mean()
    return df, column_name


def format_usdt(value):
    formatted_value = f"{value:,.2f}"
    brazilian_value = formatted_value.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"US$ {brazilian_value} (USDT)"


def analyze_coin(coin_symbol=SYMBOL):
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        bars = exchange.fetch_ohlcv(
            coin_symbol,
            timeframe=TIMEFRAME,
            limit=CANDLE_LIMIT,
        )

        minimum_candles = EMA_PERIOD + 2
        if len(bars) < minimum_candles:
            return (
                f"ERRO: dados insuficientes para {coin_symbol}. "
                f"Recebidos {len(bars)} candles; necessários pelo menos {minimum_candles}."
            )

        df = pd.DataFrame(
            bars,
            columns=['time', 'open', 'high', 'low', 'close', 'volume'],
        )
        df, ema_column = calculate_ema(df)

        # A última linha (-1) pode representar um candle ainda em formação.
        # O sinal usa somente o candle mais recente já encerrado.
        closed_candle = df.iloc[-2]
        close_price = closed_candle['close']
        ema_value = closed_candle[ema_column]
        candle_time = pd.to_datetime(
            int(closed_candle['time']),
            unit='ms',
            utc=True,
        ).tz_convert('America/Sao_Paulo').strftime(
            '%d/%m/%Y %H:%M (horário de Brasília)'
        )

        if pd.isnull(close_price) or pd.isnull(ema_value):
            return f"ERRO: fechamento ou EMA {EMA_PERIOD} indisponível para {coin_symbol}."

        if close_price > ema_value:
            action = 'COMPRA'
            position = 'acima'
        elif close_price < ema_value:
            action = 'VENDA — abrir posição vendida'
            position = 'abaixo'
        else:
            action = 'NEUTRO'
            position = 'igual à'

        return (
            f"Sinal: {action}. {coin_symbol} fechou {position} EMA {EMA_PERIOD} "
            f"no gráfico de {TIMEFRAME}. "
            f"Fechamento: {format_usdt(close_price)} | "
            f"EMA {EMA_PERIOD}: {format_usdt(ema_value)} | "
            f"Candle fechado em: {candle_time}"
        )

    except ccxt.NetworkError as error:
        print(f"Detalhes da falha de conexão: {error}")
        return f"ERRO: não foi possível conectar à Binance para analisar {coin_symbol}."
    except ccxt.ExchangeError as error:
        print(f"Detalhes do erro da Binance: {error}")
        return f"ERRO: a Binance recusou os dados solicitados para {coin_symbol}."
    except (KeyError, IndexError, TypeError, ValueError) as error:
        print(f"Detalhes dos dados inválidos: {error}")
        return f"ERRO: os dados recebidos para {coin_symbol} são inválidos ou incompletos."
    except Exception as error:
        print(f"Erro inesperado ao analisar {coin_symbol}: {error}")
        return f"ERRO: ocorreu uma falha inesperada ao analisar {coin_symbol}."


def run_strategy():
    return analyze_coin(SYMBOL)

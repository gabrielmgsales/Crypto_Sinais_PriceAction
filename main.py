import argparse
import asyncio
from pathlib import Path

import ccxt
import pandas as pd

from telegram_notifier import send_telegram_message


EMA_PERIOD = 20
TIMEFRAME = '15m'


def calculate_ema(df, period=EMA_PERIOD):
    df['ema_20'] = df['close'].ewm(span=period, adjust=False).mean()
    return df


def analyze_coin(coin_symbol):
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        bars = exchange.fetch_ohlcv(coin_symbol, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(
            bars,
            columns=['time', 'open', 'high', 'low', 'close', 'volume'],
        )
        df = calculate_ema(df)

        # A última linha (-1) pode representar um candle ainda em formação.
        # O sinal usa somente o candle mais recente já encerrado.
        closed_candle = df.iloc[-2]
        close_price = closed_candle['close']
        ema_20 = closed_candle['ema_20']

        if pd.isnull(close_price) or pd.isnull(ema_20):
            return None

        if close_price > ema_20:
            action = 'COMPRA'
            position = 'acima'
        elif close_price < ema_20:
            action = 'VENDA — abrir posição vendida'
            position = 'abaixo'
        else:
            action = 'NEUTRO'
            position = 'igual à'

        return (
            f"Sinal: {action}. {coin_symbol} fechou {position} EMA 20 "
            f"no gráfico de 15 minutos. "
            f"Fechamento: {close_price:.2f} | EMA 20: {ema_20:.2f}"
        )

    except Exception as error:
        print(f"Erro ao analisar {coin_symbol}: {error}")

    return None


def build_message(signals):
    if not signals:
        return "Não foi possível determinar o sinal de BTC/USDT."

    return "\n\n".join(signals)


async def analyze_assets_async(notify=True):
    pairs_file = Path(__file__).with_name('pares_usdt.txt')
    with pairs_file.open('r', encoding='utf-8') as file:
        coins_list = [line.strip() for line in file if line.strip()]

    signals = [signal for coin in coins_list if (signal := analyze_coin(coin))]
    message = build_message(signals)

    if notify:
        await send_telegram_message(message)
    else:
        print(message)

    return signals


async def run_analysis(notify=True):
    return await analyze_assets_async(notify=notify)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gera sinal de compra ou venda de BTC/USDT com base na EMA 20."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exibe o resultado no terminal sem enviar mensagem ao Telegram.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_analysis(notify=not args.dry_run))

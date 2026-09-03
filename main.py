import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import ccxt
import pandas as pd

from telegram_notifier import send_telegram_message


def calculate_atr(df, period):
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift())
    df['low_close'] = abs(df['low'] - df['close'].shift())
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['average_true_range'] = df['true_range'].rolling(window=period).mean()
    return df


def calculate_dmi(df, period):
    df['high_diff'] = df['high'].diff()
    df['low_diff'] = df['low'].diff()
    df['up_move'] = df['high_diff'].apply(lambda x: x if x > 0 else 0)
    df['down_move'] = df['low_diff'].apply(lambda x: abs(x) if x < 0 else 0)

    df['ema_up'] = df['up_move'].ewm(span=period).mean()
    df['ema_down'] = df['down_move'].ewm(span=period).mean()

    df['+DI'] = (df['ema_up'] / df['average_true_range']) * 100
    df['-DI'] = (df['ema_down'] / df['average_true_range']) * 100
    return df


def calculate_dpo(df, period):
    df['dpo'] = df['close'].shift(int(period / 2) + 1).rolling(window=period).mean()
    df['dpo'] = df['close'] - df['dpo']
    return df


def analyze_coin(coin_symbol):
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        bars = exchange.fetch_ohlcv(coin_symbol, timeframe='15m', limit=100)
        df = pd.DataFrame(
            bars,
            columns=['time', 'open', 'high', 'low', 'close', 'volume'],
        )

        df = calculate_atr(df, 14)
        df = calculate_dmi(df, 14)
        df = calculate_dpo(df, 21)

        current_plus_di = df['+DI'].iloc[-1]
        current_minus_di = df['-DI'].iloc[-1]
        previous_plus_di = df['+DI'].iloc[-2]
        previous_minus_di = df['-DI'].iloc[-2]

        current_dpo = df['dpo'].iloc[-1]
        previous_dpo = df['dpo'].iloc[-2]

        if all(
            pd.notnull(value)
            for value in (
                current_plus_di,
                current_minus_di,
                previous_plus_di,
                previous_minus_di,
            )
        ):
            if previous_plus_di < previous_minus_di and current_plus_di > current_minus_di:
                return f"+DI e -DI indicando reversão de tendência para alta em {coin_symbol}"
            if previous_plus_di > previous_minus_di and current_plus_di < current_minus_di:
                return f"-DI e +DI indicando reversão de tendência para baixa em {coin_symbol}"

        if pd.notnull(current_dpo) and pd.notnull(previous_dpo):
            if previous_dpo < 0 and current_dpo > 0:
                return f"DPO indicando reversão para alta em {coin_symbol}"
            if previous_dpo > 0 and current_dpo < 0:
                return f"DPO indicando reversão para baixa em {coin_symbol}"

    except Exception as error:
        print(f"Erro ao analisar {coin_symbol}: {error}")

    return None


def build_message(signals):
    if not signals:
        return "Nenhum ativo com sinal."

    formatted_signals = "\n\n".join(f"- {signal}" for signal in signals)
    return f"Ativos com sinais:\n\n{formatted_signals}"


async def analyze_assets_async(notify=True):
    pairs_file = Path(__file__).with_name('pares_usdt.txt')
    with pairs_file.open('r', encoding='utf-8') as file:
        coins_list = [line.strip() for line in file if line.strip()]

    with ThreadPoolExecutor() as executor:
        signals = [result for result in executor.map(analyze_coin, coins_list) if result]

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
        description="Analisa BTC/USDT e, opcionalmente, envia o resultado pelo Telegram."
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

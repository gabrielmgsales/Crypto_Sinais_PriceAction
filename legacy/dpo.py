import ccxt
import pandas as pd
import numpy as np
import asyncio
from telegram_notifier import send_telegram_message

async def calculate_atr(df, period):
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift())
    df['low_close'] = abs(df['low'] - df['close'].shift())
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['average_true_range'] = df['true_range'].rolling(window=period).mean()
    return df

async def calculate_dpo(df, period):
    shift = int(period / 2) + 1
    df['dpo'] = df['close'].shift(shift) - df['close'].rolling(window=period).mean()
    return df

async def calculate_dmi(df, period):
    df['high_shifted'] = df['high'].shift(1)
    df['low_shifted'] = df['low'].shift(1)

    df['up_move'] = df['high'] - df['high_shifted']
    df['down_move'] = df['low_shifted'] - df['low']

    df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
    df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)

    df['avg_plus_dm'] = df['plus_dm'].rolling(window=period).mean()
    df['avg_minus_dm'] = df['minus_dm'].rolling(window=period).mean()

    df['plus_di'] = 100 * (df['avg_plus_dm'] / df['average_true_range'])
    df['minus_di'] = 100 * (df['avg_minus_dm'] / df['average_true_range'])

    return df

async def detect_trend_reversal(df, symbol):
    current_dpo = df['dpo'].iloc[-1]
    previous_dpo = df['dpo'].iloc[-2]
    current_plus_di = df['plus_di'].iloc[-1]
    current_minus_di = df['minus_di'].iloc[-1]

    if pd.notnull(current_dpo) and pd.notnull(previous_dpo) and pd.notnull(current_plus_di) and pd.notnull(current_minus_di):
        if previous_dpo < 0 and current_dpo > 0 and current_plus_di > current_minus_di:
            return f"DPO indicando reversão de tendência para alta em {symbol}"
        elif previous_dpo > 0 and current_dpo < 0 and current_minus_di > current_plus_di:
            return f"DPO indicando reversão de tendência para baixa em {symbol}"
    return None

async def analyze_coin(coin_symbol):
    try:
        exchange = ccxt.binance()
        bars = exchange.fetch_ohlcv(coin_symbol, timeframe='1h')  # Não limitar a quantidade de candles
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        period = 21
        
        # Calcular o ATR, DPO e DMI de forma assíncrona
        df = await calculate_atr(df, period)
        df = await calculate_dpo(df, period)
        df = await calculate_dmi(df, period)

        # Detecção de reversão de tendência com DPO e DMI
        reversal_signal = await detect_trend_reversal(df, coin_symbol)

        return reversal_signal

    except Exception as e:
        print(f"Erro ao analisar {coin_symbol}: {e}")
    return None

async def analyze_assets_async():
    with open('pares_usdt.txt', 'r') as file:
        coins_list = [line.strip() for line in file.readlines() if line.strip()]

    assets_with_signals = []

    tasks = [analyze_coin(coin) for coin in coins_list]
    results = await asyncio.gather(*tasks)

    assets_with_signals = [result for result in results if result]

    if assets_with_signals:
        message = "Ativos com sinais:\n\n"
        for asset_signal in assets_with_signals:
            message += f"- {asset_signal}\n\n"

        await send_telegram_message(message)
    else:
        await send_telegram_message("Nenhum ativo com sinal.")

async def run_analysis():
    await analyze_assets_async()

if __name__ == "__main__":
    asyncio.run(run_analysis())
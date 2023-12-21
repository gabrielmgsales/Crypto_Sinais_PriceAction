import ccxt
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import asyncio
from telegram_notifier import send_telegram_message

def calculate_rsi(df, period):
    df['delta'] = df['close'].diff()
    df['gain'] = (df['delta'] * 0).where(df['delta'] < 0, df['delta'])
    df['loss'] = (-df['delta'] * 0).where(df['delta'] < 0, df['delta'])

    df['avg_gain'] = df['gain'].rolling(window=period).mean()
    df['avg_loss'] = df['loss'].rolling(window=period).mean().abs()

    df['rs'] = df['avg_gain'] / df['avg_loss']
    df['rsi'] = 100 - (100 / (1 + df['rs']))

    return df

def detect_recent_cross(df):
    if df['rsi'].iloc[-1] > df['sma'].iloc[-1] and df['rsi'].iloc[-2] < df['sma'].iloc[-2]:
        return "RSI crossed above SMA in the previous candle"
    elif df['rsi'].iloc[-1] < df['sma'].iloc[-1] and df['rsi'].iloc[-2] > df['sma'].iloc[-2]:
        return "RSI crossed below SMA in the previous candle"
    else:
        return None

def analyze_coin(coin_symbol):
    try:
        exchange = ccxt.binance()
        bars = exchange.fetch_ohlcv(coin_symbol, timeframe='1h', limit=15)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        period = 14
        df = calculate_rsi(df, period)

        # Calcular a SMA de 14 períodos
        df['sma'] = df['close'].rolling(window=14).mean()

        recent_cross = detect_recent_cross(df)

        if recent_cross:
            return f"Cruzamento detectado em {coin_symbol}: {recent_cross}"

    except Exception as e:
        print(f"Erro ao analisar {coin_symbol}: {e}")
    return None

async def analyze_assets_async():
    with open('pares_usdt.txt', 'r') as file:
        coins_list = [line.strip() for line in file.readlines() if line.strip()]

    assets_with_signals = []

    for coin_symbol in coins_list:
        result = analyze_coin(coin_symbol)
        if result:
            assets_with_signals.append(result)

    if assets_with_signals:
        message = "Ativos com sinais:\n\n"
        for asset_signal in assets_with_signals:
            message += f"- {asset_signal}\n\n"

        await send_telegram_message(message)
    else:
        await send_telegram_message("Nenhum ativo com sinal no RSI.")

async def run_analysis():
    await analyze_assets_async()

if __name__ == "__main__":
    asyncio.run(run_analysis())
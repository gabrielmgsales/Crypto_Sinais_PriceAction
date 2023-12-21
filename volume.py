import ccxt
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import asyncio
from telegram_notifier import send_telegram_message

async def analyze_volume_strength_15min_async(coin_symbol):
    try:
        exchange = ccxt.binance()  # Substitua 'binance' pela exchange desejada
        bars = await exchange.fetch_ohlcv(coin_symbol, timeframe='15m', limit=100)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        current_volume = df['volume'].iloc[-1]
        previous_volume = df['volume'].iloc[-2]
        previous_candle_range = df['high'].iloc[-3] - df['low'].iloc[-3]  # Candle fechado anterior
        
        # Defina um limiar para identificar um volume como forte e um candle como fraco
        volume_threshold = 50000  # Ajuste este valor conforme necessário
        
        # Verifica se o volume do candle atual é forte e se o candle de preço correspondente (anterior) é fraco
        if previous_volume > 2 * volume_threshold and previous_candle_range < 0.5 * current_volume:
            return f"Sinal de volume forte e candle de preço fraco em {coin_symbol}."
        
    except Exception as e:
        print(f"Erro ao analisar {coin_symbol}: {e}")
    return None

async def analyze_assets_15min_async():
    # Carregar moedas do arquivo pares_usdt.txt
    with open('pares_usdt.txt', 'r') as file:
        coins_list = [line.strip() for line in file.readlines() if line.strip()]

    assets_with_signals = []

    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, analyze_volume_strength_15min_async, coin) for coin in coins_list]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                assets_with_signals.append(result)

    if assets_with_signals:
        message = "Ativos com sinais de volume forte e candle de preço fraco (Intervalo de 15 minutos):\n\n"
        for asset_signal in assets_with_signals:
            message += f"- {asset_signal}\n\n"

        await send_telegram_message(message)
    else:
        await send_telegram_message("Nenhum ativo com sinal de volume forte e candle de preço fraco (Intervalo de 15 minutos).")

if __name__ == "__main__":
    asyncio.run(analyze_assets_15min_async())
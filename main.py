import ccxt
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import asyncio
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
        exchange = ccxt.binance()  # Substitua 'binance' pela exchange desejada
        bars = exchange.fetch_ohlcv(coin_symbol, timeframe='15m', limit=100)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        period = 14
        df = calculate_atr(df, period)
        df = calculate_dmi(df, period)
        
        period_dpo = 21  # Período para o DPO
        df = calculate_dpo(df, period_dpo)
        
        current_plus_di = df['+DI'].iloc[-1]
        current_minus_di = df['-DI'].iloc[-1]
        previous_plus_di = df['+DI'].iloc[-2]
        previous_minus_di = df['-DI'].iloc[-2]
        
        current_dpo = df['dpo'].iloc[-1]
        previous_dpo = df['dpo'].iloc[-2]

        if pd.notnull(current_plus_di) and pd.notnull(current_minus_di) and pd.notnull(previous_plus_di) and pd.notnull(previous_minus_di):
            if previous_plus_di < previous_minus_di and current_plus_di > current_minus_di:
                return f"+DI e -DI indicando reversão de tendência para alta em {coin_symbol}"
            elif previous_plus_di > previous_minus_di and current_plus_di < current_minus_di:
                return f"-DI e +DI indicando reversão de tendência para baixa em {coin_symbol}"
        
        if pd.notnull(current_dpo) and pd.notnull(previous_dpo):
            if previous_dpo < 0 and current_dpo > 0:
                return f"DPO indicando reversão para alta em {coin_symbol}"
            elif previous_dpo > 0 and current_dpo < 0:
                return f"DPO indicando reversão para baixa em {coin_symbol}"
        
    except Exception as e:
        print(f"Erro ao analisar {coin_symbol}: {e}")
    return None

async def analyze_assets_async():
    # Carregar moedas do arquivo pares_usdt.txt
    with open('pares_usdt.txt', 'r') as file:
        coins_list = [line.strip() for line in file.readlines() if line.strip()]

    assets_with_signals = []

    with ThreadPoolExecutor() as executor:
        results = executor.map(analyze_coin, coins_list)
        
        for result in results:
            if result:
                assets_with_signals.append(result)

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
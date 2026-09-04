from backend.strategies import ema_20


DEFAULT_STRATEGY_ID = ema_20.STRATEGY_ID

_STRATEGIES = {
    ema_20.STRATEGY_ID: {
        'metadata': ema_20.get_metadata,
        'runner': ema_20.run_strategy,
    },
}


def list_strategies():
    return [entry['metadata']() for entry in _STRATEGIES.values()]


def get_strategy(strategy_id):
    try:
        return _STRATEGIES[strategy_id]['metadata']()
    except KeyError as error:
        raise ValueError(f"Estratégia desconhecida: {strategy_id}") from error


def run_strategy(strategy_id):
    try:
        runner = _STRATEGIES[strategy_id]['runner']
    except KeyError as error:
        raise ValueError(f"Estratégia desconhecida: {strategy_id}") from error

    return runner()

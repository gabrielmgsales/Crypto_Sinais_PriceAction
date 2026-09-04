from backend.strategies.registry import DEFAULT_STRATEGY_ID, run_strategy


def main():
    result = run_strategy(DEFAULT_STRATEGY_ID)
    print(result)
    return result


if __name__ == "__main__":
    main()

from backend.strategies.ema_20 import run_strategy


def main():
    result = run_strategy()
    print(result)
    return result


if __name__ == "__main__":
    main()

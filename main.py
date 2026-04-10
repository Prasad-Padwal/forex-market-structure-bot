import argparse


def main():
    parser = argparse.ArgumentParser(description='Trading Bot CLI')
    parser.add_argument('--action', type=str, required=True, choices=['buy', 'sell'],
                        help='Specify action: buy or sell')
    parser.add_argument('--amount', type=float, required=True,
                        help='Amount to trade')
    parser.add_argument('--symbol', type=str, required=True,
                        help='Trading pair symbol (e.g., EURUSD)')

    args = parser.parse_args()
    
    # Example logic to execute the trade
    if args.action == 'buy':
        print(f'Buying {args.amount} of {args.symbol}')
    elif args.action == 'sell':
        print(f'Selling {args.amount} of {args.symbol}')


if __name__ == '__main__':
    main()
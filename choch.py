def detect_choh(prices):
    """
    Detects Change of Character (CHoC) based on the given price data.
    Identifies Bullish CHoH and Bearish CHoH patterns.
    """
    bullish_choh = []
    bearish_choh = []

    for i in range(1, len(prices) - 1):
        # Bullish CHoH Pattern Detection
        if prices[i - 1] < prices[i] > prices[i + 1]:
            bullish_choh.append((i, prices[i]))
        # Bearish CHoH Pattern Detection
        elif prices[i - 1] > prices[i] < prices[i + 1]:
            bearish_choh.append((i, prices[i]))

    return bullish_choh, bearish_choh

# Example usage
if __name__ == '__main__':
    sample_prices = [1.0, 1.2, 1.1, 1.3, 1.0, 1.5, 1.4]
    bullish, bearish = detect_choh(sample_prices)
    print('Bullish CHoH patterns:', bullish)
    print('Bearish CHoH patterns:', bearish)
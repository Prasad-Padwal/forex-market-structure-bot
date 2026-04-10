class MarketStructureLevels:
    def __init__(self, price_data):
        self.price_data = price_data
        self.zones = []

    def calculate_zones(self):
        # Simplified example for 3-level zones
        high = max(self.price_data)
        low = min(self.price_data)
        mid = (high + low) / 2
        self.zones = [low, mid, high]

    def get_zones(self):
        return self.zones

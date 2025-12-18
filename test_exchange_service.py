"""Test the updated Exchange Rate Service"""

from app.models.value_objects import Currency
from app.services.exchange_rate_service import ExchangeRateService

def test_exchange_service():
    print("=" * 70)
    print("TESTING EXCHANGE RATE SERVICE")
    print("=" * 70)
    
    # Initialize service (will try to fetch live rates)
    service = ExchangeRateService()
    
    # Get rate info
    info = service.get_rate_info()
    print(f"\nRate Source: {info['source']}")
    print(f"Last Update: {info['last_update']}")
    print(f"Cache Valid: {info['cache_valid']}")
    
    print("\n" + "=" * 70)
    print("CURRENT EXCHANGE RATES (Base: TRY)")
    print("=" * 70)
    
    for currency, rate in info['rates'].items():
        if currency != 'TRY':
            print(f"1 {currency:>3} = {rate:>8.2f} TRY")
    
    print("\n" + "=" * 70)
    print("CONVERSION TESTS")
    print("=" * 70)
    
    # Test conversions
    test_cases = [
        (100, Currency.USD, Currency.TRY),
        (100, Currency.EUR, Currency.TRY),
        (1000, Currency.TRY, Currency.USD),
        (1000, Currency.TRY, Currency.EUR),
        (100, Currency.USD, Currency.EUR),
    ]
    
    for amount, from_curr, to_curr in test_cases:
        converted = service.convert(amount, from_curr, to_curr)
        rate = service.get_rate(from_curr, to_curr)
        print(f"{amount:>8.2f} {from_curr.value} = {converted:>10.2f} {to_curr.value} "
              f"(rate: {rate:.6f})")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    test_exchange_service()
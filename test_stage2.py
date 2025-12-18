from app.models.value_objects import Money, Currency
from app.models.account import Account
from app.models.transaction import TransactionType
from app.services.exchange_rate_service import ExchangeRateService
from app.services.transaction_service import TransactionService
from app.services.reporting_service import ReportingService

# Test Money
m1 = Money(100.50, Currency.USD)
m2 = Money(50.25, Currency.USD)
print(f"m1 + m2 = {m1 + m2}")  # Should print: 150.75 USD

# Test Account
account = Account("ACC001", "CUST001", Money(1000.0, Currency.USD))
account.deposit(Money(500.0, Currency.USD), "Salary")
account.withdraw(Money(200.0, Currency.USD), "ATM")
print(f"Balance: {account.balance}")  # Should print: 1300.00 USD

# Test Running Balance (Generator)
print("\nRunning Balance:")
for txn, balance in account.get_running_balance():
    print(f"{txn.transaction_type.value}: {txn.amount} -> Balance: {balance}")

# Test Exchange Rate
service = ExchangeRateService()
rate = service.get_rate(Currency.USD, Currency.TRY)
print(f"\n1 USD = {rate} TRY")

# Test Transaction Filtering
criteria = {'transaction_type': TransactionType.DEPOSIT}
deposits = TransactionService.search_transactions(account.transactions, criteria)
print(f"\nFound {len(deposits)} deposits")

# Test Reporting
report = ReportingService.generate_monthly_summary(account.transactions)
print(f"\nMonthly summary: {report}")

print("\n✅ All tests passed!")
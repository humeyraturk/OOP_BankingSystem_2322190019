🏦 OOP Banking System - Stage 3: Final Release (Advanced Application)
Course: Banking and Payment System
Student ID: Hümeyra TÜRK - 2322190019
Branch: S3_AdvancedApplication

📋 Project Overview
This project implements a production-ready banking system demonstrating advanced Object-Oriented Programming principles, SOLID design patterns, and enterprise-grade architecture. Stage 3 (Final Release) delivers a complete application with Streamlit Web GUI, JSON Persistence, Real-time Currency Exchange API Integration, Fraud Detection, and comprehensive business logic for presentation-ready deployment.

🎯 Design Principles
Core OOP Principles Applied

Encapsulation: Private attributes with property-based access control
Inheritance: Abstract base classes for polymorphic behavior
Polymorphism: Multiple account types with specialized behaviors (SavingsAccount, CheckingAccount)
Abstraction: Clear separation between interface and implementation

SOLID Principles

Single Responsibility: Each class has one clear purpose
Open/Closed: Extensible through inheritance, closed for modification
Liskov Substitution: Derived classes can substitute base classes
Interface Segregation: Clean, focused interfaces
Dependency Inversion: Depend on abstractions, not concretions


🏗️ Architecture
Layered Architecture
┌─────────────────────────────────────┐
│  Presentation Layer                 │  ✅ IMPLEMENTED
│  (Streamlit Web GUI)                │     (Stage 3)
├─────────────────────────────────────┤
│     Service Layer                   │  ✅ IMPLEMENTED
│  (Business Logic & Algorithms)      │     (Stage 2-3)
│  • ExchangeRateService (Live API)   │
│  • FraudDetectionService            │
│  • TransactionService               │
│  • ReportingService                 │
├─────────────────────────────────────┤
│     Domain Layer (Models)           │  ✅ IMPLEMENTED
│     (Core Business Objects)         │     (Stage 1-2)
│  • Money, Currency                  │
│  • Account, SavingsAccount          │
│  • CheckingAccount, Transaction     │
│  • Customer, Bank                   │
├─────────────────────────────────────┤
│     Data Layer                      │  ✅ IMPLEMENTED
│     (JSON Persistence)              │     (Stage 3)
└─────────────────────────────────────┘

📊 UML Class Diagram
mermaidclassDiagram
    class Currency {
        <<enumeration>>
        USD
        EUR
        GBP
        TRY
    }

    class Money {
        <<frozen dataclass>>
        -float amount
        -Currency currency
        +__add__(other) Money
        +__sub__(other) Money
        +__str__() str
    }

    class TransactionType {
        <<enumeration>>
        DEPOSIT
        WITHDRAWAL
        TRANSFER
        INTEREST
        FEE
    }

    class Transaction {
        -str transaction_id
        -datetime timestamp
        -TransactionType transaction_type
        -Money amount
        -str description
        -str account_number
        -str related_account
        +__str__() str
    }

    class AbstractAccount {
        <<abstract>>
        -str account_number
        -str owner_id
        -Money balance
        -List~Transaction~ transactions
        +deposit(amount, description)* bool
        +withdraw(amount, description)* bool
        +get_balance() Money
        +get_transaction_history() List~Transaction~
        +get_running_balance() Generator
    }

    class SavingsAccount {
        -float interest_rate
        +apply_interest() Money
        +calculate_interest() Money
    }

    class CheckingAccount {
        -float overdraft_limit
        +get_available_balance() Money
        +is_overdrawn() bool
    }

    class Customer {
        -str customer_id
        -str name
        -str email
        -str phone
        -List~AbstractAccount~ accounts
        +add_account(account) void
        +get_account(account_number) AbstractAccount
    }

    class Bank {
        -str name
        -Dict~str,Customer~ customers
        -Dict~str,AbstractAccount~ accounts
        +create_customer(id, name, email, phone) Customer
        +get_customer(customer_id) Customer
        +register_account(account) void
        +get_account(account_number) AbstractAccount
        +get_all_customers() List~Customer~
        +get_all_accounts() List~AbstractAccount~
    }

    class ExchangeRateService {
        +get_rate(from, to) float
        +convert(amount, from, to) float
        +update_rates() bool
    }

    class FraudDetectionService {
        +check_transaction(account, amount) Tuple
        +check_withdrawal(account, amount) Tuple
        +check_deposit(account, amount) Tuple
    }

    Money --> Currency
    Transaction --> Money
    Transaction --> TransactionType
    AbstractAccount --> Money
    AbstractAccount --> Transaction
    SavingsAccount --|> AbstractAccount
    CheckingAccount --|> AbstractAccount
    Customer --> AbstractAccount
    Bank --> Customer
    Bank --> AbstractAccount
    Bank ..> ExchangeRateService
    Bank ..> FraudDetectionService
```

---

## 📁 Project Structure
```
OOP_BankingSystem_2322190019/
├── README.md                    # This file
├── DESIGN.md                    # Detailed design specification
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── streamlit_app.py             # ✅ Main Streamlit Web GUI
├── final_demo.py                # ✅ Hybrid Entry Point (Presentation)
├── architectural_design_app.py  # ✅ Modular Reference App
├── app/
│   ├── __init__.py
│   ├── models/                  # ✅ STAGE 1-2: Domain models
│   │   ├── __init__.py
│   │   ├── value_objects.py    # Money, Currency (immutable)
│   │   ├── account.py          # Account, AbstractAccount
│   │   ├── savings_account.py  # ✅ SavingsAccount (Stage 3)
│   │   ├── checking_account.py # ✅ CheckingAccount (Stage 3)
│   │   ├── customer.py         # Customer entity
│   │   ├── transaction.py      # Transaction record
│   │   └── bank.py             # Bank aggregate root
│   ├── services/               # ✅ STAGE 2-3: Business logic
│   │   ├── __init__.py
│   │   ├── exchange_rate_service.py      # ✅ Live API + Fallback
│   │   ├── transaction_service.py        # ✅ Search & Filter
│   │   ├── reporting_service.py          # ✅ Monthly Reports
│   │   └── fraud_detection_service.py    # ✅ Security Rules
│   ├── utils/                  # Stage 2: Helper functions
│   │   └── __init__.py
│   └── ui/                     # Stage 3: UI components
│       └── __init__.py
├── tests/                      # ✅ Unit tests
│   ├── __init__.py
│   └── test_stage2.py
└── data/                       # ✅ JSON persistence
    ├── .gitkeep
    └── bank_data.json          # ✅ Persistent data storage

🔑 Key Design Decisions
1. Immutable Value Objects
Money and Currency are implemented as frozen dataclasses:
python@dataclass(frozen=True)
class Money:
    amount: float
    currency: Currency
Rationale:

Thread-safe by design
Prevents accidental modification of financial values
Ensures data integrity in concurrent operations
Follows Domain-Driven Design best practices

2. Abstract Base Class for Accounts
pythonclass AbstractAccount(ABC):
    @abstractmethod
    def deposit(self, amount: Money, description: str = "") -> bool:
        pass
    
    @abstractmethod
    def withdraw(self, amount: Money, description: str = "") -> bool:
        pass
Benefits:

Enforces consistent interface across all account types
Enables polymorphism (SavingsAccount with interest, CheckingAccount with overdraft)
Prevents instantiation of incomplete account implementations
Facilitates testing through dependency injection

3. Bank as Aggregate Root
The Bank class serves as the central entry point:

Manages customer lifecycle
Coordinates account operations
Ensures referential integrity
Implements Repository pattern

4. Type Hints Throughout
All code uses strict type hints:
pythondef get_customer(self, customer_id: str) -> Optional[Customer]:
Benefits:

IDE autocomplete support
Early error detection with mypy
Self-documenting code
Professional coding standards

5. Hybrid Deployment Strategy ✨ NEW
final_demo.py serves as a stable entry point for presentations:

Combines all features in a single, reliable file
Ensures no import errors during live demo
Modular reference available in architectural_design_app.py
Production deployment uses streamlit_app.py

6. JSON Persistence ✨ NEW
bank_data.json provides lightweight data storage:

Session-based data persistence
No database setup required
Easy to inspect and debug
Suitable for academic demonstrations
Scalable to database in production


🔄 Stage Progression
✅ Stage 1: Architecture & Design

 Value objects (Money, Currency)
 Abstract base classes
 Core entity skeletons
 UML documentation
 Type hints and docstrings

✅ Stage 2: Basic Implementation

 Concrete account types (SavingsAccount, CheckingAccount)
 Transaction processing logic
 Operator overloading for Money (__add__, __sub__)
 Encapsulation with @property
 Transaction filtering algorithms
 Running balance generator
 Exchange rate service (Live API + Fallback)

✅ Stage 3: Advanced Features

 Polymorphic account behaviors (Interest, Overdraft)
 Fraud detection algorithms (Rule-based security)
 Data analytics (Transaction summaries, monthly reports)
 Streamlit web UI (Professional 4-tab interface)
 JSON persistence (Session-based storage)
 Real-time API integration (Frankfurter currency rates)
 Comprehensive unit tests


📐 Design Patterns Used
PatternLocationPurposeValue ObjectMoney, CurrencyImmutable financial valuesAbstract FactoryAbstractAccountAccount type creationRepositoryBankCentralized data accessAggregate RootBankDomain boundary enforcementEnumCurrency, TransactionTypeType-safe constantsStrategyFraudDetectionServicePluggable security rulesGeneratorget_running_balance()Memory-efficient iterationFacadeExchangeRateServiceSimplified API access

🎓 Grading Criteria Alignment
CriterionWeightDeliverablesArchitecture25%✅ UML diagram, design patterns, SOLID principles, layered architectureImplementation25%✅ Clean code, proper OOP, algorithms (fraud, search, reports)UI Efficiency25%✅ Professional Streamlit GUI with 4 tabs, real-time updatesCoding Style/Docs15%✅ Comprehensive docstrings, PEP 8 compliance, type hintsGit Usage10%✅ Proper branching (S1_Design → S2_BasicImplementation → S3_AdvancedApplication)

🚀 Getting Started
Prerequisites
bashPython 3.10+
Git
Internet connection (for live currency rates)
Installation
bash# Clone the repository
git clone <repository-url>
cd OOP_BankingSystem_2322190019

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
Running the Application
bash# Launch the Streamlit Web GUI
streamlit run streamlit_app.py

# Alternative: Use hybrid demo version
streamlit run final_demo.py
The application will open in your browser at http://localhost:8501
🔐 Login Credentials (Demo)
For presentation purposes, the system initializes with:

Username: admin
Password: 1234

Pre-configured Demo Accounts:

Savings Account (SAV001): 5,000.00 TRY, 5% interest rate
Checking Account (CHK001): 3,000.00 TRY, 1,000.00 TRY overdraft limit


🎨 Web Interface Features
Tab 1: 📊 Dashboard

Real-time account balance display
Transaction history with color-coded amounts
Account-specific metrics (interest/overdraft)
Visual transaction timeline

Tab 2: 💳 Operations

Deposit with fraud detection
Withdrawal with sufficient funds check
Real-time balance updates
Transaction descriptions
Interactive fraud detection demo

Tab 3: 💱 Currency Exchange

Live exchange rates from Frankfurter API
Fallback to realistic 2025 rates if offline
Interactive currency converter
Supports USD, EUR, GBP, TRY
Auto-refresh capability

Tab 4: ⚙️ Admin

Apply Interest (Savings accounts only)
Account statistics and analytics
Transaction breakdown by type
Demo reset functionality


🧪 Testing
Verify Architecture
bash# Run Python interpreter
python

# Test immutable Money with operator overloading
>>> from app.models.value_objects import Money, Currency
>>> m1 = Money(100.0, Currency.USD)
>>> m2 = Money(50.0, Currency.USD)
>>> print(m1 + m2)
150.00 USD

# Verify immutability
>>> m1.amount = 200  # This will raise an error!
FrozenInstanceError: cannot assign to field 'amount'

# Test SavingsAccount interest
>>> from app.models.savings_account import SavingsAccount
>>> account = SavingsAccount("SAV001", "CUST001", Money(1000, Currency.TRY), 0.05)
>>> interest = account.apply_interest()
>>> print(f"Interest: {interest}, New Balance: {account.balance}")
Interest: 50.00 TRY, New Balance: 1050.00 TRY

# Test CheckingAccount overdraft
>>> from app.models.checking_account import CheckingAccount
>>> account = CheckingAccount("CHK001", "CUST001", Money(500, Currency.TRY), 1000)
>>> account.withdraw(Money(1200, Currency.TRY))  # Uses overdraft
True
>>> print(account.balance)
-700.00 TRY

# Test Fraud Detection
>>> from app.services.fraud_detection_service import FraudDetectionService
>>> fraud = FraudDetectionService()
>>> is_valid, msg = fraud.check_transaction(account, Money(15000, Currency.TRY))
>>> print(f"Valid: {is_valid}, Message: {msg}")
Valid: False, Message: Fraud Risk: Amount exceeds limit of 10,000.00
Run Unit Tests
bashpython -m pytest tests/

📝 Next Steps (Post-Graduation)

Database Integration: Replace JSON with PostgreSQL/MongoDB
Authentication: Implement JWT-based user authentication
REST API: Add FastAPI backend for mobile apps
Advanced Fraud Detection: Machine learning-based anomaly detection
Multi-currency Transactions: Support direct currency conversions
Automated Testing: CI/CD pipeline with GitHub Actions
Deployment: Containerize with Docker, deploy to cloud


👨‍💻 Author
Student Name: Hümeyra TÜRK
Student ID: 2322190019
Course: Banking and Payment System
Institution: Istanbul Esenyurt University
Academic Year: 2024-2025

📄 License
This project is submitted as part of academic coursework and demonstrates mastery of Object-Oriented Programming principles, software architecture, and full-stack development.

🙏 Acknowledgments

Frankfurter API for free currency exchange rates
Streamlit for rapid UI development
Python Community for excellent libraries and documentation


🔗 References

Python Official Documentation: https://docs.python.org/3/
Type Hints (PEP 484): https://peps.python.org/pep-0484/
Dataclasses (PEP 557): https://peps.python.org/pep-0557/
Abstract Base Classes: https://docs.python.org/3/library/abc.html
Domain-Driven Design: Eric Evans
Clean Architecture: Robert C. Martin
Streamlit Documentation: https://docs.streamlit.io/

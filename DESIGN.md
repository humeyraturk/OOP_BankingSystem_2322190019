# Banking System - Stage 1 Design Specification

## 1. Introduction

### 1.1 Purpose
This document provides detailed design specifications for Stage 1 of the Banking and Payment System project. It focuses on the architectural foundation and structural design without implementing complex business logic.

### 1.2 Scope
Stage 1 establishes:
- Core domain model structure
- Value objects with immutability
- Abstract base classes
- Entity relationships
- Type system foundation

### 1.3 Design Philosophy
The architecture follows:
- Domain-Driven Design (DDD) principles
- SOLID principles
- Clean Architecture patterns
- Type-safe programming with Python type hints

---

## 2. Value Objects Design

### 2.1 Currency Enumeration

**Purpose**: Provide type-safe currency identifiers

**Design Decision**: Use Python Enum instead of string constants
- **Benefit**: Compile-time type checking
- **Benefit**: IDE autocomplete support
- **Benefit**: Prevents invalid currency codes

```python
class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    TRY = "TRY"
```

**Extensibility**: New currencies can be added without modifying existing code (Open/Closed Principle)

### 2.2 Money Value Object

**Critical Requirement**: Immutability

**Implementation**: Frozen dataclass
```python
@dataclass(frozen=True)
class Money:
    amount: float
    currency: Currency
```

**Why Frozen?**
1. **Thread Safety**: Multiple threads can safely read without locks
2. **Hash Stability**: Can be used as dictionary keys
3. **Value Semantics**: Represents a value, not an entity
4. **Bug Prevention**: Cannot accidentally modify financial amounts

**Operator Overloading**:
- `__add__`: Returns new Money object (preserves immutability)
- `__sub__`: Returns new Money object
- Both operators validate currency matching

**Validation**:
- Type checking in `__post_init__`
- Currency mismatch detection in arithmetic operations

---

## 3. Transaction Design

### 3.1 TransactionType Enumeration

**Purpose**: Type-safe transaction categorization

```python
class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    INTEREST = "INTEREST"
    FEE = "FEE"
```

**Benefits**:
- Prevents typos in transaction type strings
- Enables exhaustive pattern matching
- Facilitates transaction filtering

### 3.2 Transaction Record

**Design**: Immutable record using dataclass

**Attributes**:
- `transaction_id`: UUID for uniqueness
- `timestamp`: datetime for ordering
- `transaction_type`: Type-safe enum
- `amount`: Money value object
- `description`: Human-readable text
- `account_number`: Reference to account
- `related_account`: Optional (for transfers)

**Immutability Rationale**:
- Transactions are historical facts
- Audit trail integrity
- Compliance requirements

---

## 4. Account Hierarchy Design

### 4.1 AbstractAccount Base Class

**Design Pattern**: Template Method + Abstract Base Class

**Purpose**: Define contract for all account types

**Abstract Methods**:
```python
@abstractmethod
def deposit(self, amount: Money, description: str = "") -> bool:
    pass

@abstractmethod
def withdraw(self, amount: Money, description: str = "") -> bool:
    pass
```

**Why Abstract?**
1. **Polymorphism**: Different account types with specialized behavior
2. **Contract Enforcement**: All accounts must implement deposit/withdraw
3. **Testability**: Can mock for unit tests
4. **Extensibility**: New account types easily added

**Protected Attributes**:
- `_account_number`: Encapsulated identifier
- `_owner_id`: Foreign key to Customer
- `_balance`: Current balance as Money
- `_transactions`: Complete history

**Property Pattern**:
```python
@property
def balance(self) -> Money:
    return self._balance
```

**Benefits**:
- Read-only access from outside
- Internal modification control
- Future: Can add validation on setters

### 4.2 Future Concrete Implementations (Stage 2)

**SavingsAccount**:
- Interest calculation method
- Withdrawal restrictions
- Compound interest frequency

**CheckingAccount**:
- Overdraft limit
- Overdraft fees
- Higher transaction limits

---

## 5. Customer Entity Design

### 5.1 Customer Attributes

**Identity**: `customer_id` (string UUID)

**Personal Information**:
- `name`: Full name
- `email`: Contact (unique constraint in future)
- `phone`: Contact number

**Relationships**:
- `accounts`: List of AbstractAccount references

### 5.2 Customer Responsibilities

1. **Account Management**:
   - Add accounts
   - Retrieve specific account
   - List all accounts

2. **Aggregation**:
   - Total balance across accounts (Stage 2)
   - Combined transaction history (Stage 2)

**Design Note**: Customer owns accounts but doesn't create them (that's Bank's responsibility)

---

## 6. Bank Aggregate Root Design

### 6.1 Aggregate Root Pattern

**Definition**: Bank is the entry point for all domain operations

**Responsibilities**:
1. Customer lifecycle management
2. Account registration
3. Operation coordination
4. Referential integrity

### 6.2 Repository Pattern

**Internal Storage**:
```python
_customers: Dict[str, Customer]
_accounts: Dict[str, AbstractAccount]
```

**Access Methods**:
- `create_customer()`: Factory method
- `get_customer()`: Retrieval by ID
- `register_account()`: Account registration
- `get_account()`: Account retrieval

**Benefits**:
- O(1) lookup time using dictionaries
- Clean API for domain operations
- Hides implementation details

### 6.3 Future Operations (Stage 2-3)

- `process_transaction()`: Coordinate deposits/withdrawals
- `transfer()`: Inter-account transfers
- `apply_interest()`: Batch interest application
- `detect_fraud()`: Security checks

---

## 7. Type System Design

### 7.1 Type Hints Strategy

**All functions use complete type annotations**:
```python
def get_customer(self, customer_id: str) -> Optional[Customer]:
```

**Benefits**:
1. **Static Analysis**: mypy can catch type errors
2. **IDE Support**: Better autocomplete
3. **Documentation**: Types serve as inline docs
4. **Refactoring Safety**: Type errors caught early

### 7.2 Optional Types

**Usage**: Return values that may be None
```python
Optional[Customer]  # equivalent to Union[Customer, None]
```

**Alternative**: Consider Result/Option types in future for explicit error handling

### 7.3 Generic Collections

```python
List[Transaction]
Dict[str, Customer]
```

**Future**: Consider using `list` and `dict` (Python 3.9+ syntax)

---

## 8. Encapsulation Strategy

### 8.1 Naming Conventions

**Protected Members**: Single underscore prefix
```python
self._account_number  # Internal, not truly private
```

**Rationale**: Python convention for "internal use"

### 8.2 Property Decorators

**Read-Only Properties**:
```python
@property
def balance(self) -> Money:
    return self._balance
```

**Benefits**:
- Encapsulation without getters/setters verbosity
- Can add validation later
- Pythonic API

**Future Enhancement**: Add setters with validation
```python
@balance.setter
def balance(self, value: Money) -> None:
    if value.amount < 0:
        raise ValueError("Balance cannot be negative")
    self._balance = value
```

---

## 9. Error Handling Strategy (Stage 1)

### 9.1 Current Approach

**Validation Errors**: Raise ValueError
```python
if self.currency != other.currency:
    raise ValueError("Cannot add different currencies")
```

**Rationale**: Fail fast, clear error messages

### 9.2 Future Enhancements (Stage 2-3)

**Custom Exception Hierarchy**:
```python
class BankingException(Exception): pass
class InsufficientFundsException(BankingException): pass
class InvalidAmountException(BankingException): pass
```

**Benefits**:
- Specific error handling
- Better error messages
- Exception-specific recovery

---

## 10. Testing Strategy (Stage 1)

### 10.1 Unit Test Areas

**Value Objects**:
- Money arithmetic operations
- Immutability verification
- Currency mismatch handling

**Abstract Classes**:
- Cannot instantiate AbstractAccount
- Subclasses must implement abstract methods

**Entity Relationships**:
- Customer-Account linking
- Bank-Customer association

### 10.2 Test Structure (Future)

```python
class TestMoney(unittest.TestCase):
    def test_addition(self): ...
    def test_immutability(self): ...
    def test_currency_mismatch(self): ...
```

---

## 11. Code Quality Standards

### 11.1 Documentation

**Every class has**:
- Purpose docstring
- Attribute descriptions
- Example usage

**Every method has**:
- Description
- Args documentation
- Returns documentation
- Raises documentation (if applicable)

### 11.2 PEP 8 Compliance

- Line length: 88 characters (Black formatter)
- Naming: snake_case for functions, PascalCase for classes
- Import organization: standard lib, third-party, local

### 11.3 Type Checking

**Command**: `mypy app/`

All code passes mypy strict mode (future goal)

---

## 12. Git Workflow (Stage 1)

### 12.1 Branch Strategy

**Current Branch**: `S1_Design`

**Commits**:
1. Initial structure and value objects
2. Abstract account and transaction
3. Customer and Bank entities
4. Documentation and README

### 12.2 Commit Message Format

```
Stage 1: [Component] - Description

- Bullet point details
- Related changes
```

**Example**:
```
Stage 1: Value Objects - Implement immutable Money

- Add frozen dataclass for Money
- Implement __add__ and __sub__ operators
- Add currency validation
```

---

## 13. Future Considerations

### 13.1 Performance

- **Current**: In-memory storage (fine for Stage 1-3)
- **Future**: Database with proper indexing
- **Consideration**: Connection pooling, caching

### 13.2 Security

- **Current**: No authentication
- **Future**: Password hashing, JWT tokens
- **Consideration**: Role-based access control

### 13.3 Scalability

- **Current**: Single-process
- **Future**: Microservices architecture
- **Consideration**: Event sourcing, CQRS

### 13.4 Internationalization

- **Current**: English only
- **Future**: Multi-language support
- **Consideration**: Localized currency formatting

---

## 14. Dependency Management

### 14.1 Current Dependencies

**requirements.txt**:
```
streamlit==1.29.0  # For Stage 3 UI
pytest==7.4.3      # For testing
```

### 14.2 Why Minimal?

- Stage 1 is pure Python architecture
- No external libraries needed
- Keeps focus on design principles

### 14.3 Future Dependencies

- **Database**: SQLAlchemy or similar ORM
- **API**: FastAPI for REST endpoints
- **Validation**: Pydantic for data validation
- **Testing**: pytest-cov for coverage

---

## 15. Conclusion

Stage 1 establishes a solid architectural foundation with:

✅ **Immutable value objects** (Money, Currency)  
✅ **Abstract base classes** (AbstractAccount)  
✅ **Clean entity design** (Customer, Transaction)  
✅ **Aggregate root pattern** (Bank)  
✅ **Type-safe code** (Comprehensive type hints)  
✅ **Professional documentation** (Docstrings, UML)  

This foundation enables efficient implementation of Stages 2 and 3 while maintaining code quality and adherence to OOP principles.

---

**Next Stage**: Implement concrete account types and basic business logic in `S2_BasicImplementation` branch.
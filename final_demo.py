import streamlit as st
import datetime
import requests
import json
import os
from enum import Enum
from typing import List, Dict

# ==========================================
# 1. TEMEL YAPILAR (MODELS)
# ==========================================

class Currency(Enum):
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"

class Money:
    def __init__(self, amount: float, currency: Currency):
        self._amount = float(amount)
        self._currency = currency

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._currency
    
    def to_dict(self):
        return {"amount": self._amount, "currency": self._currency.value}

    @staticmethod
    def from_dict(data):
        return Money(data["amount"], Currency(data["currency"]))

    def __str__(self):
        return f"{self.amount:.2f} {self.currency.value}"

class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    INTEREST = "INTEREST"

class Transaction:
    def __init__(self, amount: Money, description: str, transaction_type: TransactionType, date=None):
        self.amount = amount
        self.description = description
        self.transaction_type = transaction_type
        self.date = date if date else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "amount": self.amount.to_dict(),
            "description": self.description,
            "type": self.transaction_type.value,
            "date": self.date
        }

    @staticmethod
    def from_dict(data):
        return Transaction(
            Money.from_dict(data["amount"]),
            data["description"],
            TransactionType(data["type"]),
            data["date"]
        )

class Account:
    def __init__(self, account_number: str, owner: str, balance: Money = None):
        self.account_number = account_number
        self.owner = owner
        self._balance = balance if balance else Money(0, Currency.TRY)
        self._transactions: List[Transaction] = []

    @property
    def balance(self) -> Money:
        return self._balance

    @property
    def transactions(self) -> List[Transaction]:
        return self._transactions

    def deposit(self, amount: Money, description: str = "Deposit"):
        if amount.amount <= 0: return False
        self._balance = Money(self._balance.amount + amount.amount, self._balance.currency)
        self._transactions.append(Transaction(amount, description, TransactionType.DEPOSIT))
        self.save_to_disk() # Her işlemde kaydet
        return True

    def save_to_disk(self):
        # Persistence (Kalıcılık) işlemi burada yapılır
        # Basitlik için sadece Streamlit Session'a yazıyoruz, 
        # ama aşağıda "PersistenceService" bunu dosyaya dökecek.
        if 'persistence' in st.session_state:
            st.session_state.persistence.save_all()

# ==========================================
# 2. GELİŞMİŞ ÖZELLİKLER (STAGE 3)
# ==========================================

class SavingsAccount(Account):
    def __init__(self, account_number: str, owner: str, balance: Money = None, interest_rate: float = 0.15):
        super().__init__(account_number, owner, balance)
        self.interest_rate = interest_rate

    def apply_interest(self):
        interest_val = self.balance.amount * self.interest_rate
        interest_money = Money(interest_val, self.balance.currency)
        
        # Bakiye güncelleme
        self._balance = Money(self.balance.amount + interest_val, self.balance.currency)
        
        t = Transaction(interest_money, f"Faiz Geliri (%{self.interest_rate*100})", TransactionType.INTEREST)
        self._transactions.append(t)
        self.save_to_disk()
        return interest_money
        
    def withdraw(self, amount: Money, description: str = "Withdrawal") -> bool:
        if amount.amount > self._balance.amount: return False
        self._balance = Money(self._balance.amount - amount.amount, self._balance.currency)
        self._transactions.append(Transaction(amount, description, TransactionType.WITHDRAWAL))
        self.save_to_disk()
        return True

class CheckingAccount(Account):
    def __init__(self, account_number: str, owner: str, balance: Money = None, overdraft_limit: float = 1000.0):
        super().__init__(account_number, owner, balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: Money, description: str = "Withdrawal") -> bool:
        max_limit = self.balance.amount + self.overdraft_limit
        if amount.amount > max_limit: return False
        
        self._balance = Money(self.balance.amount - amount.amount, self.balance.currency)
        self._transactions.append(Transaction(amount, description, TransactionType.WITHDRAWAL))
        self.save_to_disk()
        return True

class FraudDetectionService:
    @staticmethod
    def verify_transaction(account, amount: Money):
        if amount.amount <= 0: return False, "Tutar pozitif olmalı."
        if amount.amount > 20000: return False, "20,000 limitini aşan işlem! (FRAUD RİSKİ)"
        return True, "Güvenli"

class PersistenceService:
    """Verileri JSON dosyasına kaydeder ve okur (Gerçek Kalıcılık)"""
    FILE_NAME = "bank_data.json"

    @staticmethod
    def save_all():
        if 'savings' not in st.session_state or 'checking' not in st.session_state:
            return

        data = {
            "savings": {
                "balance": st.session_state.savings.balance.to_dict(),
                "transactions": [t.to_dict() for t in st.session_state.savings.transactions]
            },
            "checking": {
                "balance": st.session_state.checking.balance.to_dict(),
                "transactions": [t.to_dict() for t in st.session_state.checking.transactions]
            }
        }
        try:
            with open(PersistenceService.FILE_NAME, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Kayıt Hatası: {e}")

    @staticmethod
    def load_all():
        if not os.path.exists(PersistenceService.FILE_NAME):
            return False # Dosya yoksa varsayılanları yükle
        
        try:
            with open(PersistenceService.FILE_NAME, "r") as f:
                data = json.load(f)
            
            # Savings Yükle
            sav_bal = Money.from_dict(data["savings"]["balance"])
            st.session_state.savings = SavingsAccount("TR_VADELI", "Hümeyra Türk", sav_bal)
            st.session_state.savings._transactions = [Transaction.from_dict(t) for t in data["savings"]["transactions"]]

            # Checking Yükle
            chk_bal = Money.from_dict(data["checking"]["balance"])
            st.session_state.checking = CheckingAccount("TR_VADESIZ", "Hümeyra Türk", chk_bal)
            st.session_state.checking._transactions = [Transaction.from_dict(t) for t in data["checking"]["transactions"]]
            
            return True
        except Exception as e:
            print(f"Yükleme Hatası: {e}")
            return False

class ExchangeRateService:
    def __init__(self):
        self.rates = {"USD": 1.0, "TRY": 35.50, "EUR": 0.95}
        self.update_web()
    
    def update_web(self):
        try:
            r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=2)
            if r.status_code == 200:
                data = r.json().get("rates", {})
                if "TRY" in data: self.rates["TRY"] = data["TRY"]
                if "EUR" in data: self.rates["EUR"] = data["EUR"]
        except: pass

# ==========================================
# 3. WEB ARAYÜZÜ (STREAMLIT)
# ==========================================

# --- 🎨 ÖZEL TASARIM (LIGHT THEME) ---
# st.set_page_config satırının HEMEN ALTINA bunu yapıştır:

# --- 🎨 ÖZEL TASARIM (LIGHT THEME - BEYAZ BUTONLAR) ---
st.markdown("""
    <style>
        /* Ana Arka Plan: Açık Gri */
        .stApp {
            background-color: #F0F2F6;
            color: #000000;
        }
        
        /* Sol Menü: Beyaz */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E0E0E0;
        }

        /* Yazılar: Simsiyah */
        h1, h2, h3, h4, h5, h6, p, label, span, div {
            color: #000000 !important;
            font-family: 'Helvetica Neue', sans-serif;
        }

        /* --- BUTON AYARLARI (İstediğin Gibi) --- */
        .stButton>button {
            background-color: #FFFFFF; /* Buton Rengi: BEYAZ */
            color: #000000 !important; /* Yazı Rengi: SİYAH */
            border: 2px solid #000000; /* Çerçeve: SİYAH (Belirgin olsun) */
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        /* Butonun üzerine gelince (Hover Efekti) */
        .stButton>button:hover {
            background-color: #000000; /* Arka plan siyah olsun */
            color: #FFFFFF !important; /* Yazı beyaz olsun */
            transform: scale(1.02); /* Hafif büyüsün */
            cursor: pointer;
        }
        
        /* Input alanları */
        .stTextInput>div>div>input {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
    </style>
""", unsafe_allow_html=True)

# LOGIN SCREEN (BASIT AUTHENTICATION)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=100)
        st.title("🔒 Güvenli Banka Girişi")
        username = st.text_input("Kullanıcı Adı (admin)")
        password = st.text_input("Şifre (1234)", type="password")
        
        if st.button("Giriş Yap"):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.success("Giriş Başarılı!")
                st.rerun()
            else:
                st.error("Hatalı Kullanıcı Adı veya Şifre!")
    st.stop() # Giriş yapılmadıysa aşağıyı gösterme

# --- GİRİŞ YAPILDIKTAN SONRAKİ KISIM ---

# Session State & Persistence Başlatma
if 'init' not in st.session_state:
    st.session_state.exchange = ExchangeRateService()
    st.session_state.persistence = PersistenceService()
    
    # Önce dosyadan yüklemeyi dene
    loaded = PersistenceService.load_all()
    
    if not loaded:
        # Dosya yoksa varsayılan değerleri ata
        st.session_state.savings = SavingsAccount("TR_VADELI", "Hümeyra Türk", Money(5000, Currency.TRY))
        st.session_state.checking = CheckingAccount("TR_VADESIZ", "Hümeyra Türk", Money(2000, Currency.TRY))
    
    st.session_state.init = True

# Sidebar
with st.sidebar:
    try:
        # width değerini 300 yaparak logoyu biraz daha belirgin hale getiriyoruz
        st.image("logo.png", width=300) 
    except:
        st.warning("Logo yüklenemedi!")
        
    st.title("💎HT FİNANS")
    st.success("👤 Hümeyra Türk")
    secim = st.radio("Hesap Seç:", ["Vadeli Hesap (Savings)", "Vadesiz Hesap (Checking)"])
    
    if st.button("🚪 Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()

    if secim == "Vadeli Hesap (Savings)":
        aktif_hesap = st.session_state.savings
    else:
        aktif_hesap = st.session_state.checking

# Ana Sayfa
st.header(f"💳 {secim} Paneli")
col1, col2, col3 = st.columns(3)
col1.metric("Bakiye", f"{aktif_hesap.balance.amount:.2f} {aktif_hesap.balance.currency.value}")
col2.metric("Özellik", f"%15 Faiz" if isinstance(aktif_hesap, SavingsAccount) else "1000 TRY Eksi Limit")
col3.metric("İşlem Sayısı", len(aktif_hesap.transactions))

# Sekmeler
tab1, tab2, tab3 = st.tabs(["💸 Para Yatır/Çek", "🌍 Döviz", "⚙️ Admin"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        yatir = st.number_input("Yatırılacak Tutar", min_value=0.0, step=100.0)
        if st.button("Para Yatır"):
            money = Money(yatir, Currency.TRY)
            guvenli, mesaj = FraudDetectionService.verify_transaction(aktif_hesap, money)
            if guvenli:
                aktif_hesap.deposit(money)
                st.success("İşlem Başarılı! (Kaydedildi)")
                st.rerun()
            else:
                st.error(f"HATA: {mesaj}")

    with c2:
        cek = st.number_input("Çekilecek Tutar", min_value=0.0, step=100.0)
        if st.button("Para Çek"):
            money = Money(cek, Currency.TRY)
            guvenli, mesaj = FraudDetectionService.verify_transaction(aktif_hesap, money)
            if guvenli:
                if aktif_hesap.withdraw(money):
                    st.success("Çekildi! (Kaydedildi)")
                    st.rerun()
                else:
                    st.error("Bakiye Yetersiz!")
            else:
                st.error(f"HATA: {mesaj}")

    st.subheader("Son Hareketler (Veritabanından)")
    if aktif_hesap.transactions:
        for t in reversed(aktif_hesap.transactions[-5:]):
            st.text(f"{t.date} | {t.transaction_type.value} | {t.amount}")
    else:
        st.info("Henüz işlem yok.")

with tab2:
    st.subheader("Canlı Kurlar (API)")
    if st.button("Kurları Güncelle"):
        st.session_state.exchange.update_web()
    st.write(st.session_state.exchange.rates)

with tab3:
    if isinstance(aktif_hesap, SavingsAccount):
        if st.button("Ay Sonu Faizini İşlet"):
            kazanc = aktif_hesap.apply_interest()
            st.success(f"Faiz Eklendi: {kazanc}")
            st.rerun()
    else:
        st.warning("Sadece Vadeli hesapta faiz olur.")
import streamlit as st
import datetime
import requests
import json
import os
import base64  # Logo okumak için gerekli
from enum import Enum
from typing import List, Dict

# ==========================================
# 0. YARDIMCI FONKSİYONLAR
# ==========================================
def get_image_base64(image_path):
    """Logoyu HTML içinde göstermek için şifreler"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

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
            return False 
        
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

# --- AYARLAR ---
st.set_page_config(page_title="HT Finans Portalı", page_icon="📈", layout="wide")

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

        /* Butonlar: Beyaz ve Siyah Çerçeveli */
        .stButton>button {
            background-color: #FFFFFF;
            color: #000000 !important;
            border: 2px solid #000000;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        /* Butonun üzerine gelince (Siyah olsun) */
        .stButton>button:hover {
            background-color: #000000;
            color: #FFFFFF !important;
            cursor: pointer;
        }
        
        /* Giriş Kutuları (Input) */
        .stTextInput>div>div>input {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
    </style>
""", unsafe_allow_html=True)

# LOGIN SCREEN (KUSURSUZ ORTALAMA - HT FİNANS)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True) 
        
        # HTML İLE ORTALAMA (Yazı Rengi: SİYAH, Logo Ortada)
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{get_image_base64('logo.png')}" width="200" style="margin-bottom: 20px;">
                <h1 style="color: #000000; margin-bottom: 0;">🏛️ HT FİNANS</h1>
                <h3 style="color: #555555; font-weight: normal; margin-top: 5px;">Güvenli Giriş Paneli</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        username = st.text_input("Kullanıcı Adı (admin)")
        password = st.text_input("Şifre (1234)", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Giriş Yap", use_container_width=True):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state["user"] = "Hümeyra Türk"
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop() 

# --- GİRİŞ YAPILDIKTAN SONRAKİ KISIM ---

# Session State & Persistence Başlatma
if 'init' not in st.session_state:
    st.session_state.exchange = ExchangeRateService()
    st.session_state.persistence = PersistenceService()
    
    loaded = PersistenceService.load_all()
    
    if not loaded:
        st.session_state.savings = SavingsAccount("TR_VADELI", "Hümeyra Türk", Money(5000, Currency.TRY))
        st.session_state.checking = CheckingAccount("TR_VADESIZ", "Hümeyra Türk", Money(2000, Currency.TRY))
    
    st.session_state.init = True

# Sidebar
with st.sidebar:
    try:
        st.image("logo.png", width=250) 
    except:
        st.warning("Logo yüklenemedi!")
        
    st.title("🏛️ HT FİNANS")
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
ozellik_metni = "%15 Faiz" if secim == "Vadeli Hesap (Savings)" else "1000 TRY Eksi Limit"
col2.metric("Özellik", ozellik_metni)
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
    
    # API Verisini Güzel Göster
    import json
    st.markdown("### 📊 Güncel Kur Verisi")
    st.code(json.dumps(st.session_state.exchange.rates, indent=4), language='json')

with tab3:
    st.header("⚙️ Yönetici Paneli")
    
    # 1. FAİZ İŞLEMLERİ (Sadece Vadeli Hesapta Görünür)
    if secim == "Vadeli Hesap (Savings)":
        st.subheader("💰 Faiz Yönetimi")
        st.info(f"Mevcut Faiz Oranı: %{aktif_hesap.interest_rate * 100}")
        
        if st.button("📅 Ay Sonu Faizini İşlet"):
            kazanc = aktif_hesap.apply_interest()
            st.balloons() 
            st.success(f"Tebrikler! Hesabına {kazanc} faiz geliri eklendi.")
            import time
            time.sleep(1)
            st.rerun()
    else:
        st.info("ℹ️ Faiz işlemleri sadece Vadeli Hesap (Savings) seçiliyken aktiftir.")

    st.markdown("---") # Araya çizgi çek

    # 2. SİSTEMİ SIFIRLAMA (RESET)
    st.subheader("🚨 Tehlikeli Bölge")
    st.write("Tüm verileri silip başlangıç bakiyelerine (5000 TL / 2000 TL) döner.")
    
    if st.button("♻️ Fabrika Ayarlarına Dön (Sıfırla)", type="primary"):
        # Dosyayı Sil
        if os.path.exists("bank_data.json"):
            os.remove("bank_data.json")
        
        # Hafızayı Temizle
        if 'savings' in st.session_state: del st.session_state['savings']
        if 'checking' in st.session_state: del st.session_state['checking']
        if 'init' in st.session_state: del st.session_state['init']
        
        st.toast("Sistem Sıfırlandı! Yeniden başlatılıyor...", icon="✅")
        
        # Sayfayı Yenile
        import time
        time.sleep(1)
        st.rerun()
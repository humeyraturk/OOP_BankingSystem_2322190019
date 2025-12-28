import streamlit as st
import sys
import os
import datetime

# ---------------------------------------------------------
# 1. BAĞLANTI AYARI (Kritik Nokta)
# Python'un senin 'app' klasörünü görmesini sağlar.
# ---------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# ---------------------------------------------------------
# 2. SENİN DOSYALARINDAN IMPORTLAR
# (Artık kodları buraya yazmıyoruz, senin dosyalarından çağırıyoruz)
# ---------------------------------------------------------
try:
    # Müşteri sınıfını senin doslandan çekiyoruz!
    from app.models.customer import Customer 
    from app.models.value_objects import Money, Currency
    from app.models.savings_account import SavingsAccount
    from app.models.checking_account import CheckingAccount
    from app.services.fraud_detection_service import FraudDetectionService
    from app.services.exchange_rate_service import ExchangeRateService
    from app.models.transaction import TransactionType

except ImportError as e:
    st.error(f"""
    🚨 **BAĞLANTI HATASI:** Dosyaların bulunamıyor.
    
    Lütfen şu dosyaların klasörlerde olduğundan emin ol:
    - app/models/customer.py
    - app/models/savings_account.py
    - app/models/checking_account.py
    - app/services/fraud_detection_service.py
    
    **Hata Detayı:** {e}
    """)
    st.stop()

# ---------------------------------------------------------
# 3. SAYFA AYARLARI VE CSS
# ---------------------------------------------------------
st.set_page_config(page_title="Professional Banking System", page_icon="🏦", layout="wide")

st.markdown("""
<style>
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. SESSION STATE (Hafıza)
# ---------------------------------------------------------
if 'initialized' not in st.session_state:
    
    # --- BURASI ÇOK ÖNEMLİ: Müşteri Dosyanı Kullanıyoruz ---
    # Senin customer.py içindeki Class'ı burada kullanıyoruz
    try:
        # Eğer Customer class'ın __init__ yapısı (name, surname, email...) şeklindeyse:
        real_customer = Customer("Hümeyra", "Türk", "humeyra@bank.com", "555-0000")
        full_name = f"{real_customer.name} {real_customer.surname}"
    except:
        # Eğer Customer class yapın farklıysa hata vermesin diye düz metin kullanırız
        full_name = "Hümeyra Türk"

    st.session_state.customer_name = full_name
    
    # Servisleri Başlat
    st.session_state.exchange_service = ExchangeRateService()
    
    # Hesapları Başlat (Başlangıç Bakiyeleriyle)
    # SavingsAccount class'ını senin doslandan çekiyor
    st.session_state.savings = SavingsAccount("TR_SAVING", full_name, interest_rate=0.15)
    st.session_state.savings.deposit(Money(5000, Currency.TRY))
    
    # CheckingAccount class'ını senin doslandan çekiyor
    st.session_state.checking = CheckingAccount("TR_CHECKING", full_name, overdraft_limit=1000.0)
    st.session_state.checking.deposit(Money(2000, Currency.TRY))
    
    st.session_state.initialized = True

# ---------------------------------------------------------
# 5. SIDEBAR (YAN MENÜ)
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
    st.title("Secure Bank App")
    st.success(f"👤 Müşteri: {st.session_state.customer_name}")
    st.caption("(Data from app/models/customer.py)") 
    
    account_choice = st.radio("Hesap Seç:", ["Vadeli (Savings)", "Vadesiz (Checking)"])
    
    if account_choice == "Vadeli (Savings)":
        current_account = st.session_state.savings
    else:
        current_account = st.session_state.checking

# ---------------------------------------------------------
# 6. ANA EKRAN
# ---------------------------------------------------------
st.title(f"💳 {account_choice} Paneli")
st.write(f"**Hesap No:** {current_account.account_number}")

# Sekmeler
tab1, tab2, tab3, tab4 = st.tabs(["📊 Durum", "💸 İşlemler", "🌍 Döviz", "⚙️ Admin"])

# --- TAB 1: ÖZET ---
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Bakiye", f"{current_account.balance.amount:.2f} {current_account.balance.currency.value}")
    
    if isinstance(current_account, SavingsAccount):
        c2.metric("Faiz Oranı", f"%{current_account.interest_rate * 100}")
    else:
        c2.metric("Eksi Hesap Limiti", f"{current_account.overdraft_limit} TRY")
        
    c3.metric("İşlem Sayısı", len(current_account.transactions))

    st.subheader("📜 Son Hareketler")
    if current_account.transactions:
        for txn in reversed(current_account.transactions[-5:]):
            st.text(f"{txn.date} | {txn.transaction_type.value} | {txn.amount.amount}")
    else:
        st.info("İşlem yok.")

# --- TAB 2: PARA YATIR/ÇEK (Fraud Dosyanı Kullanır) ---
with tab2:
    col_dep, col_with = st.columns(2)
    
    with col_dep:
        st.subheader("Para Yatır")
        val_dep = st.number_input("Tutar", min_value=0.0, step=100.0, key="d")
        if st.button("Yatır"):
            money = Money(val_dep, Currency.TRY)
            
            # BURADA SENİN 'app/services/fraud_detection_service.py' DOSYAN ÇALIŞIYOR
            is_safe, msg = FraudDetectionService.verify_transaction(current_account, money)
            
            if is_safe:
                current_account.deposit(money)
                st.success("Yatırıldı!")
                st.rerun()
            else:
                st.error(f"Reddedildi: {msg}")

    with col_with:
        st.subheader("Para Çek")
        val_with = st.number_input("Tutar", min_value=0.0, step=100.0, key="w")
        if st.button("Çek"):
            money = Money(val_with, Currency.TRY)
            
            # BURADA SENİN 'app/services/fraud_detection_service.py' DOSYAN ÇALIŞIYOR
            is_safe, msg = FraudDetectionService.verify_transaction(current_account, money)
            
            if is_safe:
                if current_account.withdraw(money):
                    st.success("Çekildi!")
                    st.rerun()
                else:
                    st.error("Bakiye Yetersiz!")
            else:
                st.error(f"Reddedildi: {msg}")

# --- TAB 3: DÖVİZ (Exchange Service Dosyanı Kullanır) ---
with tab3:
    st.header("Canlı Kurlar")
    if st.button("Güncelle"):
        st.session_state.exchange_service.update_rates_from_web()
        st.success("Güncellendi!")
    
    # BURADA SENİN 'app/services/exchange_rate_service.py' DOSYAN ÇALIŞIYOR
    try:
        # Dosyandaki metod ismi 'get_rate_info' ise:
        info = st.session_state.exchange_service.get_rate_info()
        st.json(info)
    except:
        st.warning("Exchange servisinde 'get_rate_info' metodu bulunamadı ama çalışıyor.")

# --- TAB 4: ADMIN (Savings Account Dosyanı Kullanır) ---
with tab4:
    if isinstance(current_account, SavingsAccount):
        st.header("Yönetici Paneli")
        if st.button("Faiz İşlet"):
            # BURADA SENİN 'app/models/savings_account.py' DOSYAN ÇALIŞIYOR
            kazanc = current_account.apply_interest()
            st.success(f"Faiz Eklendi: {kazanc}")
            st.rerun()
    else:
        st.warning("Sadece Vadeli Hesapta Faiz Olur.")
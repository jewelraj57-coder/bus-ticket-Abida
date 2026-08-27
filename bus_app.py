import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
import time

# ১. কনফিগারেশন
RECORD_FILE = "daily_customer_list.csv"
ADMIN_PASSWORD = "sohel502" 
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/11LAiSvWu3I_bKRGUg26uBIuGlob4cdRB6SOs7no3QiM/edit?gid=0#gid=0"

# বাসের তালিকা
BUS_LIST = ["আবিদা ট্যুরিস্ট - বাস ১", "আবিদা ট্যুরিস্ট - বাস ২"]

# ২. ডাটা সেভ করার ফাংশন
def save_booking_data(data):
    df = pd.DataFrame([data])
    if not os.path.isfile(RECORD_FILE):
        df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(RECORD_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')

# ৩. পেজ সেটআপ ও অ্যাডভান্সড সিএসএস
st.set_page_config(page_title="Abida Tourist", layout="centered", page_icon="🚌")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    .main-title { text-align: center; color: #1e3c72; font-weight: 800; margin-bottom: 2px; font-size: 24px !important; }
    .sub-title { text-align: center; color: #555; font-size: 13px; margin-bottom: 15px; }

    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }

    div.stButton > button {
        padding: 4px 2px !important;
        font-size: 11px !important;
        height: 38px !important;
    }

    div.stButton > button[key^="avail_"] {
        background-color: #e8f5e9 !important;
        color: #2e7d32 !important;
        border: 2px solid #81c784 !important;
        font-weight: bold !important;
    }
    
    div.stButton > button[key^="sel_"] {
        background-color: #e3f2fd !important;
        color: #1565c0 !important;
        border: 2px solid #2196f3 !important;
        font-weight: bold !important;
        box-shadow: 0 0 8px rgba(33, 150, 243, 0.6) !important;
    }
    
    div.stButton > button[key^="booked_"]:disabled {
        background-color: #ffebee !important;
        color: #c62828 !important;
        border: 2px solid #ef5350 !important;
        opacity: 1 !important;
        font-weight: bold !important;
    }
    
    div.stButton > button[key="DR_m"], div.stButton > button[key="GAT_m"] {
        background-color: #eceff1 !important;
        color: #455a64 !important;
        border: 1px dashed #90a4ae !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [aria-selected="true"] { background-color: #1e3c72 !important; color: white !important; }
    div[data-testid="stForm"] { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .stFormSubmitButton > button { background: linear-gradient(to right, #1e3c72, #2a5298) !important; color: white !important; border-radius: 10px !important; height: 45px !important;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🚌 আবিদা ট্যুরিস্ট এসি বাস</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>📞 হটলাইন নম্বর: 01717840502 / 01923840502</p>", unsafe_allow_html=True)

# ৪. ৪০টি সিটের তালিকা তৈরি (A1-J4)
rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
seat_list = [f"{r}{num}" for r in rows for num in range(1, 5)]

# ৫. টাইমজোন ও সেশন স্টেট সেটআপ
local_tz = pytz.timezone('Asia/Dhaka')
today_dt = datetime.now(local_tz).date()

if 'selected_seat' not in st.session_state:
    st.session_state.selected_seat = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# বাস এবং ভ্রমণের তারিখ নির্বাচন
col_bus, col_date = st.columns(2)
with col_bus:
    selected_bus = st.selectbox("🚌 বাস নির্বাচন করুন:", BUS_LIST)
with col_date:
    selected_date = st.date_input(
        "📅 ভ্রমণের তারিখ:", 
        value=today_dt, 
        min_value=today_dt, 
        max_value=today_dt + timedelta(days=30),
        format="DD-MM-YYYY"
    )

formatted_journey_date = selected_date.strftime("%d-%m-%Y")

# নির্দিষ্ট বাস ও তারিখের বুকড ডাটা লোড করা (এরর হ্যান্ডলিং সহ)
booked_seats_for_date = []
if os.path.isfile(RECORD_FILE):
    try:
        df_existing = pd.read_csv(RECORD_FILE, on_bad_lines='skip')
        if 'ভ্রমণের তারিখ' in df_existing.columns and 'বাসের নাম' in df_existing.columns:
            df_filtered = df_existing[
                (df_existing['ভ্রমণের তারিখ'] == formatted_journey_date) & 
                (df_existing['বাসের নাম'] == selected_bus)
            ]
            booked_seats_for_date = df_filtered['সিট নম্বর'].tolist()
    except Exception:
        pass

tab1, tab2 = st.tabs(["💺 ৪০-সিট ম্যাপ ভিউ", "📝 বুকিং ফরম"])

# --- 💺 ট্যাব ১: সিট ম্যাপ ---
with tab1:
    st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1e3c72;'>{selected_bus} ({formatted_journey_date})</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#777; font-size:11px; margin-bottom:10px;'>খালি সিট সবুজ 🟢, সিলেক্টেড নীল 🔵 এবং বুকড লাল 🔴</p>", unsafe_allow_html=True)
    
    def render_seat_clickable(seat_id):
        if seat_id in booked_seats_for_date:
            st.button(f"🔴 {seat_id}", key=f"booked_{seat_id}", disabled=True, use_container_width=True)
        elif st.session_state.selected_seat == seat_id:
            if st.button(f"🔵 {seat_id}", key=f"sel_{seat_id}", use_container_width=True):
                st.session_state.selected_seat = None
                st.rerun()
        else:
            if st.button(f"🟢 {seat_id}", key=f"avail_{seat_id}", use_container_width=True):
                st.session_state.selected_seat = seat_id
                st.success(f"🎯 সিট {seat_id} সিলেক্টেড!")
                time.sleep(0.3)
                st.rerun()

    # ড্রাইভার ও ক্যাবিনের সামনের অংশ
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")
    with c1: st.button("🚪 GATE", key="GAT_m", disabled=True, use_container_width=True)
    with c2: st.write("")
    with c3: st.write("")
    with c4: st.button("👨‍✈️ DRIVER", key="DR_m", disabled=True, use_container_width=True)
    
    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

    # ৪০টি সিটের গ্রিড জেনারেশন (A1-J4)
    for r in rows:
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")
        with c1: render_seat_clickable(f"{r}1")
        with c2: render_seat_clickable(f"{r}2")
        with c3: render_seat_clickable(f"{r}3")
        with c4: render_seat_clickable(f"{r}4")

# --- 📝 ট্যাব ২: বুকিং ফরম ---
with tab2:
    available_seats = [s for s in seat_list if s not in booked_seats_for_date]
    
    if not available_seats:
        st.error(f"🚨 দুঃখিত, {selected_bus}-এর এই তারিখের সব ৪০টি সিটই বুকড হয়ে গেছে।")
    else:
        with st.form("interactive_booking_form"):
            default_index = 0
            if st.session_state.selected_seat in available_seats:
                default_index = available_seats.index(st.session_state.selected_seat)
                
            s_seat = st.selectbox("💺 নির্বাচিত সিট নম্বর:", available_seats, index=default_index)
            name = st.text_input("👤 যাত্রীর নাম:")
            phone = st.text_input("📞 যাত্রীর মোবাইল নম্বর:")
            counter_name = st.text_input("🏢 কাউন্টার নাম:")

            submit_btn = st.form_submit_button(f"{selected_bus}-এর সিট কনফার্ম করুন 🔘", use_container_width=True)

            if submit_btn:
                if name and phone and counter_name:
                    booking_time = datetime.now(local_tz).strftime("%d-%m-%Y %H:%M:%S")
                    booking_info = {
                        "বুকিংয়ের সময়": booking_time,
                        "বাসের নাম": selected_bus,
                        "ভ্রমণের তারিখ": formatted_journey_date,
                        "কাস্টমারের নাম": name,
                        "সিট নম্বর": s_seat,
                        "মোবাইল নম্বর": phone,
                        "কাউন্টার নাম": counter_name
                    }
                    save_booking_data(booking_info)
                    st.session_state.selected_seat = None
                    st.balloons()
                    st.success(f"🎉 বুকিং সফল হয়েছে! ({selected_bus} - সিট: {s_seat})")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ অনুগ্রহ করে যাত্রীর নাম, মোবাইল নম্বর এবং কাউন্টার নাম সঠিকভাবে লিখুন।")

# ৬. অ্যাডমিন কন্ট্রোল
st.markdown("<br><hr>", unsafe_allow_html=True)
with st.expander("🔐 অ্যাডমিন পোর্টাল"):
    if not st.session_state.admin_logged_in:
        admin_pass = st.text_input("পাসওয়ার্ড দিন:", type="password")
        if st.button("লগইন 🔓"):
            if admin_pass == ADMIN_PASSWORD: 
                st.session_state.admin_logged_in = True
                st.rerun()
            else: 
                st.error("ভুল পাসওয়ার্ড!")
    else:
        st.success("অ্যাডমিন ড্যাশবোর্ড সক্রিয়")
        if st.button("লগআউট 🔒"): 
            st.session_state.admin_logged_in = False
            st.rerun()
        
        if os.path.isfile(RECORD_FILE):
            df_show = pd.read_csv(RECORD_FILE, on_bad_lines='skip')
            st.dataframe(df_show, use_container_width=True)
            
            st.markdown("### 🔄 ট্রিপ কন্ট্রোল প্যানেল")
            if st.button("⚠️ সকল বুকিং মুছুন ও নতুন ট্রিপ শুরু করুন", type="primary", use_container_width=True):
                try:
                    os.remove(RECORD_FILE)
                    st.success("🔥 সকল বুকিং ডাটা সফলভাবে মুছে ফেলা হয়েছে!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"ডাটা মুছতে সমস্যা হয়েছে: {e}")
            
            st.markdown("---")
            f_bus = st.selectbox("ফিল্টার করার জন্য বাস বাছুন:", BUS_LIST, key="admin_bus_filter")
            f_date = st.date_input("তারিখ ফিল্টার করুন:", value=today_dt, format="DD-MM-YYYY", key="admin_date_filter")
            
            if 'বাসের নাম' in df_show.columns and 'ভ্রমণের তারিখ' in df_show.columns:
                df_f = df_show[
                    (df_show['ভ্রমণের তারিখ'] == f_date.strftime("%d-%m-%Y")) &
                    (df_show['বাসের নাম'] == f_bus)
                ]
                st.write(f"📊 **{f_bus}** - {f_date.strftime('%d-%m-%Y')} এর মোট বুকিং: {len(df_f)} টি")
                for index, row in df_f.iterrows():
                    with st.expander(f"সিট {row['সিট নম্বর']} - {row['কাস্টমারের নাম']}"):
                        st.write(f"📱 ফোন: {row['মোবাইল নম্বর']} | 🏢 কাউন্টার: {row['কাউন্টার নাম']}")
                        st.write(f"⏰ বুকিং টাইম: {row['বুকিংয়ের সময়']}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c_down, c_link = st.columns(2)
            with c_down: 
                st.download_button("📁 Excel রিপোর্ট", df_show.to_csv(index=False).encode('utf-8-sig'), "bus_report.csv")
            with c_link: 
                         st.link_button("🌐 Google Sheet খুলুন", GOOGLE_SHEET_URL)
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

BUS_LIST = ["আবিদা ট্যুরিস্ট - বাস ১", "আবিদা ট্যুরিস্ট - বাস ২"]

# ২. সময় নিয়ন্ত্রণ (বাংলাদেশ টাইম জোন - BD Time)
local_tz = pytz.timezone('Asia/Dhaka')

def get_bd_time():
    """বাংলাদেশের বর্তমান সময় ও তারিখ পাওয়ার ফাংশন"""
    return datetime.now(local_tz)

today_dt = get_bd_time().date()

# ৩. ডাটা সেভ ও আপডেট করার ফাংশন
def save_booking_data(data_list):
    df = pd.DataFrame(data_list)
    if not os.path.isfile(RECORD_FILE):
        df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(RECORD_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')

def overwrite_all_data(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')

# ৪. পেজ সেটআপ ও অ্যাডভান্সড সিএসএস
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

# ৫. ৩৭টি সিটের তালিকা তৈরি (A-H পর্যন্ত ৪টি করে সিট, I সারিতে ৫টি সিট)
rows_normal = ["A", "B", "C", "D", "E", "F", "G", "H"]
seat_list = [f"{r}{num}" for r in rows_normal for num in range(1, 5)] + [f"I{num}" for num in range(1, 6)]

# সেশন স্টেট সেটআপ
if 'selected_seats' not in st.session_state:
    st.session_state.selected_seats = []
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

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

# বুকড সিট ফিল্টার
booked_seats_for_date = []
if os.path.isfile(RECORD_FILE):
    try:
        df_existing = pd.read_csv(RECORD_FILE, dtype=str, on_bad_lines='skip')
        if 'ভ্রমণের তারিখ' in df_existing.columns and 'বাসের নাম' in df_existing.columns:
            df_existing['ভ্রমণের তারিখ'] = df_existing['ভ্রমণের তারিখ'].str.strip()
            df_existing['বাসের নাম'] = df_existing['বাসের নাম'].str.strip()
            
            df_filtered = df_existing[
                (df_existing['ভ্রমণের তারিখ'] == formatted_journey_date) & 
                (df_existing['বাসের নাম'] == selected_bus)
            ]
            booked_seats_for_date = [s.strip() for s in df_filtered['সিট নম্বর'].dropna().tolist()]
    except Exception:
        booked_seats_for_date = []

st.session_state.selected_seats = [
    s for s in st.session_state.selected_seats if s not in booked_seats_for_date
]

tab1, tab2 = st.tabs(["💺 ৩৭-সিট ম্যাপ ভিউ", "📝 বুকিং ফরম"])

# --- 💺 ট্যাব ১: সিট ম্যাপ (মাঝখানে হাঁটার রাস্তা সহ) ---
with tab1:
    st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1e3c72;'>{selected_bus} ({formatted_journey_date})</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#777; font-size:11px; margin-bottom:10px;'>খালি সিট সবুজ 🟢, সিলেক্টেড নীল 🔵 এবং বুকড লাল 🔴</p>", unsafe_allow_html=True)
    
    def render_seat_clickable(seat_id):
        if seat_id in booked_seats_for_date:
            st.button(f"🔴 {seat_id}", key=f"booked_{seat_id}", disabled=True, use_container_width=True)
        elif seat_id in st.session_state.selected_seats:
            if st.button(f"🔵 {seat_id}", key=f"sel_{seat_id}", use_container_width=True):
                st.session_state.selected_seats.remove(seat_id)
                st.rerun()
        else:
            if st.button(f"🟢 {seat_id}", key=f"avail_{seat_id}", use_container_width=True):
                st.session_state.selected_seats.append(seat_id)
                st.rerun()

    # ড্রাইভার ও গেইট বিন্যাস (মাঝখানে ফাঁকা রাস্তা রেখে)
    c1, c2, c_gap, c3, c4 = st.columns([1, 1, 0.8, 1, 1], gap="small")
    with c1: st.button("🚪 GATE", key="GAT_m", disabled=True, use_container_width=True)
    with c2: st.write("")
    with c_gap: st.write("") # মাঝখানের হাঁটার রাস্তা
    with c3: st.write("")
    with c4: st.button("👨‍✈️ DRIVER", key="DR_m", disabled=True, use_container_width=True)
    
    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

    # A থেকে H সারি (বাম পাশে ২টি, মাঝখানে হাঁটার রাস্তা, ডান পাশে ২টি সিট)
    for r in rows_normal:
        c1, c2, c_gap, c3, c4 = st.columns([1, 1, 0.8, 1, 1], gap="small")
        with c1: render_seat_clickable(f"{r}1")
        with c2: render_seat_clickable(f"{r}2")
        with c_gap: st.markdown("<p style='text-align:center; color:#ccc; font-size:10px; margin:auto;'>|</p>", unsafe_allow_html=True) # হাঁটার রাস্তার জন্য খালি জায়গা বা দাগ
        with c3: render_seat_clickable(f"{r}3")
        with c4: render_seat_clickable(f"{r}4")

    st.markdown("<hr style='margin:5px 0; border-style:dashed;'>", unsafe_allow_html=True)
    
    # I সারি (পেছনের সারিতে ৫টি সিট একসাথে)
    i_cols = st.columns(5, gap="small")
    for idx, num in enumerate(range(1, 6)):
        with i_cols[idx]:
            render_seat_clickable(f"I{num}")

    if st.session_state.selected_seats:
        st.info(f"🎯 আপনার পছন্দকৃত সিট: **{', '.join(st.session_state.selected_seats)}**")

# --- 📝 ট্যাব ২: মূল বুকিং ফরম ---
with tab2:
    available_seats = [s for s in seat_list if s not in booked_seats_for_date]
    
    if not available_seats:
        st.error(f"🚨 দুঃখিত, {selected_bus}-এর এই তারিখের সব ৩৭টি সিটই বুকড হয়ে গেছে।")
    else:
        st.subheader("বুকিং বিবরণ")
        
        with st.form("interactive_booking_form", clear_on_submit=True):
            seats = st.multiselect(
                "📲 সিট নির্বাচন করুন (এক বা একাধিক সিট বাছতে পারবেন):", 
                options=available_seats, 
                default=st.session_state.selected_seats
            )
            name = st.text_input("👤 যাত্রীর নাম:").strip()
            phone = st.text_input("📞 যাত্রীর মোবাইল নম্বর:").strip()
            counter_name = st.text_input("🏢 কাউন্টার নাম:").strip()

            submit_btn = st.form_submit_button(f"{selected_bus}-এর টিকেট কনফার্ম করুন 🔘", use_container_width=True)

            if submit_btn:
                if not seats:
                    st.error("⚠️ অনুগ্রহ করে অন্তত একটি সিট নির্বাচন করুন!")
                elif name and phone and counter_name:
                    booking_time = get_bd_time().strftime("%d-%m-%Y %I:%M:%S %p")
                    
                    booking_records = []
                    for seat in seats:
                        booking_records.append({
                            "বুকিংয়ের সময় (BD Time)": booking_time,
                            "বাসের নাম": selected_bus,
                            "ভ্রমণের তারিখ": formatted_journey_date,
                            "কাস্টমারের নাম": str(name),
                            "সিট নম্বর": str(seat),
                            "মোবাইল নম্বর": str(phone),
                            "কাউন্টার নাম": str(counter_name)
                        })
                    
                    save_booking_data(booking_records)
                    confirmed_seats = ", ".join(seats)
                    
                    st.session_state.selected_seats = []
                    
                    st.balloons()
                    st.success(f"🎉 বুকিং সফল হয়েছে! ({selected_bus} - সিট: {confirmed_seats})")
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error("⚠️ অনুগ্রহ করে যাত্রীর নাম, মোবাইল নম্বর এবং কাউন্টার নাম সঠিকভাবে লিখুন।")

# ৬. অ্যাডমিন কন্ট্রোল ও রিপোর্ট জেনারেটর
st.markdown("<br><hr>", unsafe_allow_html=True)
with st.expander("🔐 অ্যাডমিন পোর্টাল (কন্ট্রোল ও এডিট)"):
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
            df_show = pd.read_csv(RECORD_FILE, dtype=str, on_bad_lines='skip')
            
            st.markdown("### 🔄 ট্রিপ কন্ট্রোল ও এডিট প্যানেল")
            
            f_bus = st.selectbox("ফিল্টার করার জন্য বাস বাছুন:", BUS_LIST, key="admin_bus_filter")
            f_date = st.date_input("তারিখ ফিল্টার করুন:", value=today_dt, format="DD-MM-YYYY", key="admin_date_filter")
            formatted_f_date = f_date.strftime("%d-%m-%Y")
            
            if 'বাসের নাম' in df_show.columns and 'ভ্রমণের তারিখ' in df_show.columns:
                df_show['ভ্রমণের তারিখ'] = df_show['ভ্রমণের তারিখ'].str.strip()
                df_show['বাসের নাম'] = df_show['বাসের নাম'].str.strip()
                
                df_f = df_show[
                    (df_show['ভ্রমণের তারিখ'] == formatted_f_date) &
                    (df_show['বাসের নাম'] == f_bus)
                ]
                st.write(f"📊 **{f_bus}** - {formatted_f_date} এর মোট বুকিং: {len(df_f)} টি")
                
                for idx, row in df_f.iterrows():
                    time_col = 'বুকিংয়ের সময় (BD Time)' if 'বুকিংয়ের সময় (BD Time)' in row else 'বুকিংয়ের সময়'
                    booking_time_str = row.get(time_col, '')
                    
                    with st.expander(f"💺 সিট: {row['সিট নম্বর']} | কাস্টমার: {row['কাস্টমারের নাম']}"):
                        st.caption(f"⏰ বুকিংয়ের সময় (BD Time): {booking_time_str}")
                        with st.form(key=f"edit_form_{idx}"):
                            new_name = st.text_input("নাম:", value=str(row['কাস্টমারের নাম']))
                            new_phone = st.text_input("ফোন:", value=str(row['মোবাইল নম্বর']))
                            new_counter = st.text_input("কাউন্টার:", value=str(row['কাউন্টার নাম']))
                            
                            c_save, c_del = st.columns(2)
                            with c_save:
                                update_btn = st.form_submit_button("✏️ আপডেট করুন")
                            with c_del:
                                delete_btn = st.form_submit_button("❌ ক্যানসেল/ডিলিট")

                            if update_btn:
                                df_show.at[idx, 'কাস্টমারের নাম'] = str(new_name).strip()
                                df_show.at[idx, 'মোবাইল নম্বর'] = str(new_phone).strip()
                                df_show.at[idx, 'কাউন্টার নাম'] = str(new_counter).strip()
                                overwrite_all_data(df_show)
                                st.success("তথ্য আপডেট হয়েছে!")
                                time.sleep(0.8)
                                st.rerun()
                                
                            if delete_btn:
                                df_show = df_show.drop(idx)
                                overwrite_all_data(df_show)
                                st.warning("বুকিংটি ক্যানসেল করা হয়েছে ও সিট খালি করা হয়েছে!")
                                time.sleep(0.8)
                                st.rerun()

            st.markdown("---")
            if st.button("⚠️ সকল ডাটা একসাথে মুছুন (Reset All)", type="primary", use_container_width=True):
                try:
                    os.remove(RECORD_FILE)
                    st.success("🔥 সকল বুকিং ডাটা মুছে ফেলা হয়েছে!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"ডাটা মুছতে সমস্যা হয়েছে: {e}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            column_order = [
                "বুকিংয়ের সময় (BD Time)", 
                "বাসের নাম", 
                "ভ্রমণের তারিখ", 
                "সিট নম্বর", 
                "কাস্টমারের নাম", 
                "মোবাইল নম্বর", 
                "কাউন্টার নাম"
            ]
            
            existing_cols = [col for col in column_order if col in df_show.columns]
            df_download = df_show[existing_cols]

            csv_data = df_download.to_csv(index=False, encoding='utf-8-sig')

            c_down, c_link = st.columns(2)
            with c_down: 
                st.download_button(
                    label="📊 এক্সেল (CSV) রিপোর্ট ডাউনলোড", 
                    data=csv_data, 
                    file_name=f"Abida_Tourist_Report_{formatted_journey_date}.csv", 
                    mime="text/csv",
                    use_container_width=True
                )
            with c_link: 
                st.link_button("🌐 Google Sheet খুলুন", GOOGLE_SHEET_URL, use_container_width=True)

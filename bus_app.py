import streamlit as st

# ৪২টি সিটের তালিকা
rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
seat_list = [f"{r}{c}" for r in rows for c in range(1, 5)][:42]

if 'booked' not in st.session_state:
    st.session_state.booked = {}

st.set_page_config(page_title="বাস টিকিট বুকিং", layout="wide")
st.title("🚌 মীরপুর টু নাজিরপুর - বাস টিকিট সিস্টেম")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("সিট নির্বাচন করুন (২+২)")
    for i in range(0, len(seat_list), 4):
        r_seats = seat_list[i:i+4]
        cols = st.columns([1, 1, 0.5, 1, 1])
        for idx, seat in enumerate(r_seats):
            d_idx = idx if idx < 2 else idx + 1
            if seat in st.session_state.booked:
                cols[d_idx].button(f"🔴 {seat}", key=seat, disabled=True)
            else:
                cols[d_idx].button(f"🟢 {seat}", key=seat)

with col2:
    st.subheader("বুকিং ফরম")
    s_seat = st.selectbox("সিট বেছে নিন", [s for s in seat_list if s not in st.session_state.booked])
    name = st.text_input("যাত্রীর নাম")
    phone = st.text_input("মোবাইল নম্বর")
    if st.button("টিকিট কনফার্ম করুন"):
        if name and phone:
            st.session_state.booked[s_seat] = {"name": name, "phone": phone}
            st.success(f"{s_seat} নম্বর টিকিটটি {name}-এর জন্য বুক হয়েছে!")
        else:
            st.error("নাম ও মোবাইল নম্বর দিন")
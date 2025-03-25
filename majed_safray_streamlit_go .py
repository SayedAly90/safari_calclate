import streamlit as st
import pandas as pd
from datetime import datetime

# ثوابت للحسابات
ENTRY_FEE_REGULAR = 100  # رسوم الدخول العادية
ENTRY_FEE_PEAK = 200     # رسوم الدخول في الموسم
SINGLE_ROOM_COST = 300   # تكلفة الغرفة الفردية
DOUBLE_ROOM_COST = 180   # تكلفة الغرفة المزدوجة
ORGANIZER_ROOM_COST = 150  # تكلفة غرفة المنظم
SAFARI_COST = 400        # تكلفة الرحلة الداخلية
CAR_RENTAL_COST = 170    # تكلفة إيجار السيارة يومياً
AIRPORT_TRANSFER_COST = 200  # تكلفة النقل من وإلى المطار
WATER_COST = 50          # تكلفة المياه
GIFT_COST = 10           # تكلفة الهدايا
MAX_PEOPLE_PER_CAR = 3   # الحد الأقصى للمشاركين في سيارة واحدة

# التأكد من وجود قائمة المشاركين في session_state
if "participants" not in st.session_state:
    st.session_state.participants = []

# واجهة المستخدم
st.title("حاسبة تكاليف رحلات السفاري")

# إدخال بيانات المشارك
st.header("إضافة مشارك جديد")
name = st.text_input("اسم المشارك:")
nights = st.number_input("عدد الليالي:", min_value=1, max_value=14, step=1)
car_days = st.number_input("أيام استئجار السيارة:", min_value=1, max_value=14, step=1)
room_type = st.selectbox("نوع الغرفة:", ["فردية", "زوجية"])
car_choice = st.selectbox("نوع السيارة:", ["خاصة", "مشاركة"])
car_sharing = st.number_input("عدد المشاركين في السيارة:", min_value=1, max_value=MAX_PEOPLE_PER_CAR, step=1)
is_organizer = st.checkbox("منظم")
is_peak_season = st.checkbox("موسم الذروة")

if st.button("إضافة مشارك"):
    if not name:
        st.error("الرجاء إدخال اسم المشارك")
    else:
        participant = {
            "name": name,
            "nights": nights,
            "car_days": car_days,
            "room_type": room_type,
            "car_choice": car_choice,
            "car_sharing": car_sharing,
            "is_organizer": is_organizer
        }
        st.session_state.participants.append(participant)
        st.success(f"تمت إضافة المشارك: {name}")

# عرض قائمة المشاركين
if st.session_state.participants:
    st.header("قائمة المشاركين")
    df = pd.DataFrame(st.session_state.participants)
    st.dataframe(df)

    # حساب التكاليف
    st.subheader("حساب التكاليف")
    if st.button("حساب التكاليف"):
        results = []
        total_cost = 0
        total_regular_participants = len([p for p in st.session_state.participants if not p["is_organizer"]])

        for participant in st.session_state.participants:
            entry_fee = ENTRY_FEE_PEAK if is_peak_season else ENTRY_FEE_REGULAR
            if participant["is_organizer"]:
                room_cost = ORGANIZER_ROOM_COST * participant["nights"]
                safari_cost = SAFARI_COST
                entry_fee_cost = 0
                car_rental_cost = 0
                airport_transfer_cost = 0
                water_cost = 0
                gift_cost = 0
            else:
                room_cost = SINGLE_ROOM_COST * participant["nights"] if participant["room_type"] == "فردية" else DOUBLE_ROOM_COST * participant["nights"]
                entry_fee_cost = entry_fee * participant["nights"]
                safari_cost = SAFARI_COST
                car_rental_cost = (CAR_RENTAL_COST * participant["car_days"]) / participant["car_sharing"] if participant["car_choice"] == "مشاركة" else CAR_RENTAL_COST * participant["car_days"]
                airport_transfer_cost = AIRPORT_TRANSFER_COST / total_regular_participants if total_regular_participants > 0 else 0
                water_cost = WATER_COST
                gift_cost = GIFT_COST

            total_participant_cost = room_cost + entry_fee_cost + safari_cost + car_rental_cost + airport_transfer_cost + water_cost + gift_cost
            results.append({
                "name": participant["name"],
                "nights": participant["nights"],
                "car_days": participant["car_days"],
                "room_type": participant["room_type"],
                "car_choice": participant["car_choice"],
                "car_sharing": participant["car_sharing"],
                "is_organizer": participant["is_organizer"],
                "total_cost": total_participant_cost
            })
            total_cost += total_participant_cost

        # عرض التفاصيل
        st.header("تفاصيل التكاليف")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)
        st.write(f"إجمالي تكلفة الرحلة: {total_cost:.2f}")

        # تصدير البيانات إلى CSV
        st.subheader("تصدير البيانات")
        if st.button("تصدير البيانات إلى CSV"):
            # إضافة صف المجموع
            total_row = {
                "name": "المجموع",
                "nights": "",
                "car_days": "",
                "room_type": "",
                "car_choice": "",
                "car_sharing": "",
                "is_organizer": "",
                "total_cost": total_cost
            }
            results_df = pd.concat([results_df, pd.DataFrame([total_row])], ignore_index=True)

            # إنشاء ملف CSV
            csv_filename = f"safari_trip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_data = results_df.to_csv(index=False, encoding="utf-8-sig")

            # توفير رابط لتحميل الملف
            st.download_button(
                label="تحميل ملف CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv"
            )

# إعادة تحميل الصفحة
if st.button("إعادة تحميل الصفحة"):
    st.session_state.participants = []
    st.success("تمت إعادة تحميل الصفحة ومسح جميع البيانات.")

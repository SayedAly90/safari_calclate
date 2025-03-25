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

    # إضافة أزرار التعديل والحذف بجانب كل مشارك
    for i, participant in enumerate(st.session_state.participants):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(f"{i + 1}. {participant['name']}")
        with col2:
            if st.button(f"تعديل", key=f"edit_{i}"):
                # تعديل بيانات المشارك
                edited_name = st.text_input("اسم المشارك (تعديل):", value=participant["name"], key=f"edit_name_{i}")
                edited_nights = st.number_input("عدد الليالي (تعديل):", min_value=1, max_value=14, step=1, value=participant["nights"], key=f"edit_nights_{i}")
                edited_car_days = st.number_input("أيام استئجار السيارة (تعديل):", min_value=1, max_value=14, step=1, value=participant["car_days"], key=f"edit_car_days_{i}")
                edited_room_type = st.selectbox("نوع الغرفة (تعديل):", ["فردية", "زوجية"], index=["فردية", "زوجية"].index(participant["room_type"]), key=f"edit_room_type_{i}")
                edited_car_choice = st.selectbox("نوع السيارة (تعديل):", ["خاصة", "مشاركة"], index=["خاصة", "مشاركة"].index(participant["car_choice"]), key=f"edit_car_choice_{i}")
                edited_car_sharing = st.number_input("عدد المشاركين في السيارة (تعديل):", min_value=1, max_value=MAX_PEOPLE_PER_CAR, step=1, value=participant["car_sharing"], key=f"edit_car_sharing_{i}")
                edited_is_organizer = st.checkbox("منظم (تعديل):", value=participant["is_organizer"], key=f"edit_is_organizer_{i}")

                if st.button("حفظ التعديلات", key=f"save_{i}"):
                    st.session_state.participants[i] = {
                        "name": edited_name,
                        "nights": edited_nights,
                        "car_days": edited_car_days,
                        "room_type": edited_room_type,
                        "car_choice": edited_car_choice,
                        "car_sharing": edited_car_sharing,
                        "is_organizer": edited_is_organizer
                    }
                    st.success(f"تم تعديل بيانات المشارك: {edited_name}")
                    st.experimental_rerun()
        with col3:
            if st.button(f"حذف", key=f"delete_{i}"):
                st.session_state.participants.pop(i)
                st.success(f"تم حذف المشارك: {participant['name']}")
                st.experimental_rerun()

    # تصدير البيانات إلى CSV
    st.subheader("تصدير البيانات")
    if st.button("تصدير البيانات إلى CSV"):
        if not st.session_state.participants:
            st.warning("لا توجد بيانات للتصدير")
        else:
            # تحويل قائمة المشاركين إلى DataFrame
            df = pd.DataFrame(st.session_state.participants)

            # حساب المجموع
            total_cost = sum([
                (SINGLE_ROOM_COST if p["room_type"] == "فردية" else DOUBLE_ROOM_COST) * p["nights"] +
                (CAR_RENTAL_COST * p["car_days"] / p["car_sharing"] if p["car_choice"] == "مشاركة" else CAR_RENTAL_COST * p["car_days"]) +
                (ENTRY_FEE_PEAK if is_peak_season else ENTRY_FEE_REGULAR) * p["nights"] +
                SAFARI_COST + WATER_COST + GIFT_COST
                for p in st.session_state.participants
            ])

            # إضافة المجموع إلى DataFrame
            df.loc[len(df)] = ["المجموع", "", "", "", "", "", "", total_cost]

            # إنشاء ملف CSV
            csv_filename = f"safari_trip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_data = df.to_csv(index=False, encoding="utf-8-sig")

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
    st.experimental_rerun()

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

    # تعديل بيانات مشارك
    st.subheader("تعديل بيانات مشارك")
    participant_to_edit = st.selectbox("اختر المشارك لتعديله:", options=[p["name"] for p in st.session_state.participants])
    if participant_to_edit:
        index_to_edit = next(i for i, p in enumerate(st.session_state.participants) if p["name"] == participant_to_edit)
        edited_name = st.text_input("اسم المشارك (تعديل):", value=st.session_state.participants[index_to_edit]["name"])
        edited_nights = st.number_input("عدد الليالي (تعديل):", min_value=1, max_value=14, step=1, value=st.session_state.participants[index_to_edit]["nights"])
        edited_car_days = st.number_input("أيام استئجار السيارة (تعديل):", min_value=1, max_value=14, step=1, value=st.session_state.participants[index_to_edit]["car_days"])
        edited_room_type = st.selectbox("نوع الغرفة (تعديل):", ["فردية", "زوجية"], index=["فردية", "زوجية"].index(st.session_state.participants[index_to_edit]["room_type"]))
        edited_car_choice = st.selectbox("نوع السيارة (تعديل):", ["خاصة", "مشاركة"], index=["خاصة", "مشاركة"].index(st.session_state.participants[index_to_edit]["car_choice"]))
        edited_car_sharing = st.number_input("عدد المشاركين في السيارة (تعديل):", min_value=1, max_value=MAX_PEOPLE_PER_CAR, step=1, value=st.session_state.participants[index_to_edit]["car_sharing"])
        edited_is_organizer = st.checkbox("منظم (تعديل):", value=st.session_state.participants[index_to_edit]["is_organizer"])

        if st.button("حفظ التعديلات"):
            st.session_state.participants[index_to_edit] = {
                "name": edited_name,
                "nights": edited_nights,
                "car_days": edited_car_days,
                "room_type": edited_room_type,
                "car_choice": edited_car_choice,
                "car_sharing": edited_car_sharing,
                "is_organizer": edited_is_organizer
            }
            st.success(f"تم تعديل بيانات المشارك: {edited_name}")

    # حذف مشارك
    st.subheader("حذف مشارك")
    participant_to_delete = st.selectbox("اختر المشارك لحذفه:", options=[p["name"] for p in st.session_state.participants])
    if st.button("حذف المشارك"):
        st.session_state.participants = [p for p in st.session_state.participants if p["name"] != participant_to_delete]
        st.success(f"تم حذف المشارك: {participant_to_delete}")

    # تصدير البيانات إلى CSV
    st.subheader("تصدير البيانات")
    if st.button("تصدير البيانات إلى CSV"):
        if not st.session_state.participants:
            st.warning("لا توجد بيانات للتصدير")
        else:
            # تحويل قائمة المشاركين إلى DataFrame
            df = pd.DataFrame(st.session_state.participants)
            
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

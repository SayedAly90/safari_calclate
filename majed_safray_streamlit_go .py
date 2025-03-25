import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# إعداد Google Sheets API
def connect_to_google_sheets(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("majed-safary-b5a0b9e18028.json", scope)  # استبدل بـ اسم ملف JSON الخاص بك
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1  # اختر الورقة الأولى
    return sheet

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
if st.button("حساب التكاليف"):
    if not st.session_state.participants:
        st.warning("الرجاء إضافة مشاركين أولاً")
    else:
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
                water_cost = WATER_COST / participant["nights"] if participant["nights"] > 0 else 0
                gift_cost = GIFT_COST

            total_participant_cost = room_cost + entry_fee_cost + safari_cost + car_rental_cost + airport_transfer_cost + water_cost + gift_cost
            results.append({
                "name": participant["name"],
                "total_cost": total_participant_cost
            })
            total_cost += total_participant_cost

        st.header("نتائج التكاليف")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)
        st.write(f"إجمالي تكلفة الرحلة: {total_cost:.2f}")

# تصدير البيانات إلى Google Sheets
if st.button("حفظ البيانات في Google Sheets"):
    if not st.session_state.participants:
        st.warning("لا توجد بيانات للحفظ")
    else:
        try:
            sheet = connect_to_google_sheets("Safari Trip Data")  # استبدل باسم Google Sheet الخاص بك
            for participant in st.session_state.participants:
                sheet.append_row([
                    participant["name"],
                    participant["nights"],
                    participant["car_days"],
                    participant["room_type"],
                    participant["car_choice"],
                    participant["car_sharing"],
                    participant["is_organizer"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
            st.success("تم حفظ البيانات في Google Sheets بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء الحفظ: {str(e)}")

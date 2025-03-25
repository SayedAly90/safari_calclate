import streamlit as st
import pandas as pd
from datetime import datetime

# التأكد من وجود المتغيرات في session_state
if "trip_info" not in st.session_state:
    st.session_state.trip_info = {
        "trip_name": "",
        "country": "",
        "entry_fee_regular": 100,
        "entry_fee_peak": 200,
        "single_room_cost": 300,
        "double_room_cost": 180,
        "organizer_room_cost": 150,
        "safari_cost": 400,
        "car_rental_cost": 170,
        "airport_transfer_cost": 200,
        "water_cost": 50,
        "gift_cost": 10,
        "max_people_per_car": 3
    }

if "participants" not in st.session_state:
    st.session_state.participants = []

# الصفحة الأولى: إدخال معلومات الرحلة
if "step" not in st.session_state:
    st.session_state.step = "trip_info"

if st.session_state.step == "trip_info":
    st.title("إعداد معلومات الرحلة")

    # إدخال معلومات الرحلة
    st.session_state.trip_info["trip_name"] = st.text_input("اسم الرحلة:", value=st.session_state.trip_info["trip_name"])
    st.session_state.trip_info["country"] = st.text_input("الدولة:", value=st.session_state.trip_info["country"])
    st.session_state.trip_info["entry_fee_regular"] = st.number_input("رسوم الدخول العادية:", min_value=0, value=st.session_state.trip_info["entry_fee_regular"])
    st.session_state.trip_info["entry_fee_peak"] = st.number_input("رسوم الدخول في موسم الذروة:", min_value=0, value=st.session_state.trip_info["entry_fee_peak"])
    st.session_state.trip_info["single_room_cost"] = st.number_input("تكلفة الغرفة الفردية:", min_value=0, value=st.session_state.trip_info["single_room_cost"])
    st.session_state.trip_info["double_room_cost"] = st.number_input("تكلفة الغرفة المزدوجة:", min_value=0, value=st.session_state.trip_info["double_room_cost"])
    st.session_state.trip_info["organizer_room_cost"] = st.number_input("تكلفة غرفة المنظم:", min_value=0, value=st.session_state.trip_info["organizer_room_cost"])
    st.session_state.trip_info["safari_cost"] = st.number_input("تكلفة الرحلة الداخلية:", min_value=0, value=st.session_state.trip_info["safari_cost"])
    st.session_state.trip_info["car_rental_cost"] = st.number_input("تكلفة إيجار السيارة يومياً:", min_value=0, value=st.session_state.trip_info["car_rental_cost"])
    st.session_state.trip_info["airport_transfer_cost"] = st.number_input("تكلفة النقل من وإلى المطار:", min_value=0, value=st.session_state.trip_info["airport_transfer_cost"])
    st.session_state.trip_info["water_cost"] = st.number_input("تكلفة المياه:", min_value=0, value=st.session_state.trip_info["water_cost"])
    st.session_state.trip_info["gift_cost"] = st.number_input("تكلفة الهدايا:", min_value=0, value=st.session_state.trip_info["gift_cost"])
    st.session_state.trip_info["max_people_per_car"] = st.number_input("الحد الأقصى للمشاركين في سيارة واحدة:", min_value=1, value=st.session_state.trip_info["max_people_per_car"])

    # زر للانتقال إلى إدخال المشاركين
    if st.button("الانتقال إلى إدخال المشاركين"):
        st.session_state.step = "participants"
        st.experimental_rerun()

# الصفحة الثانية: إدخال المشاركين وحساب التكاليف
if st.session_state.step == "participants":
    st.title(f"رحلة: {st.session_state.trip_info['trip_name']} - {st.session_state.trip_info['country']}")

    # إدخال بيانات المشارك
    st.header("إضافة مشارك جديد")
    name = st.text_input("اسم المشارك:")
    nights = st.number_input("عدد الليالي:", min_value=1, max_value=14, step=1)
    car_days = st.number_input("أيام استئجار السيارة:", min_value=1, max_value=14, step=1)
    room_type = st.selectbox("نوع الغرفة:", ["فردية", "زوجية"])
    car_choice = st.selectbox("نوع السيارة:", ["خاصة", "مشاركة"])
    car_sharing = st.number_input("عدد المشاركين في السيارة:", min_value=1, max_value=st.session_state.trip_info["max_people_per_car"], step=1)
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
                entry_fee = st.session_state.trip_info["entry_fee_peak"] if is_peak_season else st.session_state.trip_info["entry_fee_regular"]
                if participant["is_organizer"]:
                    room_cost = st.session_state.trip_info["organizer_room_cost"] * participant["nights"]
                    safari_cost = st.session_state.trip_info["safari_cost"]
                    entry_fee_cost = 0
                    car_rental_cost = 0
                    airport_transfer_cost = 0
                    water_cost = 0
                    gift_cost = 0
                else:
                    room_cost = st.session_state.trip_info["single_room_cost"] * participant["nights"] if participant["room_type"] == "فردية" else st.session_state.trip_info["double_room_cost"] * participant["nights"]
                    entry_fee_cost = entry_fee * participant["nights"]
                    safari_cost = st.session_state.trip_info["safari_cost"]
                    car_rental_cost = (st.session_state.trip_info["car_rental_cost"] * participant["car_days"]) / participant["car_sharing"] if participant["car_choice"] == "مشاركة" else st.session_state.trip_info["car_rental_cost"] * participant["car_days"]
                    airport_transfer_cost = st.session_state.trip_info["airport_transfer_cost"] / total_regular_participants if total_regular_participants > 0 else 0
                    water_cost = st.session_state.trip_info["water_cost"]
                    gift_cost = st.session_state.trip_info["gift_cost"]

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

    # زر للعودة إلى صفحة معلومات الرحلة
    if st.button("العودة إلى صفحة معلومات الرحلة"):
        st.session_state.step = "trip_info"
        st.experimental_rerun()

import streamlit as st
import pandas as pd
import base64
from io import BytesIO

st.set_page_config(page_title="حاسبة تكاليف الرحلة", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better RTL support
st.markdown("""
<style>
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .reportview-container .main .block-container {
        direction: rtl;
    }
    h1, h2, h3, p, div {
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        float: right;
    }
    .stDownloadButton>button {
        float: right;
    }
</style>
""", unsafe_allow_html=True)

# Function to create Excel download link
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='تفاصيل التكاليف', index=False)
        # Auto-adjust columns' width
        worksheet = writer.sheets['تفاصيل التكاليف']
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col) + 2)
            worksheet.set_column(i, i, column_width)
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename="تفاصيل_التكاليف.xlsx"):
    """Generates a link to download the Excel file"""
    val = to_excel(df)
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">تحميل كملف إكسل</a>'

# Initialize session state
if 'participants' not in st.session_state:
    st.session_state.participants = []

if 'organizer_included' not in st.session_state:
    st.session_state.organizer_included = False

if 'season_fee' not in st.session_state:
    st.session_state.season_fee = 100

# Define constants
INTERNAL_FLIGHT_COST = 400  # تكلفة الرحلة الداخلية
GIFT_COST = 10  # تكلفة الهدايا
SINGLE_ROOM_COST = 300  # تكلفة الغرفة الفردية لليلة
DOUBLE_ROOM_COST = 180  # تكلفة الغرفة المزدوجة للشخص لليلة
ORGANIZER_HOTEL_COST = 150  # تكلفة الفندق للمنظم لليلة
CAR_COST_PER_DAY = 170  # تكلفة السيارة لليوم
AIRPORT_TRANSFER_COST = 200  # تكلفة النقل من وإلى المطار
WATER_COST = 50  # تكلفة المياه

# Title
st.markdown("<h1 class='rtl'>حاسبة تكاليف الرحلة</h1>", unsafe_allow_html=True)

# Create sidebar for settings
with st.sidebar:
    st.markdown("<h2 class='rtl'>إعدادات الرحلة</h2>", unsafe_allow_html=True)
    
    # Season cost
    season_options = {"موسم منخفض (100)": 100, "موسم مرتفع (200)": 200}
    selected_season = st.radio("رسوم الدخول حسب الموسم", options=list(season_options.keys()), index=0)
    st.session_state.season_fee = season_options[selected_season]
    
    # Organizer settings
    st.markdown("<h3 class='rtl'>إعدادات المنظم</h3>", unsafe_allow_html=True)
    add_organizer = st.checkbox("إضافة منظم للرحلة", value=st.session_state.organizer_included)
    
    if add_organizer:
        if not st.session_state.organizer_included:
            st.session_state.organizer_included = True
            organizer_nights = st.session_state.get('organizer_nights', 1)
            # Add organizer to participants if not already added
            if not any(p.get('name') == 'المنظم' for p in st.session_state.participants):
                st.session_state.participants.append({
                    'name': 'المنظم',
                    'nights': organizer_nights,
                    'car_days': 0,
                    'room_type': 'فردية',
                    'car_sharing': 'بدون سيارة',
                    'car_sharing_count': 0,
                    'is_organizer': True
                })
        
        # Update organizer nights if already exists
        organizer = next((p for p in st.session_state.participants if p.get('is_organizer', False)), None)
        if organizer:
            organizer_nights = st.number_input("عدد ليالي المنظم", min_value=1, value=organizer.get('nights', 1), key='organizer_nights')
            # Update the organizer's nights in participants list
            for p in st.session_state.participants:
                if p.get('is_organizer', False):
                    p['nights'] = organizer_nights
    else:
        st.session_state.organizer_included = False
        # Remove organizer from participants if exists
        st.session_state.participants = [p for p in st.session_state.participants if not p.get('is_organizer', False)]

# Main form for adding participants
st.markdown("<h2 class='rtl'>إضافة مشارك جديد</h2>", unsafe_allow_html=True)

with st.form(key='participant_form'):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("اسم المشارك", key="name")
        nights = st.selectbox("عدد الليالي في الفندق", options=list(range(1, 11)), index=0, key="nights")
        room_type = st.radio("نوع الغرفة", options=["فردية", "زوجية"], key="room_type")
    
    with col2:
        car_days = st.selectbox("عدد أيام استئجار السيارة", options=list(range(0, 11)), index=0, key="car_days")
        car_sharing = st.radio("خيار السيارة", options=["سيارة خاصة", "مشاركة السيارة", "بدون سيارة"], index=1, key="car_sharing")
        
        # Show car sharing count only if car sharing is selected
        car_sharing_count = 1
        if car_sharing == "مشاركة السيارة":
            car_sharing_count = st.selectbox("عدد المشاركين في السيارة (بحد أقصى 3)", options=list(range(2, 4)), index=0, key="car_sharing_count")
    
    submit_button = st.form_submit_button(label="إضافة المشارك")
    
    if submit_button and name:
        # Add new participant
        st.session_state.participants.append({
            'name': name,
            'nights': nights,
            'car_days': car_days,
            'room_type': room_type,
            'car_sharing': car_sharing,
            'car_sharing_count': car_sharing_count if car_sharing == "مشاركة السيارة" else 0,
            'is_organizer': False
        })
        st.success(f"تمت إضافة المشارك {name} بنجاح!")
        # Clear form
        st.experimental_rerun()

# Display and edit participants
if st.session_state.participants:
    st.markdown("<h2 class='rtl'>المشاركون</h2>", unsafe_allow_html=True)
    
    for i, participant in enumerate(st.session_state.participants):
        if participant.get('is_organizer', False) and not st.session_state.organizer_included:
            continue
            
        st.markdown(f"<h3 class='rtl'>المشارك {i+1}: {participant['name']}</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not participant.get('is_organizer', False):
                participant['nights'] = st.number_input(
                    "عدد الليالي", 
                    min_value=1, 
                    value=participant['nights'], 
                    key=f"nights_{i}"
                )
                participant['room_type'] = st.radio(
                    "نوع الغرفة", 
                    options=["فردية", "زوجية"], 
                    index=0 if participant['room_type'] == "فردية" else 1, 
                    key=f"room_type_{i}"
                )
        
        with col2:
            if not participant.get('is_organizer', False):
                participant['car_days'] = st.number_input(
                    "عدد أيام السيارة", 
                    min_value=0, 
                    value=participant['car_days'], 
                    key=f"car_days_{i}"
                )
                car_options = ["سيارة خاصة", "مشاركة السيارة", "بدون سيارة"]
                default_index = car_options.index(participant['car_sharing']) if participant['car_sharing'] in car_options else 1
                participant['car_sharing'] = st.radio(
                    "خيار السيارة", 
                    options=car_options, 
                    index=default_index, 
                    key=f"car_sharing_{i}"
                )
        
        with col3:
            if not participant.get('is_organizer', False) and participant['car_sharing'] == "مشاركة السيارة":
                participant['car_sharing_count'] = st.number_input(
                    "عدد المشاركين في السيارة", 
                    min_value=2, 
                    max_value=3, 
                    value=participant.get('car_sharing_count', 2), 
                    key=f"car_sharing_count_{i}"
                )
            
            if not participant.get('is_organizer', False):
                if st.button(f"حذف المشارك {participant['name']}", key=f"delete_{i}"):
                    st.session_state.participants.pop(i)
                    st.experimental_rerun()

    # Calculate costs
    if st.button("حساب التكاليف"):
        # Count number of regular participants (excluding organizer)
        regular_participants = [p for p in st.session_state.participants if not p.get('is_organizer', False)]
        num_participants = len(regular_participants)
        
        # Prepare results dataframe
        results = []
        
        # Calculate costs for each participant
        for participant in st.session_state.participants:
            is_organizer = participant.get('is_organizer', False)
            
            # Basic fixed costs
            internal_flight = INTERNAL_FLIGHT_COST
            gifts = 0 if is_organizer else GIFT_COST
            
            # Hotel costs
            if is_organizer:
                hotel_cost = participant['nights'] * ORGANIZER_HOTEL_COST
            elif participant['room_type'] == "فردية":
                hotel_cost = participant['nights'] * SINGLE_ROOM_COST
            else:  # زوجية
                hotel_cost = participant['nights'] * DOUBLE_ROOM_COST
            
            # Season entry fee
            season_entry_fee = 0 if is_organizer else participant['nights'] * st.session_state.season_fee
            
            # Car costs
            car_cost = 0
            if not is_organizer and participant['car_sharing'] != "بدون سيارة":
                if participant['car_sharing'] == "سيارة خاصة":
                    car_cost = participant['car_days'] * CAR_COST_PER_DAY
                else:  # مشاركة السيارة
                    car_cost = (participant['car_days'] * CAR_COST_PER_DAY) / participant['car_sharing_count']
            
            # Airport transfer and water costs
            airport_transfer = 0 if is_organizer else AIRPORT_TRANSFER_COST / num_participants
            water_cost = 0 if is_organizer else WATER_COST / (participant['nights'] * num_participants)
            
            # Total cost
            total_cost = internal_flight + gifts + hotel_cost + season_entry_fee + car_cost + airport_transfer + water_cost
            
            # Add to results
            results.append({
                'الاسم': participant['name'],
                'عدد الليالي': participant['nights'],
                'نوع الغرفة': participant['room_type'],
                'أيام السيارة': participant['car_days'],
                'خيار السيارة': participant['car_sharing'],
                'تكلفة الرحلة الداخلية': internal_flight,
                'تكلفة الهدايا': gifts,
                'تكلفة الفندق': hotel_cost,
                'رسوم الدخول': season_entry_fee,
                'تكلفة السيارة': car_cost,
                'النقل من وإلى المطار': airport_transfer,
                'تكلفة المياه': water_cost,
                'التكلفة الإجمالية': total_cost
            })
        
        # Create dataframe and display
        df_results = pd.DataFrame(results)
        
        st.markdown("<h2 class='rtl'>تفاصيل التكاليف</h2>", unsafe_allow_html=True)
        st.dataframe(df_results)
        
        # Total trip cost
        total_trip_cost = df_results['التكلفة الإجمالية'].sum()
        st.markdown(f"<h3 class='rtl'>التكلفة الإجمالية للرحلة: {total_trip_cost:.2f}</h3>", unsafe_allow_html=True)
        
        # Download link
        st.markdown(get_table_download_link(df_results), unsafe_allow_html=True)

# Instructions for deployment
st.markdown("""
<div class='rtl'>
<h2>تعليمات النشر على Streamlit</h2>
<ol>
    <li>قم بحفظ هذا الكود في ملف app.py</li>
    <li>قم بإنشاء ملف requirements.txt يحتوي على المكتبات المطلوبة:
        <pre>
streamlit
pandas
xlsxwriter
        </pre>
    </li>
    <li>ارفع الملفات إلى GitHub</li>
    <li>انتقل إلى موقع <a href="https://streamlit.io/" target="_blank">Streamlit</a> وقم بإنشاء حساب</li>
    <li>قم بإنشاء تطبيق جديد واختر المستودع الذي رفعت إليه الملفات</li>
    <li>استمتع بتطبيقك!</li>
</ol>
</div>
""", unsafe_allow_html=True)
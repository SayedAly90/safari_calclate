import streamlit as st
import pandas as pd
import json
import csv
from datetime import datetime
import base64
import io

class SafariCostCalculator:
    def __init__(self):
        # Constants for calculations
        self.ENTRY_FEE_REGULAR = 100  # Regular entry fee
        self.ENTRY_FEE_PEAK = 200     # Peak season entry fee
        self.SINGLE_ROOM_COST = 300   # Single room cost
        self.DOUBLE_ROOM_COST = 180   # Double room cost
        self.ORGANIZER_ROOM_COST = 150  # Organizer room cost
        self.SAFARI_COST = 400        # Internal safari trip cost
        self.CAR_RENTAL_COST = 170    # Daily car rental cost
        self.AIRPORT_TRANSFER_COST = 200  # Airport transfer cost
        self.WATER_COST = 50          # Water cost
        self.GIFT_COST = 10           # Gift cost
        self.MAX_PEOPLE_PER_CAR = 3   # Maximum people per car

    def calculate_costs(self, participants, is_peak_season):
        if not participants:
            st.warning("الرجاء إضافة مشاركين أولاً")
            return None, None

        # Count regular participants (excluding organizers)
        regular_participants = [p for p in participants if not p["is_organizer"]]
        total_regular_participants = len(regular_participants)
        
        # Count all participants
        total_participants = len(participants)
        
        # Calculate costs for each participant
        results = []
        total_cost = 0
        
        for participant in participants:
            cost_details = {}
            
            # Entry fee based on season
            entry_fee = self.ENTRY_FEE_PEAK if is_peak_season else self.ENTRY_FEE_REGULAR
            
            if participant["is_organizer"]:
                # Organizer only pays for hotel and safari
                room_cost = self.ORGANIZER_ROOM_COST * participant["nights"]
                safari_cost = self.SAFARI_COST
                
                # Other costs are zero for organizer
                entry_fee_cost = 0
                car_rental_cost = 0
                airport_transfer_cost = 0
                water_cost = 0
                gift_cost = 0
            else:
                # Room cost based on room type
                if participant["room_type"] == "فردية":
                    room_cost = self.SINGLE_ROOM_COST * participant["nights"]
                else:  # Double room
                    room_cost = self.DOUBLE_ROOM_COST * participant["nights"]
                
                # Entry fee costs
                entry_fee_cost = entry_fee * participant["nights"]
                
                # Safari cost
                safari_cost = self.SAFARI_COST
                
                # Car rental cost
                if participant["car_choice"] == "خاصة":
                    car_rental_cost = self.CAR_RENTAL_COST * participant["car_days"]
                else:  # Shared car
                    # Use number of participants sharing the car
                    if participant["car_sharing"] > 0:
                        car_rental_cost = (self.CAR_RENTAL_COST * participant["car_days"]) / participant["car_sharing"]
                    else:
                        car_rental_cost = 0
                
                # Airport transfer cost - divided among regular participants
                airport_transfer_cost = self.AIRPORT_TRANSFER_COST / total_regular_participants if total_regular_participants > 0 else 0
                
                # Water cost (divided by number of nights)
                water_cost = self.WATER_COST / participant["nights"] if participant["nights"] > 0 else 0
                
                # Gift cost
                gift_cost = self.GIFT_COST
            
            # Total cost for participant
            total_participant_cost = (
                room_cost + entry_fee_cost + safari_cost + car_rental_cost + 
                airport_transfer_cost + water_cost + gift_cost
            )
            
            # Compile cost details
            cost_details = {
                "name": participant["name"],
                "is_organizer": participant["is_organizer"],
                "room_cost": room_cost,
                "entry_fee_cost": entry_fee_cost,
                "safari_cost": safari_cost,
                "car_rental_cost": car_rental_cost,
                "airport_transfer_cost": airport_transfer_cost,
                "water_cost": water_cost,
                "gift_cost": gift_cost,
                "total_cost": total_participant_cost
            }
            
            results.append(cost_details)
            total_cost += total_participant_cost
        
        return results, total_cost

def get_download_link(df, filename, text):
    """Generate a link to download the dataframe as a CSV file"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def main():
    st.set_page_config(page_title="حاسبة تكاليف رحلات السفاري", layout="wide", direction="rtl")
    
    # Custom CSS for RTL layout
    st.markdown("""
        <style>
        body {
            direction: rtl;
            text-align: right;
        }
        .css-18e3th9 {
            padding-right: 3rem;
            padding-left: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("حاسبة تكاليف رحلات السفاري")
    
    # Initialize calculator
    calculator = SafariCostCalculator()
    
    # Initialize session state for participants list if it doesn't exist
    if 'participants' not in st.session_state:
        st.session_state.participants = []
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["إضافة مشاركين", "عرض التكاليف", "حفظ واستيراد البيانات"])
    
    with tab1:
        st.header("إضافة مشارك")
        
        # Form for adding a participant
        with st.form("participant_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("اسم المشارك")
                nights = st.number_input("عدد الليالي", min_value=1, max_value=14, value=1)
                car_days = st.number_input("أيام استئجار السيارة", min_value=1, max_value=14, value=1)
                is_organizer = st.checkbox("منظم")
            
            with col2:
                room_type = st.radio("نوع الغرفة", ["زوجية", "فردية"])
                car_choice = st.radio("سيارة", ["مشاركة", "خاصة"])
                car_sharing = st.number_input("عدد المشاركين في السيارة", min_value=1, max_value=calculator.MAX_PEOPLE_PER_CAR, value=1)
                is_peak_season = st.checkbox("موسم الذروة")
            
            submitted = st.form_submit_button("إضافة مشارك")
            
            if submitted:
                if not name:
                    st.error("الرجاء إدخال اسم المشارك")
                else:
                    # Add participant to session state
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
                    st.success(f"تمت إضافة المشارك {name} بنجاح!")
        
        # Show current participants
        if st.session_state.participants:
            st.header("قائمة المشاركين")
            
            # Convert participants to DataFrame for display
            participants_df = pd.DataFrame(st.session_state.participants)
            participants_df.columns = [
                "الاسم", "عدد الليالي", "أيام السيارة", "نوع الغرفة", 
                "السيارة", "عدد المشاركين", "منظم"
            ]
            
            # Display participants table with edit and delete options
            st.dataframe(participants_df)
            
            # Select participant to edit or delete
            participant_names = [p["name"] for p in st.session_state.participants]
            selected_participant = st.selectbox("اختر مشارك للتعديل أو الحذف", participant_names)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("حذف المشارك"):
                    # Find index of selected participant
                    index = next((i for i, p in enumerate(st.session_state.participants) 
                                 if p["name"] == selected_participant), None)
                    
                    if index is not None:
                        # Remove participant
                        st.session_state.participants.pop(index)
                        st.success(f"تم حذف المشارك {selected_participant} بنجاح!")
                        st.experimental_rerun()
            
            with col2:
                if st.button("تعديل المشارك"):
                    # Find index of selected participant
                    index = next((i for i, p in enumerate(st.session_state.participants) 
                                 if p["name"] == selected_participant), None)
                    
                    if index is not None:
                        # Store selected participant index in session state
                        st.session_state.edit_index = index
                        # Set editing mode
                        st.session_state.editing = True
                        st.experimental_rerun()
            
            # Edit form (appears only in editing mode)
            if st.session_state.get('editing', False):
                edit_index = st.session_state.edit_index
                edit_participant = st.session_state.participants[edit_index]
                
                st.header(f"تعديل بيانات {edit_participant['name']}")
                
                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_name = st.text_input("اسم المشارك", value=edit_participant["name"])
                        edit_nights = st.number_input("عدد الليالي", min_value=1, max_value=14, value=edit_participant["nights"])
                        edit_car_days = st.number_input("أيام استئجار السيارة", min_value=1, max_value=14, value=edit_participant["car_days"])
                        edit_is_organizer = st.checkbox("منظم", value=edit_participant["is_organizer"])
                    
                    with col2:
                        edit_room_type = st.radio("نوع الغرفة", ["زوجية", "فردية"], index=0 if edit_participant["room_type"] == "زوجية" else 1)
                        edit_car_choice = st.radio("سيارة", ["مشاركة", "خاصة"], index=0 if edit_participant["car_choice"] == "مشاركة" else 1)
                        edit_car_sharing = st.number_input("عدد المشاركين في السيارة", 
                                                         min_value=1, 
                                                         max_value=calculator.MAX_PEOPLE_PER_CAR, 
                                                         value=edit_participant["car_sharing"])
                    
                    save_edit = st.form_submit_button("حفظ التعديلات")
                    
                    if save_edit:
                        # Update participant data
                        st.session_state.participants[edit_index] = {
                            "name": edit_name,
                            "nights": edit_nights,
                            "car_days": edit_car_days,
                            "room_type": edit_room_type,
                            "car_choice": edit_car_choice,
                            "car_sharing": edit_car_sharing,
                            "is_organizer": edit_is_organizer
                        }
                        
                        # Exit editing mode
                        st.session_state.editing = False
                        st.success("تم تحديث بيانات المشارك بنجاح!")
                        st.experimental_rerun()
                
                if st.button("إلغاء التعديل"):
                    # Exit editing mode without saving
                    st.session_state.editing = False
                    st.experimental_rerun()
    
    with tab2:
        st.header("حساب التكاليف")
        
        if not st.session_state.participants:
            st.warning("الرجاء إضافة مشاركين أولاً")
        else:
            # Season selection for cost calculation
            is_peak_season = st.checkbox("احتساب تكاليف موسم الذروة")
            
            if st.button("حساب التكاليف"):
                # Calculate costs
                cost_results, total_cost = calculator.calculate_costs(
                    st.session_state.participants, is_peak_season)
                
                if cost_results:
                    # Store results in session state
                    st.session_state.cost_results = cost_results
                    st.session_state.total_cost = total_cost
                    
                    # Display results header
                    st.subheader("تقرير تكاليف رحلة السفاري")
                    st.markdown("---")
                    
                    # Trip information
                    total_participants = len(st.session_state.participants)
                    organizer_count = sum(1 for p in st.session_state.participants if p["is_organizer"])
                    regular_participants = total_participants - organizer_count
                    
                    st.markdown(f"**إجمالي عدد المشاركين:** {total_participants} (منهم {organizer_count} منظم)")
                    st.markdown(f"**نوع الموسم:** {'موسم الذروة' if is_peak_season else 'الموسم العادي'}")
                    st.markdown("---")
                    
                    # Display individual costs
                    for i, cost in enumerate(cost_results, 1):
                        st.markdown(f"### {i}. {cost['name']} ({'منظم' if cost['is_organizer'] else 'مشارك'})")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**تكلفة الإقامة:** {cost['room_cost']:.2f}")
                            if not cost["is_organizer"]:
                                st.markdown(f"**رسوم الدخول:** {cost['entry_fee_cost']:.2f}")
                                st.markdown(f"**تكلفة النقل من/إلى المطار:** {cost['airport_transfer_cost']:.2f}")
                                st.markdown(f"**تكلفة المياه:** {cost['water_cost']:.2f}")
                        
                        with col2:
                            st.markdown(f"**تكلفة الرحلة الداخلية:** {cost['safari_cost']:.2f}")
                            if not cost["is_organizer"]:
                                st.markdown(f"**تكلفة إيجار السيارة:** {cost['car_rental_cost']:.2f}")
                                st.markdown(f"**تكلفة الهدايا:** {cost['gift_cost']:.2f}")
                        
                        st.markdown(f"**إجمالي التكلفة:** {cost['total_cost']:.2f}")
                        st.markdown("---")
                    
                    # Total trip cost
                    st.subheader(f"إجمالي تكلفة الرحلة: {total_cost:.2f}")
                    
                    # Create DataFrame for download
                    cost_df = pd.DataFrame(cost_results)
                    cost_df['نوع المشارك'] = cost_df['is_organizer'].apply(lambda x: 'منظم' if x else 'مشارك')
                    
                    # Rename columns for better readability
                    cost_df = cost_df.rename(columns={
                        'name': 'الاسم',
                        'room_cost': 'تكلفة الإقامة',
                        'entry_fee_cost': 'رسوم الدخول',
                        'safari_cost': 'تكلفة الرحلة الداخلية',
                        'car_rental_cost': 'تكلفة إيجار السيارة',
                        'airport_transfer_cost': 'تكلفة النقل من/إلى المطار',
                        'water_cost': 'تكلفة المياه',
                        'gift_cost': 'تكلفة الهدايا',
                        'total_cost': 'إجمالي التكلفة'
                    })
                    
                    # Drop is_organizer column as we already have نوع المشارك
                    cost_df = cost_df.drop('is_organizer', axis=1)
                    
                    # Generate download link
                    st.markdown(
                        get_download_link(cost_df, 
                                         f"safari_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                         "تنزيل التقرير كملف CSV"),
                        unsafe_allow_html=True
                    )
    
    with tab3:
        st.header("حفظ واستيراد البيانات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Save data
            if st.button("حفظ البيانات الحالية"):
                if not st.session_state.participants:
                    st.warning("لا توجد بيانات للحفظ")
                else:
                    # Create JSON data
                    data = {
                        "participants": st.session_state.participants,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Convert to JSON string
                    json_data = json.dumps(data, ensure_ascii=False, indent=4)
                    
                    # Create download link
                    b64 = base64.b64encode(json_data.encode()).decode()
                    filename = f"safari_trip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    href = f'<a href="data:file/json;base64,{b64}" download="{filename}">تنزيل ملف البيانات</a>'
                    st.markdown(href, unsafe_allow_html=True)
        
        with col2:
            # Load data
            uploaded_file = st.file_uploader("استيراد بيانات", type=["json"])
            
            if uploaded_file is not None:
                try:
                    # Load the uploaded JSON file
                    data = json.load(uploaded_file)
                    
                    # Update session state with loaded participants
                    st.session_state.participants = data.get("participants", [])
                    
                    # Add car_sharing field if missing
                    for participant in st.session_state.participants:
                        if "car_sharing" not in participant:
                            participant["car_sharing"] = 1
                    
                    st.success("تم تحميل البيانات بنجاح!")
                    
                    # Show imported data preview
                    st.subheader("البيانات المستوردة")
                    participants_df = pd.DataFrame(st.session_state.participants)
                    if not participants_df.empty:
                        participants_df.columns = [
                            "الاسم", "عدد الليالي", "أيام السيارة", "نوع الغرفة", 
                            "السيارة", "عدد المشاركين", "منظم"
                        ]
                        st.dataframe(participants_df)
                    
                except Exception as e:
                    st.error(f"حدث خطأ أثناء تحميل البيانات: {str(e)}")

if __name__ == "__main__":
    main()
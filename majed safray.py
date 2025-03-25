#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import datetime

class SafariCostCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("حاسبة تكاليف رحلات السفاري")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        
        # ثوابت للحسابات
        self.ENTRY_FEE_REGULAR = 100  # رسوم الدخول العادية
        self.ENTRY_FEE_PEAK = 200     # رسوم الدخول في الموسم
        self.SINGLE_ROOM_COST = 300   # تكلفة الغرفة الفردية
        self.DOUBLE_ROOM_COST = 180   # تكلفة الغرفة المزدوجة
        self.ORGANIZER_ROOM_COST = 150  # تكلفة غرفة المنظم
        self.SAFARI_COST = 400        # تكلفة الرحلة الداخلية
        self.CAR_RENTAL_COST = 170    # تكلفة إيجار السيارة يومياً
        self.AIRPORT_TRANSFER_COST = 200  # تكلفة النقل من وإلى المطار
        self.WATER_COST = 50          # تكلفة المياه
        self.GIFT_COST = 10           # تكلفة الهدايا
        self.MAX_PEOPLE_PER_CAR = 3   # الحد الأقصى للمشاركين في سيارة واحدة
        
        # متغيرات البرنامج
        self.participants = []
        self.is_peak_season = tk.BooleanVar(value=False)
        self.current_participant_index = None
        
        # إنشاء الواجهة
        self.create_widgets()
    
    def create_widgets(self):
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill="both")
        
        # إطار إضافة مشارك جديد
        input_frame = ttk.LabelFrame(main_frame, text="بيانات المشارك", padding="10")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # الصف الأول من الإدخالات
        row1 = ttk.Frame(input_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Label(row1, text="اسم المشارك:").pack(side="right", padx=5)
        self.name_entry = ttk.Entry(row1, width=20)
        self.name_entry.pack(side="right", padx=5)
        
        ttk.Label(row1, text="نوع المشارك:").pack(side="right", padx=5)
        self.is_organizer = tk.BooleanVar(value=False)
        ttk.Checkbutton(row1, text="منظم", variable=self.is_organizer).pack(side="right", padx=5)
        
        # الصف الثاني من الإدخالات
        row2 = ttk.Frame(input_frame)
        row2.pack(fill="x", pady=5)
        
        ttk.Label(row2, text="عدد الليالي:").pack(side="right", padx=5)
        self.nights_values = [str(i) for i in range(1, 15)]
        self.nights_combo = ttk.Combobox(row2, values=self.nights_values, width=5)
        self.nights_combo.current(0)
        self.nights_combo.pack(side="right", padx=5)
        
        ttk.Label(row2, text="أيام استئجار السيارة:").pack(side="right", padx=5)
        self.car_days_values = [str(i) for i in range(1, 15)]
        self.car_days_combo = ttk.Combobox(row2, values=self.car_days_values, width=5)
        self.car_days_combo.current(0)
        self.car_days_combo.pack(side="right", padx=5)
        
        # الصف الثالث من الإدخالات
        row3 = ttk.Frame(input_frame)
        row3.pack(fill="x", pady=5)
        
        ttk.Label(row3, text="نوع الغرفة:").pack(side="right", padx=5)
        self.room_type = tk.StringVar(value="زوجية")
        ttk.Radiobutton(row3, text="فردية", variable=self.room_type, value="فردية").pack(side="right", padx=5)
        ttk.Radiobutton(row3, text="زوجية", variable=self.room_type, value="زوجية").pack(side="right", padx=5)
        
        ttk.Label(row3, text="سيارة:").pack(side="right", padx=5)
        self.car_choice = tk.StringVar(value="مشاركة")
        ttk.Radiobutton(row3, text="خاصة", variable=self.car_choice, value="خاصة").pack(side="right", padx=5)
        ttk.Radiobutton(row3, text="مشاركة", variable=self.car_choice, value="مشاركة").pack(side="right", padx=5)
        
        # عدد المشاركين في السيارة
        ttk.Label(row3, text="عدد المشاركين في السيارة:").pack(side="right", padx=5)
        self.car_sharing_values = [str(i) for i in range(1, self.MAX_PEOPLE_PER_CAR + 1)]
        self.car_sharing_combo = ttk.Combobox(row3, values=self.car_sharing_values, width=3)
        self.car_sharing_combo.current(0)  # افتراضي 1
        self.car_sharing_combo.pack(side="right", padx=5)
        
        ttk.Label(row3, text="الموسم:").pack(side="right", padx=5)
        ttk.Checkbutton(row3, text="موسم الذروة", variable=self.is_peak_season).pack(side="right", padx=5)
        
        # أزرار الإضافة والتعديل والحذف
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill="x", pady=10)
        
        self.add_button = ttk.Button(button_frame, text="إضافة مشارك", command=self.add_participant)
        self.add_button.pack(side="right", padx=5)
        
        self.update_button = ttk.Button(button_frame, text="تحديث بيانات", command=self.update_participant, state="disabled")
        self.update_button.pack(side="right", padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="حذف مشارك", command=self.delete_participant, state="disabled")
        self.delete_button.pack(side="right", padx=5)
        
        self.calculate_button = ttk.Button(button_frame, text="حساب التكاليف", command=self.calculate_all_costs)
        self.calculate_button.pack(side="left", padx=5)
        
        self.save_button = ttk.Button(button_frame, text="حفظ البيانات", command=self.save_data)
        self.save_button.pack(side="left", padx=5)
        
        self.load_button = ttk.Button(button_frame, text="استيراد بيانات", command=self.load_data)
        self.load_button.pack(side="left", padx=5)
        
        self.export_button = ttk.Button(button_frame, text="تصدير إلى Excel/CSV", command=self.export_data)
        self.export_button.pack(side="left", padx=5)
        
        # جدول المشاركين
        participant_frame = ttk.LabelFrame(main_frame, text="قائمة المشاركين", padding="10")
        participant_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("name", "nights", "car_days", "room_type", "car_choice", "car_sharing", "is_organizer")
        self.tree = ttk.Treeview(participant_frame, columns=columns, show="headings")
        
        self.tree.heading("name", text="الاسم")
        self.tree.heading("nights", text="الليالي")
        self.tree.heading("car_days", text="أيام السيارة")
        self.tree.heading("room_type", text="نوع الغرفة")
        self.tree.heading("car_choice", text="السيارة")
        self.tree.heading("car_sharing", text="عدد المشاركين")
        self.tree.heading("is_organizer", text="المنظم")
        
        self.tree.column("name", width=150)
        self.tree.column("nights", width=80)
        self.tree.column("car_days", width=80)
        self.tree.column("room_type", width=80)
        self.tree.column("car_choice", width=80)
        self.tree.column("car_sharing", width=80)
        self.tree.column("is_organizer", width=80)
        
        scrollbar = ttk.Scrollbar(participant_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ربط حدث تحديد صف في الجدول
        self.tree.bind("<<TreeviewSelect>>", self.on_participant_select)
        
        # إطار النتائج
        results_frame = ttk.LabelFrame(main_frame, text="النتائج", padding="10")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill="both", expand=True)
    
    def add_participant(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("خطأ", "الرجاء إدخال اسم المشارك")
            return
        
        # جمع البيانات
        participant = {
            "name": name,
            "nights": int(self.nights_combo.get()),
            "car_days": int(self.car_days_combo.get()),
            "room_type": self.room_type.get(),
            "car_choice": self.car_choice.get(),
            "car_sharing": int(self.car_sharing_combo.get()),
            "is_organizer": self.is_organizer.get()
        }
        
        # إضافة إلى القائمة وتحديث الجدول
        self.participants.append(participant)
        self.update_participants_tree()
        self.clear_inputs()
    
    def update_participant(self):
        if self.current_participant_index is None:
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("خطأ", "الرجاء إدخال اسم المشارك")
            return
        
        # تحديث بيانات المشارك
        self.participants[self.current_participant_index] = {
            "name": name,
            "nights": int(self.nights_combo.get()),
            "car_days": int(self.car_days_combo.get()),
            "room_type": self.room_type.get(),
            "car_choice": self.car_choice.get(),
            "car_sharing": int(self.car_sharing_combo.get()),
            "is_organizer": self.is_organizer.get()
        }
        
        # تحديث الجدول
        self.update_participants_tree()
        self.clear_inputs()
        
        # تعطيل أزرار التعديل والحذف
        self.update_button.config(state="disabled")
        self.delete_button.config(state="disabled")
        self.add_button.config(state="normal")
        self.current_participant_index = None
    
    def delete_participant(self):
        if self.current_participant_index is None:
            return
        
        # حذف المشارك
        del self.participants[self.current_participant_index]
        
        # تحديث الجدول
        self.update_participants_tree()
        self.clear_inputs()
        
        # تعطيل أزرار التعديل والحذف
        self.update_button.config(state="disabled")
        self.delete_button.config(state="disabled")
        self.add_button.config(state="normal")
        self.current_participant_index = None
    
    def on_participant_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        index = int(self.tree.item(item, "tags")[0])
        self.current_participant_index = index
        
        # عرض بيانات المشارك المحدد في نموذج الإدخال
        participant = self.participants[index]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, participant["name"])
        self.nights_combo.set(str(participant["nights"]))
        self.car_days_combo.set(str(participant["car_days"]))
        self.room_type.set(participant["room_type"])
        self.car_choice.set(participant["car_choice"])
        self.car_sharing_combo.set(str(participant["car_sharing"]))
        self.is_organizer.set(participant["is_organizer"])
        
        # تفعيل أزرار التعديل والحذف
        self.update_button.config(state="normal")
        self.delete_button.config(state="normal")
        self.add_button.config(state="disabled")
    
    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.nights_combo.current(0)
        self.car_days_combo.current(0)
        self.room_type.set("زوجية")
        self.car_choice.set("مشاركة")
        self.car_sharing_combo.current(0)
        self.is_organizer.set(False)
    
    def update_participants_tree(self):
        # حذف كل الصفوف
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # إضافة المشاركين
        for i, participant in enumerate(self.participants):
            organizer_status = "نعم" if participant["is_organizer"] else "لا"
            self.tree.insert("", tk.END, values=(
                participant["name"],
                participant["nights"],
                participant["car_days"],
                participant["room_type"],
                participant["car_choice"],
                participant["car_sharing"],
                organizer_status
            ), tags=(str(i),))
    
    def calculate_all_costs(self):
        if not self.participants:
            messagebox.showinfo("تنبيه", "الرجاء إضافة مشاركين أولاً")
            return
        
        # إجمالي عدد المشاركين (باستثناء المنظم)
        regular_participants = [p for p in self.participants if not p["is_organizer"]]
        total_regular_participants = len(regular_participants)
        
        # إجمالي جميع المشاركين
        total_participants = len(self.participants)
        
        # احتساب التكاليف لكل مشارك
        results = []
        total_cost = 0
        
        for participant in self.participants:
            cost_details = {}
            
            # رسوم الدخول
            entry_fee = self.ENTRY_FEE_PEAK if self.is_peak_season.get() else self.ENTRY_FEE_REGULAR
            
            if participant["is_organizer"]:
                # المنظم يدفع فقط تكلفة الفندق والرحلة الداخلية
                room_cost = self.ORGANIZER_ROOM_COST * participant["nights"]
                safari_cost = self.SAFARI_COST  # المنظم يدفع تكلفة الرحلة الداخلية
                
                # باقي التكاليف صفر للمنظم
                entry_fee_cost = 0
                car_rental_cost = 0
                airport_transfer_cost = 0
                water_cost = 0
                gift_cost = 0
            else:
                # رسوم الإقامة حسب نوع الغرفة
                if participant["room_type"] == "فردية":
                    room_cost = self.SINGLE_ROOM_COST * participant["nights"]
                else:  # زوجية
                    room_cost = self.DOUBLE_ROOM_COST * participant["nights"]
                
                # تكاليف رسوم الدخول
                entry_fee_cost = entry_fee * participant["nights"]
                
                # تكلفة الرحلة الداخلية
                safari_cost = self.SAFARI_COST
                
                # تكلفة إيجار السيارة
                if participant["car_choice"] == "خاصة":
                    car_rental_cost = self.CAR_RENTAL_COST * participant["car_days"]
                else:  # مشاركة
                    # استخدام عدد المشاركين في السيارة من بيانات المشارك
                    if participant["car_sharing"] > 0:
                        car_rental_cost = (self.CAR_RENTAL_COST * participant["car_days"]) / participant["car_sharing"]
                    else:
                        car_rental_cost = 0
                
                # تكلفة النقل من وإلى المطار - تقسم على المشاركين فقط (بدون المنظم)
                airport_transfer_cost = self.AIRPORT_TRANSFER_COST / total_regular_participants if total_regular_participants > 0 else 0
                
                # تكلفة المياه (تقسم على عدد الليالي)
                water_cost = self.WATER_COST / participant["nights"] if participant["nights"] > 0 else 0
                
                # تكلفة الهدايا
                gift_cost = self.GIFT_COST
            
            # إجمالي التكلفة للمشارك
            total_participant_cost = (
                room_cost + entry_fee_cost + safari_cost + car_rental_cost + 
                airport_transfer_cost + water_cost + gift_cost
            )
            
            # تجميع تفاصيل التكاليف
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
        
        # عرض النتائج
        self.display_results(results, total_cost, total_participants, total_regular_participants)
    
    def display_results(self, results, total_cost, total_participants, total_regular_participants):
        self.results_text.delete(1.0, tk.END)
        
        # ترويسة
        self.results_text.insert(tk.END, "تقرير تكاليف رحلة السفاري\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # معلومات الرحلة
        self.results_text.insert(tk.END, f"إجمالي عدد المشاركين: {total_participants} (منهم {total_participants - total_regular_participants} منظم)\n")
        season_type = "موسم الذروة" if self.is_peak_season.get() else "الموسم العادي"
        self.results_text.insert(tk.END, f"نوع الموسم: {season_type}\n\n")
        
        # تفاصيل تكاليف كل مشارك
        for i, cost_details in enumerate(results, 1):
            participant_type = "منظم" if cost_details["is_organizer"] else "مشارك"
            self.results_text.insert(tk.END, f"{i}. {cost_details['name']} ({participant_type})\n")
            self.results_text.insert(tk.END, f"   تكلفة الإقامة: {cost_details['room_cost']:.2f}\n")
            
            if cost_details["is_organizer"]:
                self.results_text.insert(tk.END, f"   تكلفة الرحلة الداخلية: {cost_details['safari_cost']:.2f}\n")
            else:
                self.results_text.insert(tk.END, f"   رسوم الدخول: {cost_details['entry_fee_cost']:.2f}\n")
                self.results_text.insert(tk.END, f"   تكلفة الرحلة الداخلية: {cost_details['safari_cost']:.2f}\n")
                self.results_text.insert(tk.END, f"   تكلفة إيجار السيارة: {cost_details['car_rental_cost']:.2f}\n")
                self.results_text.insert(tk.END, f"   تكلفة النقل من/إلى المطار: {cost_details['airport_transfer_cost']:.2f}\n")
                self.results_text.insert(tk.END, f"   تكلفة المياه: {cost_details['water_cost']:.2f}\n")
                self.results_text.insert(tk.END, f"   تكلفة الهدايا: {cost_details['gift_cost']:.2f}\n")
            
            self.results_text.insert(tk.END, f"   إجمالي التكلفة: {cost_details['total_cost']:.2f}\n\n")
        
        # إجمالي تكلفة الرحلة
        self.results_text.insert(tk.END, "=" * 50 + "\n")
        self.results_text.insert(tk.END, f"إجمالي تكلفة الرحلة: {total_cost:.2f}\n")
        
        # تاريخ الحساب
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results_text.insert(tk.END, f"\nتاريخ التقرير: {current_date}")
        
        # حفظ النتائج للتصدير
        self.cost_results = results
    
    def save_data(self):
        if not self.participants:
            messagebox.showinfo("تنبيه", "لا توجد بيانات للحفظ")
            return
        
        # حفظ البيانات في ملف
        try:
            data = {
                "participants": self.participants,
                "is_peak_season": self.is_peak_season.get(),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            filename = f"safari_trip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("نجاح", f"تم حفظ البيانات في الملف: {filename}")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ البيانات: {str(e)}")
    
    def load_data(self):
        try:
            filename = filedialog.askopenfilename(
                title="اختر ملف البيانات",
                filetypes=[("ملفات JSON", "*.json"), ("جميع الملفات", "*.*")]
            )
            
            if not filename:
                return
            
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # تحميل البيانات
            self.participants = data.get("participants", [])
            
            # إضافة حقل عدد المشاركين في السيارة إذا لم يكن موجوداً
            for participant in self.participants:
                if "car_sharing" not in participant:
                    participant["car_sharing"] = 1
            
            self.is_peak_season.set(data.get("is_peak_season", False))
            
            # تحديث الواجهة
            self.update_participants_tree()
            
            messagebox.showinfo("نجاح", "تم تحميل البيانات بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل البيانات: {str(e)}")
    
    def export_data(self):
        if not hasattr(self, "cost_results"):
            messagebox.showinfo("تنبيه", "الرجاء حساب التكاليف أولاً قبل التصدير")
            return
        
        try:
            filetypes = [("ملفات CSV", "*.csv"), ("جميع الملفات", "*.*")]
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=filetypes,
                title="حفظ التقرير"
            )
            
            if not filename:
                return
            
            with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
                csv_writer = csv.writer(csvfile)
                
                # كتابة العناوين
                headers = [
                    "الاسم", "نوع المشارك", "تكلفة الإقامة", "رسوم الدخول", 
                    "الرحلة الداخلية", "إيجار السيارة", "النقل من/إلى المطار", 
                    "تكلفة المياه", "تكلفة الهدايا", "إجمالي التكلفة"
                ]
                csv_writer.writerow(headers)
                
                # كتابة البيانات
                for cost in self.cost_results:
                    participant_type = "منظم" if cost["is_organizer"] else "مشارك"
                    row = [
                        cost["name"], participant_type, round(cost["room_cost"], 2),
                        round(cost["entry_fee_cost"], 2), round(cost["safari_cost"], 2),
                        round(cost["car_rental_cost"], 2), round(cost["airport_transfer_cost"], 2),
                        round(cost["water_cost"], 2), round(cost["gift_cost"], 2),
                        round(cost["total_cost"], 2)
                    ]
                    csv_writer.writerow(row)
                
                # إضافة الإجمالي
                total_cost = sum(cost["total_cost"] for cost in self.cost_results)
                csv_writer.writerow([])
                csv_writer.writerow(["إجمالي التكلفة", "", "", "", "", "", "", "", "", round(total_cost, 2)])
            
            messagebox.showinfo("نجاح", f"تم تصدير البيانات إلى: {filename}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير البيانات: {str(e)}")


# تشغيل التطبيق
if __name__ == "__main__":
    root = tk.Tk()
    app = SafariCostCalculator(root)
    root.mainloop() 


import os
import sqlite3
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة لتكون متوافقة مع الموبايل والحاسوب
st.set_page_config(
    page_title="نظام إدارة حضور ودرجات الطلاب - ثائر قحطان",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# دعم الاتجاه من اليمين لليسار (RTL) وتنسيق التصميم
st.markdown(
    """
    <style>
    body, div, span, label, input, button {
        direction: rtl;
        text-align: right;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background-color: #eef2f7;
        color: #182957;
    }
    .header-box {
        background-color: #182957;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

APP_NAME = "نظام إدارة حضور ودرجات الطلاب"
TEACHER = "THAER ALJUMAILY"
DB_FILE = "school_system_web.db"
SECTIONS = ["A", "B", "C", "D", "E", "F", "G", "H"]
TERMS = ["الفصل الأول", "امتحان نصف السنة", "الفصل الثاني", "امتحان نهاية السنة"]


def init_db():
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            subject TEXT DEFAULT 'الفيزياء',
            name TEXT NOT NULL, 
            grade TEXT DEFAULT '', 
            section TEXT DEFAULT 'A',
            attendance REAL DEFAULT 0, 
            absence REAL DEFAULT 0,
            participation REAL DEFAULT 0, 
            activity REAL DEFAULT 0,
            term1 REAL DEFAULT 0, 
            mid_year REAL DEFAULT 0, 
            term2 REAL DEFAULT 0, 
            end_year REAL DEFAULT 0,
            attendance2 REAL DEFAULT 0, 
            absence2 REAL DEFAULT 0, 
            participation2 REAL DEFAULT 0, 
            activity2 REAL DEFAULT 0
        )
    """)
  conn.commit()
  conn.close()


init_db()

# الترويسة الرئيسية
st.markdown(
    f"""
    <div class="header-box">
        <h2>{APP_NAME}</h2>
        <p style="margin: 0; font-size: 16px; color: #d9e5ff;">{TEACHER}</p>
    </div>
""",
    unsafe_allow_html=True,
)

# الشريط الجانبي لإدخال وتعديل بيانات الطلاب
with st.sidebar:
  st.header("📌 إدخال بيانات الطالب والدرجات")

  name = st.text_input("اسم الطالب الثلاثي")
  grade_input = st.text_input("الصف الدراسي")
  section_input = st.selectbox("الشعبة", SECTIONS)
  subject_input = st.text_input("اسم المادة الدراسية", "الفيزياء")
  selected_term = st.selectbox("الفصل الدراسي الحالي", TERMS)

  st.subheader("📝 درجات النشاط والحضور اليومي")
  attendance = st.number_input("الحضور", 0.0, 10.0, 0.0, 0.5)
  absence = st.number_input("الغياب", 0.0, 10.0, 0.0, 0.5)
  participation = st.number_input("المشاركة", 0.0, 10.0, 0.0, 0.5)
  activity = st.number_input("النشاط الصفي", 0.0, 10.0, 0.0, 0.5)

  st.subheader("📊 الدرجات الامتحانية للفصول")
  term1 = st.number_input("امتحان الفصل الأول (من 100)", 0.0, 100.0, 0.0)
  mid_year = st.number_input("امتحان نصف السنة (من 100)", 0.0, 100.0, 0.0)
  term2 = st.number_input("امتحان الفصل الثاني (من 100)", 0.0, 100.0, 0.0)
  end_year = st.number_input("امتحان نهاية السنة (من 100)", 0.0, 100.0, 0.0)

  if st.button("➕ حفظ وإضافة الطالب الجديد", use_container_width=True):
    if name.strip():
      conn = sqlite3.connect(DB_FILE)
      c = conn.cursor()
      c.execute(
          """
                INSERT INTO students (subject, name, grade, section, attendance, absence, participation, activity, term1, mid_year, term2, end_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
          (
              subject_input,
              name.strip(),
              grade_input,
              section_input,
              attendance,
              absence,
              participation,
              activity,
              term1,
              mid_year,
              term2,
              end_year,
          ),
      )
      conn.commit()
      conn.close()
      st.success("تمت إضافة الطالب بنجاح!")
      st.rerun()
    else:
      st.warning("يرجى إدخال اسم الطالب على الأقل!")

# استرجاع وعرض البيانات في الجداول
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql_query("SELECT * FROM students", conn)
conn.close()

if not df.empty:
  # حساب المجاميع والمعدلات بدقة وفقاً لنظامك المعتمد
  df["مجموع الفصل الأول"] = (
      df["attendance"]
      + df["absence"]
      + df["participation"]
      + df["activity"]
      + df["term1"]
  )
  df["مجموع الفصل الثاني"] = (
      df["attendance2"]
      + df["absence2"]
      + df["participation2"]
      + df["activity2"]
      + df["term2"]
  )

  # حساب المعدل النهائي استناداً للدرجات المدخلة
  def calc_average(row):
    entered = [
        row["مجموع الفصل الأول"],
        row["mid_year"],
        row["مجموع الفصل الثاني"],
        row["end_year"],
    ]
    valid = [v for v in entered if v > 0]
    return round(sum(valid) / len(valid), 2) if valid else 0.0

  df["المعدل النهائي"] = df.apply(calc_average, axis=1)

  # ألسنة العرض المتبوبة (Tabs) تطابق تماماً تبويبات برنامجك المكتبي
  tab1, tab2, tab3, tab4, tab5 = st.tabs([
      "درجات الفصل الأول",
      "درجات الفصل الثاني",
      "نصف السنة",
      "نهاية السنة",
      "الدرجات النهائية والتقارير",
  ])

  with tab1:
    st.subheader("سجل درجات الفصل الأول والحضور اليومي")
    st.dataframe(
        df[[
            "id",
            "name",
            "grade",
            "section",
            "attendance",
            "absence",
            "participation",
            "activity",
            "term1",
            "مجموع الفصل الأول",
        ]].rename(columns={
            "id": "ت",
            "name": "اسم الطالب",
            "grade": "الصف",
            "section": "الشعبة",
            "attendance": "الحضور",
            "absence": "الغياب",
            "participation": "المشاركة",
            "activity": "النشاط",
            "term1": "امتحان الفصل الأول",
        }),
        use_container_width=True,
    )

  with tab2:
    st.subheader("سجل درجات الفصل الثاني")
    st.dataframe(
        df[[
            "id",
            "name",
            "grade",
            "section",
            "term2",
            "مجموع الفصل الثاني",
        ]].rename(columns={
            "id": "ت",
            "name": "اسم الطالب",
            "grade": "الصف",
            "section": "الشعبة",
            "term2": "امتحان الفصل الثاني",
        }),
        use_container_width=True,
    )

  with tab3:
    st.subheader("درجات امتحان نصف السنة")
    st.dataframe(
        df[["id", "name", "grade", "section", "mid_year"]].rename(columns={
            "id": "ت",
            "name": "اسم الطالب",
            "grade": "الصف",
            "section": "الشعبة",
            "mid_year": "نصف السنة",
        }),
        use_container_width=True,
    )

  with tab4:
    st.subheader("درجات امتحان نهاية السنة")
    st.dataframe(
        df[["id", "name", "grade", "section", "end_year"]].rename(columns={
            "id": "ت",
            "name": "اسم الطالب",
            "grade": "الصف",
            "section": "الشعبة",
            "end_year": "نهاية السنة",
        }),
        use_container_width=True,
    )

  with tab5:
    st.subheader("لوحة المعدلات النهائية والنتائج الشاملة")
    st.dataframe(
        df[[
            "id",
            "name",
            "grade",
            "section",
            "مجموع الفصل الأول",
            "mid_year",
            "مجموع الفصل الثاني",
            "end_year",
            "المعدل النهائي",
        ]].rename(columns={
            "id": "ت",
            "name": "اسم الطالب",
            "grade": "الصف",
            "section": "الشعبة",
            "mid_year": "نصف السنة",
            "end_year": "نهاية السنة",
        }),
        use_container_width=True,
    )
else:
  st.info("لا توجد بيانات طلاب مسجلة حتى الآن. استخدم الشريط الجانبي للإضافة.")
import streamlit as st
import sqlite3
import os
from datetime import datetime
import fitz
from PIL import Image
import io

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Alayadivembu M.P.C.S Ltd", layout="wide")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# DATABASE
# -------------------------
conn = sqlite3.connect("portal.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS files (
    filename TEXT,
    month TEXT,
    uploaded_by TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS audit (
    action TEXT,
    filename TEXT,
    time TEXT
)
""")

conn.commit()

# -------------------------
# MONTH FUNCTION
# -------------------------
def get_month():
    return datetime.now().strftime("%B")

# -------------------------
# HEADER
# -------------------------
st.markdown("""
<div style="
    background: linear-gradient(90deg, #0d47a1, #1565c0);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    font-size: 35px;
    font-weight: bold;
">
Alayadivembu M.P.C.S Ltd
</div>
""", unsafe_allow_html=True)

# -------------------------
# PDF VIEWER (FIXED)
# -------------------------
def pdf_viewer(file_path):

    doc = fitz.open(file_path)
    total_pages = len(doc)

    if "page" not in st.session_state:
        st.session_state.page = 0

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Previous"):
            if st.session_state.page > 0:
                st.session_state.page -= 1

    with col2:
        st.write(f"📄 Page {st.session_state.page + 1} / {total_pages}")

    with col3:
        if st.button("➡️ Next"):
            if st.session_state.page < total_pages - 1:
                st.session_state.page += 1

    zoom = st.slider("🔍 Zoom", 1.0, 3.0, 1.5)

    page = doc.load_page(st.session_state.page)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    img = Image.open(io.BytesIO(pix.tobytes("png")))

    st.image(img, use_container_width=True)

# -------------------------
# UPLOAD SECTION (FIXED)
# -------------------------
st.subheader("📤 Upload PDF")

file = st.file_uploader("Choose PDF", type=["pdf"])

if file:

    file_path = os.path.join(UPLOAD_FOLDER, file.name)

    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    month = get_month()

    c.execute(
        "INSERT INTO files VALUES (?,?,?)",
        (file.name, month, "ADMIN")
    )

    c.execute(
        "INSERT INTO audit VALUES (?,?,?)",
        ("UPLOAD", file.name, str(datetime.now()))
    )

    conn.commit()

    st.success("Uploaded Successfully ✅")

# -------------------------
# MONTH FILTER
# -------------------------
st.subheader("📂 Documents")

months = ["All","January","February","March","April","May","June",
          "July","August","September","October","November","December"]

selected_month = st.selectbox("📅 Select Month", months)

# -------------------------
# FETCH DATA (FIXED)
# -------------------------
if selected_month == "All":
    c.execute("SELECT * FROM files")
else:
    c.execute("SELECT * FROM files WHERE month=?", (selected_month,))

files = c.fetchall()

# -------------------------
# DISPLAY FILES
# -------------------------
if len(files) == 0:
    st.info("📭 No documents available")
else:

    for fdata in files:

        file_path = os.path.join(UPLOAD_FOLDER, fdata[0])

        col1, col2 = st.columns([4,1])

        with col1:
            st.write(f"📄 {fdata[0]}  |  📅 {fdata[1]}")

        with col2:

            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button("⬇️ Download", f, fdata[0])

            if st.button(f"👁 View {fdata[0]}"):
                st.session_state["pdf"] = file_path

# -------------------------
# PDF PREVIEW SECTION (FIXED)
# -------------------------
if "pdf" in st.session_state:

    if os.path.exists(st.session_state["pdf"]):

        st.markdown("---")
        st.subheader("📄 PDF Viewer")

        pdf_viewer(st.session_state["pdf"])

# -------------------------
# FOOTER
# -------------------------
st.markdown("""
---
<center>
<b>Created by K. Kiruvaran</b>
</center>
""", unsafe_allow_html=True)
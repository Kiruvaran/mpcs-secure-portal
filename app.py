import streamlit as st
import sqlite3
import os
import hashlib
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

c.execute("""CREATE TABLE IF NOT EXISTS files (
    filename TEXT,
    month TEXT,
    uploaded_by TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS audit (
    action TEXT,
    filename TEXT,
    time TEXT
)""")

conn.commit()

# -------------------------
# SECURITY (HIDDEN ADMIN)
# -------------------------
ADMIN_KEY = "ALAYA2026"
ADMIN_HASH = hashlib.sha256(ADMIN_KEY.encode()).hexdigest()

key = st.query_params.get("admin_key", "")

def is_admin(k):
    return hashlib.sha256(k.encode()).hexdigest() == ADMIN_HASH

admin_mode = is_admin(key)

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
# ADVANCED PDF VIEWER
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
# ADMIN PANEL (HIDDEN)
# -------------------------
if admin_mode:

    st.success("🔐 ADMIN MODE ACTIVE")

    st.header("📤 Upload Documents")

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:

        path = os.path.join(UPLOAD_FOLDER, file.name)

        with open(path, "wb") as f:
            f.write(file.getbuffer())

        c.execute("INSERT INTO files VALUES (?,?,?)",
                  (file.name, "ADMIN", "ADMIN"))

        c.execute("INSERT INTO audit VALUES (?,?,?)",
                  ("UPLOAD", file.name, str(datetime.now())))

        conn.commit()

        st.success("Uploaded Successfully ✅")

# -------------------------
# PUBLIC VIEW
# -------------------------
st.subheader("📂 Documents")

c.execute("SELECT * FROM files")
files = c.fetchall()

if not files:
    st.info("No documents available")
else:

    for fdata in files:

        file_path = os.path.join(UPLOAD_FOLDER, fdata[0])

        col1, col2 = st.columns([4,1])

        with col1:
            st.write("📄", fdata[0])

        with col2:

            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button("⬇️ Download", f, fdata[0])

            if st.button(f"👁 View {fdata[0]}"):
                st.session_state["pdf"] = file_path

# -------------------------
# PDF VIEW SECTION
# -------------------------
if "pdf" in st.session_state:
    st.markdown("---")
    st.subheader("📄 Advanced PDF Viewer")

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
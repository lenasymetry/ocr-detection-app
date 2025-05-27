import streamlit as st
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import numpy as np
import cv2
import io

# ------------------------
# Logo
# ------------------------
logo = Image.open("mon_logo.png")
st.image(logo, width=150)

# ------------------------
# Titre
# ------------------------
st.title("🧾 OCR Multi-documents : Détection du type")
st.write("Importe plusieurs fichiers (PDF ou images) pour détecter le type de document.")

# ------------------------
# Mots-clés par type
# ------------------------
types_documents = {
    "Carte d'identité": ["RÉPUBLIQUE", "FRANÇAISE", "CARD", "NATIONALE", "NATIONALITÉ"],
    "Passeport": ["PASSEPORT", "NUMÉRO", "AUTORITÉ", "DATE DE NAISSANCE", "SIGNATURE", "RÉPUBLIQUE"],
    "Titre de séjour": ["SÉJOUR", "TITRE", "RÉSIDENCE", "RESIDENCE", "PERMIT"],
    "Carte Vitale": ["ASSURANCE", "MALADIE", "CARTE", "VITALE"],
}

# ------------------------
# OCR image
# ------------------------
def extraire_texte_image(image):
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gris = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    texte = pytesseract.image_to_string(gris, lang="fra+eng")
    return texte

# ------------------------
# Détection type document
# ------------------------
def reconnaitre_document(image):
    texte = extraire_texte_image(image)
    mots_trouves = set()
    type_reconnu = "Type inconnu"

    for type_doc, mots in types_documents.items():
        for mot in mots:
            if mot.upper() in texte.upper():
                mots_trouves.add(mot)
        if len(mots_trouves.intersection(mots)) >= 2:
            type_reconnu = type_doc
            break

    return texte, mots_trouves, type_reconnu

# ------------------------
# Chargement PDF -> Image
# ------------------------
def convertir_pdf_en_image(pdf_bytes):
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

# ------------------------
# Upload multi-fichiers
# ------------------------
uploaded_files = st.file_uploader(
    "Choisis un ou plusieurs fichiers (PDF, JPG, PNG...)",
    type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff"],
    accept_multiple_files=True
)

# ------------------------
# Traitement de chaque fichier
# ------------------------
if uploaded_files:
    for file in uploaded_files:
        st.divider()
        st.markdown(f"### 📄 Fichier : `{file.name}`")

        ext = file.name.lower().split(".")[-1]

        if ext == "pdf":
            images = convertir_pdf_en_image(file.read())
        else:
            images = [Image.open(file)]

        for idx, image in enumerate(images):
            if len(images) > 1:
                st.markdown(f"#### 🖼️ Page {idx+1}")
            else:
                st.markdown("#### 🖼️ Image détectée")

            st.image(image, use_column_width=True)

            texte, mots, type_doc = reconnaitre_document(image)

            st.markdown(f"**Type détecté :** `{type_doc}`")
            st.markdown(f"**Mots-clés trouvés :** {', '.join(mots) if mots else 'Aucun'}")

            with st.expander("📝 Texte OCR brut"):
                st.text(texte)


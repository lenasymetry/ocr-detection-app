import streamlit as st
from PIL import Image
import pytesseract
import pdf2image
import tempfile
import os
import cv2
import numpy as np

st.set_page_config(page_title="Détection OCR de documents", layout="wide")

# Logo (optionnel)
try:
    logo = Image.open("mon_logo.png")
    st.image(logo, width=150)
except:
    pass

st.title("🧾 Détection OCR des types de documents")
st.write("Importe une ou plusieurs images/PDF pour détecter s’il s’agit d’un passeport, carte d’identité, titre de séjour, etc.")

# Liste des mots-clés par type de document
types_documents = {
    "Carte d'identité": ["RÉPUBLIQUE", "FRANÇAISE", "NATIONALE", "CNI"],
    "Passeport": ["PASSEPORT", "RÉPUBLIQUE", "FRANÇAISE"],
    "Titre de séjour": ["TITRE DE SÉJOUR", "RESIDENCE PERMIT", "PERMIS DE SÉJOUR"],
    "Carte Vitale": ["CARTE", "VITALE", "ASSURANCE", "MALADIE"],
}

def detecter_type_document(texte):
    texte_up = texte.upper()
    
    def au_moins_n_mots(mots, n=2):
        compte = sum(1 for mot in mots if mot in texte_up)
        return compte >= n
    
    if au_moins_n_mots(["RÉPUBLIQUE", "FRANÇAISE", "CARTE", "IDENTITÉ"], 2):
        return "Carte d'identité"
    
    if au_moins_n_mots(["RÉPUBLIQUE", "FRANÇAISE", "PASSEPORT"], 2):
        return "Passeport"
    
    if au_moins_n_mots(["RESIDENCE PERMIT", "TITRE DE SÉJOUR"], 1):
        return "Titre de séjour"
    
    if au_moins_n_mots(["ASSURANCE", "MALADIE", "VITALE"], 2):
        return "Carte Vitale"
    
    return "Type inconnu"


# Fonction pour extraire l’identité (simplifiée)
def extraire_identite(type_doc, texte):
    lignes = [l.strip() for l in texte.splitlines() if l.strip()]
    nom = prenom = None

    if type_doc == "Carte d'identité":
        for i, l in enumerate(lignes):
            if "NOM" in l.upper() and i + 1 < len(lignes):
                nom = lignes[i + 1]
            if "PRÉNOM" in l.upper() and i + 1 < len(lignes):
                prenom = lignes[i + 1]

    elif type_doc == "Carte Vitale":
        maj = [l for l in lignes if l.isupper()]
        if len(maj) >= 2:
            prenom, nom = maj[-2], maj[-1]

    elif type_doc == "Titre de séjour":
        for i, l in enumerate(lignes):
            if "NOM PRÉNOM" in l.upper() or "NOM PRÉNOMS" in l.upper():
                if i + 1 < len(lignes):
                    full = lignes[i + 1].split()
                    if len(full) >= 2:
                        nom = full[0]
                        prenom = " ".join(full[1:])

    return nom, prenom

# Traitement OCR pour une image
def ocr_image(pil_image):
    image_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    texte = pytesseract.image_to_string(gray, lang='fra+eng')
    return texte

# Traitement PDF → images
def convert_pdf_to_images(pdf_file):
    with tempfile.TemporaryDirectory() as path:
        images = pdf2image.convert_from_bytes(pdf_file.read(), dpi=200, output_folder=path)
    return images

# Interface d'import
uploaded_files = st.file_uploader("📤 Importer un ou plusieurs fichiers (image ou PDF)", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)

if uploaded_files:
    for fichier in uploaded_files:
        st.divider()
        st.subheader(f"📄 Fichier : {fichier.name}")

        # PDF
        if fichier.type == "application/pdf":
            images = convert_pdf_to_images(fichier)
        else:
            images = [Image.open(fichier)]

        # OCR
        full_text = ""
        for img in images:
            texte = ocr_image(img)
            full_text += texte + "\n"

        # Détection
        type_doc = detecter_type_document(full_text)
        nom, prenom = extraire_identite(type_doc, full_text)

        st.markdown(f"**📘 Type détecté :** `{type_doc}`")
        if nom or prenom:
            st.markdown(f"**👤 Nom détecté :** `{nom}`")
            st.markdown(f"**👤 Prénom détecté :** `{prenom}`")
        with st.expander("📝 Texte OCR brut"):
            st.text(full_text)



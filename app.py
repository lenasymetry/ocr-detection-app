import streamlit as st
import pytesseract
from PIL import Image
import cv2
import numpy as np

# ------------------------
# Affichage du logo (centre + responsive)
# ------------------------
logo = Image.open("mon_logo.png")
st.image(logo, width=150)


# ------------------------
# Titre de l'app
# ------------------------
st.title("🧾 Détection du type de document par OCR")
st.write("Importe une image pour détecter s’il s’agit d’un passeport, carte d’identité, titre de séjour, etc.")

# ------------------------
# Liste de mots-clés par type de document
# ------------------------
types_documents = {
    "Carte d'identité": ["RÉPUBLIQUE", "FRANÇAISE", "CARD", "NATIONALE", "NATIONALITÉ"],
    "Passeport": ["PASSPORT", "NUMÉRO", "AUTORITÉ", "DATE DE NAISSANCE", "SIGNATURE"],
    "Titre de séjour": ["SÉJOUR", "TITRE", "RESIDENCE", "PERMIT"],
    "Carte Vitale": ["ASSURANCE", "MALADIE", "CARTE", "VITALE"],
}

# ------------------------
# Fonction principale de détection
# ------------------------
def reconnaitre_document(image):
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gris = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    texte = pytesseract.image_to_string(gris)

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
# Interface d'import d'image
# ------------------------
uploaded_file = st.file_uploader(
    "Choisir un fichier image",
    type=["png", "jpg", "jpeg", "tiff", "bmp"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Image importée", width=600)

    texte, mots, type_doc = reconnaitre_document(image)

    st.subheader("🔎 Résultat")
    st.markdown(f"**Type de document détecté :** {type_doc}")
    st.markdown(f"**Mots-clés trouvés :** {', '.join(mots)}")

    with st.expander("📝 Texte OCR brut"):
        st.text(texte)

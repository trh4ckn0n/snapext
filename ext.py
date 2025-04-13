import pytesseract
import cv2
import os
import numpy as np
import re
from PIL import Image

# Fonction pour prétraiter l'image (contrast, binarisation, inversion)
def preprocess_image(image_path):
    img = cv2.imread(image_path)

    # Convertir en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Augmenter contraste et netteté
    alpha, beta = 2.0, 10  # Contraste + Luminosité
    contrast = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # Appliquer un seuillage adaptatif pour une meilleure séparation texte/fond
    adaptive_thresh = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)

    # Vérifier si le texte est blanc sur fond noir et inverser si nécessaire
    if np.mean(adaptive_thresh) > 127:
        adaptive_thresh = cv2.bitwise_not(adaptive_thresh)

    return Image.fromarray(adaptive_thresh)

# OCR avec des paramètres optimisés pour Tesseract
def ocr_with_tesseract(image):
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@"'
    return pytesseract.image_to_string(image, config=custom_config)

# Extraction des noms et usernames avec regex
def extract_names_and_usernames(text):
    members = []

    # Regex améliorée pour capter les noms + usernames
    pattern = r"([A-Za-zÀ-ÿ\-']{2,}(?:\s[A-Za-zÀ-ÿ\-']{2,})*):?\s*(@?[A-Za-z0-9_]+)"
    matches = re.findall(pattern, text)

    for match in matches:
        name, username = match
        members.append({'name': name.strip(), 'username': username.strip()})

    return members

# Parcours des images et extraction avancée
def process_images_in_directory(directory_path, output_file):
    all_members = []
    with open(output_file, "w", encoding="utf-8") as file:
        for filename in os.listdir(directory_path):
            if filename.lower().endswith((".jpg", ".png", ".jpeg")):
                image_path = os.path.join(directory_path, filename)

                # Prétraitement
                preprocessed_image = preprocess_image(image_path)

                # Extraction OCR
                extracted_text = ocr_with_tesseract(preprocessed_image)

                # Extraction des noms et usernames
                members = extract_names_and_usernames(extracted_text)
                all_members.extend(members)

                # Enregistrement des résultats
                file.write(f"--- {filename} ---\n")
                for member in members:
                    file.write(f"Nom : {member['name']}, Identifiant : {member['username']}\n")
                file.write("\n")

    return all_members

# Exemple d'utilisation
directory_path = "screen"  # Répertoire contenant les images
output_file = "results.txt"  # Fichier de sortie
members = process_images_in_directory(directory_path, output_file)

print("Extraction terminée. Résultats enregistrés dans results.txt.")

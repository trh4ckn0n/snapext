import pytesseract
from openai import OpenAI

client = OpenAI(api_key="sk-******")  # Corrected import for OpenAI
import cv2
import re
import os
from PIL import Image

# Initialisation du client OpenAI avec la clé API

# Fonction pour prétraiter l'image
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
    return Image.fromarray(thresh)

# OCR avec Tesseract
def ocr_with_tesseract(image):
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, config=custom_config)

# Fonction de validation avec GPT-4
def validate_with_gpt4(extracted_text):
    response = client.chat.completions.create(# Corrected function name
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Vous êtes un assistant très précis et vous aidez au mieux à trouver les noms et usernames de comptes Snapchat présents dans le texte extrait par OCR des captures d'écran d'un groupe Snapchat."},
            {"role": "user", "content": f"Vérifiez les informations extraites suivantes : {extracted_text}"}
        ])
    return response.choices[0].message.content  # Corrected response parsing

# Extraction des membres (noms et utilisateurs) via regex
def extract_members(text):
    members = []
    # Regex pour trouver des noms et des usernames sous un format courant
    pattern = r"([A-Za-zÀ-ÿ0-9]+(?: [A-Za-zÀ-ÿ0-9]+)*):?(@?[A-Za-z0-9_]+)"
    matches = re.findall(pattern, text)
    for match in matches:
        name, username = match
        members.append({'name': name, 'username': username})
    return members

# Parcours des images dans un répertoire
def process_images_in_directory(directory_path, output_file):
    all_members = []
    with open(output_file, "w") as file:  # Ouvrir le fichier en mode écriture
        for filename in os.listdir(directory_path):
            if filename.endswith(".jpg") or filename.endswith(".png"):  # Ajouter d'autres formats si nécessaire
                image_path = os.path.join(directory_path, filename)
                preprocessed_image = preprocess_image(image_path)
                extracted_text = ocr_with_tesseract(preprocessed_image)  # Extraire le texte de l'image
                # Extraire les membres du texte extrait
                members = extract_members(extracted_text)
                all_members.extend(members)
                # Vérification supplémentaire avec GPT-4 si nécessaire
                for member in members:
                    validated_info = validate_with_gpt4(f"Nom : {member['name']}, Identifiant : {member['username']}")
                    # Écrire les informations dans le fichier
                    file.write(f"Membre : {member['name']}, Identifiant : {member['username']}\n")
                    file.write(f"Validation GPT-4 pour {member['name']} ({member['username']}): {validated_info}\n\n")
    return all_members

# Exemple d'utilisation
directory_path = "screen"  # Spécifier le chemin du répertoire contenant les images
output_file = "results.txt"  # Fichier de sortie pour les résultats
members = process_images_in_directory(directory_path, output_file)

# Affichage des résultats
for member in members:
    print(f"Membre : {member['name']}, Identifiant : {member['username']}")

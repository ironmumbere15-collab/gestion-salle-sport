"""
Module d'envoi WhatsApp pour 365 GYM & FITNESS
Envoie automatiquement le lien de profil aux clients via WhatsApp
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration WhatsApp (Twilio ou autre service)
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "https://api.twilio.com/2010-04-01/Accounts")
WHATSAPP_ACCOUNT_SID = os.getenv("WHATSAPP_ACCOUNT_SID", "")
WHATSAPP_AUTH_TOKEN = os.getenv("WHATSAPP_AUTH_TOKEN", "")
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM", "")  # Ex: +243XXXXXXXXX
APP_URL = os.getenv("APP_URL", "https://365gym.app")
GYM_NAME = "365 GYM & FITNESS"

def envoyer_lien_profil_whatsapp(whatsapp: str, nom_client: str) -> bool:
    """
    Envoie un message WhatsApp au client avec le lien d'accès à son profil
    
    Args:
        whatsapp: Numéro WhatsApp du client (format: 243XXXXXXXXX ou +243XXXXXXXXX)
        nom_client: Nom du client
    
    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Nettoyer et formater le numéro
        num_clean = "".join(filter(str.isdigit, str(whatsapp)))
        if num_clean.startswith("0"):
            num_clean = "243" + num_clean[1:]
        elif not num_clean.startswith("243"):
            num_clean = "243" + num_clean
        
        numero_whatsapp = f"+{num_clean}"
        
        # Générer le lien de profil
        lien_profil = f"{APP_URL}/profil?id={whatsapp}"
        
        # Message WhatsApp
        message = f"""Bonjour {nom_client}! 👋

🎉 Bienvenue à {GYM_NAME} 365 jours par an ! 💪

🔗 *ACCÉDEZ À VOTRE PROFIL:*
{lien_profil}

Depuis votre profil vous pouvez:
📊 Consulter votre abonnement
📱 Télécharger notre application
⏰ Gérer vos réservations
💬 Nous contacter

Votre transformation commence maintenant ! 🚀

À bientôt ! 💪"""
        
        # Configuration Twilio
        auth = (WHATSAPP_ACCOUNT_SID, WHATSAPP_AUTH_TOKEN)
        url = f"{WHATSAPP_API_URL}/{WHATSAPP_ACCOUNT_SID}/Messages.json"
        
        data = {
            "From": WHATSAPP_FROM,
            "To": numero_whatsapp,
            "Body": message
        }
        
        response = requests.post(url, data=data, auth=auth)
        
        if response.status_code == 201:
            print(f"✅ Message WhatsApp envoyé à {numero_whatsapp}")
            return True
        else:
            print(f"❌ Erreur WhatsApp: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi WhatsApp: {str(e)}")
        return False


def generer_lien_et_message(whatsapp: str, nom_client: str) -> dict:
    """
    Génère le lien et le message sans l'envoyer (utile pour affichage)
    
    Args:
        whatsapp: Numéro WhatsApp
        nom_client: Nom du client
    
    Returns:
        dict: Contient le lien et le message
    """
    # Nettoyer le numéro
    num_clean = "".join(filter(str.isdigit, str(whatsapp)))
    if num_clean.startswith("0"):
        num_clean = "243" + num_clean[1:]
    elif not num_clean.startswith("243"):
        num_clean = "243" + num_clean
    
    lien_profil = f"{APP_URL}/profil?id={whatsapp}"
    
    message = f"""Bonjour {nom_client}! 👋

🎉 Bienvenue à {GYM_NAME} 365 jours par an ! 💪

🔗 *ACCÉDEZ À VOTRE PROFIL:*
{lien_profil}

Depuis votre profil vous pouvez:
📊 Consulter votre abonnement
📱 Télécharger notre application
⏰ Gérer vos réservations
💬 Nous contacter

Votre transformation commence maintenant ! 🚀

À bientôt ! 💪"""
    
    return {
        "lien": lien_profil,
        "message": message,
        "numero_whatsapp": f"+{num_clean}"
    }

import paho.mqtt.client as mqtt
import json
import ssl
import os
import django
from datetime import date

# --- INITIALISATION DU MOTEUR DJANGO ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Employe
from payroll.models import PresenceManuelle
from attendance.models import PointageIoT  # 👈 CORRIGÉ : Le bon nom de ton modèle !

# --- CONFIGURATION HIVEMQ ---
BROKER = "c69c5ab4c09848f88fe18d9374121871.s1.eu.hivemq.cloud"
PORT = 8883

# Tes identifiants Wokwi
USER = "davincii5"
PASS = "Davincii123456"
TOPIC = "sirh/attendance"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("📡 Connecté au broker HiveMQ avec succès ! (Code 0)")
        client.subscribe(TOPIC)
        print("⏳ En attente des badges RFID depuis Wokwi...")
    else:
        print(f"❌ Échec de connexion (Code {rc}). Vérifie ton USER et ton PASS !")

def on_message(client, userdata, msg):
    try:
        # On lit le JSON envoyé par Wokwi
        payload = msg.payload.decode().strip()
        data = json.loads(payload)
        
        matricule_recu = data.get("matricule", "")
        type_pointage = data.get("type_pointage", "ENTREE")
        id_capteur_recu = data.get("id_capteur", "ESP32_INCONNU") # 👈 NOUVEAU : On gère le capteur

        print(f"\n🔔 Badge scanné : {matricule_recu} ({type_pointage})")

        # On cherche l'employé
        employe = Employe.objects.get(matricule=matricule_recu)

        # 1. On crée la bulle verte pour la RH
        PresenceManuelle.objects.update_or_create(
            employe=employe,
            date_jour=date.today(),
            defaults={'statut': 'PRESENT'}
        )
        print(f"✅ {employe.username} marqué PRÉSENT dans la grille RH.")

        # 2. On crée l'historique Live pour le Dashboard IoT
        PointageIoT.objects.create(  # 👈 CORRIGÉ : On utilise le bon modèle
            employe=employe,
            type_pointage=type_pointage,
            id_capteur=id_capteur_recu,
            est_justifie=False
        )
        print(f"✅ Pointage ajouté dans le flux Live !")

    except Employe.DoesNotExist:
        print(f"❌ Erreur : Aucun employé avec le matricule '{matricule_recu}'")
    except json.JSONDecodeError:
        print(f"⚠️ Erreur : Ce n'est pas un JSON valide -> {payload}")
    except Exception as e:
        print(f"⚠️ Erreur système : {e}")

client = mqtt.Client()
client.username_pw_set(USER, PASS)
client.tls_set(tls_version=ssl.PROTOCOL_TLS)

client.on_connect = on_connect
client.on_message = on_message

print("🚀 Démarrage du pont MQTT...")
client.connect(BROKER, PORT, 60)
client.loop_forever()
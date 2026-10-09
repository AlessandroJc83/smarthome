# Activer les vraies notifications push sur téléphone

Le code de l'application est préparé. Il reste à créer les clés et à rendre le site accessible en HTTPS.

## A. Installation (une seule fois)
Dans le terminal VS Code, depuis le dossier du projet :
```powershell
python -m pip install -r requirements.txt
python generer_cles_vapid.py
```
Conserve `vapid_private.pem` secret. Ne le publie pas sur GitHub.

## B. Démarrer le serveur
Le serveur lit automatiquement `vapid_private.pem` et `vapid_public_key.txt` :
```powershell
$env:VAPID_SUBJECT="mailto:ton-adresse@example.com"
$env:FLASK_SECRET_KEY="remplace-par-une-longue-cle-aleatoire"
python app.py
```

## C. Pour recevoir les alertes sur le téléphone
Le site doit être ouvert sur une URL publique en HTTPS. `http://127.0.0.1:5000` sur le PC n'est pas accessible depuis le téléphone et ne permet pas le Push Web sur téléphone. Il faut héberger le projet sur un service qui prend en charge Flask + HTTPS (ou utiliser un tunnel HTTPS pour un test ponctuel).
1. Ouvre l'URL HTTPS depuis le téléphone.
2. Clique sur « Activer les notifications téléphone » et autorise les notifications.
3. Clique sur « Simuler une intrusion » depuis l'application. Une notification push doit arriver.

Le navigateur et le système du téléphone doivent autoriser les notifications. Sur iPhone, la prise en charge dépend notamment de Safari et de l'installation du site sur l'écran d'accueil.

## Alertes configurées
- Intrusion simulée
- Fumée/incendie simulé
- Fuite d'eau simulée
- Mode absence activé
- Température sous 18 °C

Ce projet est une simulation logicielle, pas un système de sécurité réel.

import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

private = ec.generate_private_key(ec.SECP256R1())
private_pem = private.private_bytes(Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
public_raw = private.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
with open("vapid_private.pem", "wb") as f:
    f.write(private_pem)
with open("vapid_public_key.txt", "w", encoding="utf-8") as f:
    f.write(b64url(public_raw))
print("Clés créées : vapid_private.pem et vapid_public_key.txt")
print("Ne partage JAMAIS vapid_private.pem. Garde les deux fichiers dans le dossier du projet.")

import os, json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from pywebpush import webpush, WebPushException

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cle-temporaire-a-remplacer")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_KEY_FILE = os.path.join(BASE_DIR, "vapid_public_key.txt")
PRIVATE_KEY_FILE = os.path.join(BASE_DIR, "vapid_private.pem")
VAPID_PUBLIC_KEY = open(PUBLIC_KEY_FILE, encoding="utf-8").read().strip() if os.path.exists(PUBLIC_KEY_FILE) else ""
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:admin@example.com")
SUBSCRIPTIONS_FILE = os.path.join(BASE_DIR, "push_subscriptions.json")

state = {
 "temperature":20,"heating":False,"heating_auto":True,
 "lights":{"Salon":False,"Cuisine":False,"Chambre":False,"Garage":False},
 "shutters":{"Salon":"ouvert","Chambre":"ouvert"},
 "alarm":False,"intrusion":False,"absence":False,"smoke":False,"water_leak":False,"events":[]
}
def log(msg,kind="info"):
 state["events"].insert(0,{"time":datetime.now().strftime("%H:%M:%S"),"message":msg,"kind":kind})
 del state["events"][50:]
def heat():
 if state["heating_auto"]:
  if state["temperature"]<18: state["heating"]=True
  elif state["temperature"]>21: state["heating"]=False
def load_subscriptions():
 try:
  with open(SUBSCRIPTIONS_FILE,encoding="utf-8") as f:return json.load(f)
 except (FileNotFoundError,json.JSONDecodeError):return []
def save_subscriptions(items):
 with open(SUBSCRIPTIONS_FILE,"w",encoding="utf-8") as f:json.dump(items,f,ensure_ascii=False,indent=2)
def send_push(title,body):
 if not VAPID_PUBLIC_KEY or not os.path.exists(PRIVATE_KEY_FILE):
  app.logger.warning("Push non configuré : clés VAPID manquantes")
  return
 subs=load_subscriptions(); valid=[]
 for sub in subs:
  try:
   webpush(subscription_info=sub,data=json.dumps({"title":title,"body":body}),vapid_private_key=PRIVATE_KEY_FILE,vapid_claims={"sub":VAPID_SUBJECT})
   valid.append(sub)
  except WebPushException as exc:
   status=getattr(getattr(exc,"response",None),"status_code",None)
   if status not in (404,410):
    valid.append(sub); app.logger.warning("Envoi push impossible: %s",exc)
  except Exception:
   valid.append(sub); app.logger.exception("Erreur push")
 save_subscriptions(valid)
@app.route("/")
def home(): return render_template("index.html",vapid_public_key=VAPID_PUBLIC_KEY)
@app.route("/service-worker.js")
def sw(): return send_from_directory(os.path.join(BASE_DIR,"static"),"service-worker.js",mimetype="application/javascript")
@app.route("/api/state")
def get_state(): return jsonify(state)
@app.route("/api/subscribe",methods=["POST"])
def subscribe():
 sub=request.get_json(silent=True)
 if not isinstance(sub,dict) or "endpoint" not in sub or "keys" not in sub:return jsonify(error="Abonnement invalide"),400
 items=load_subscriptions()
 if not any(x.get("endpoint")==sub["endpoint"] for x in items):items.append(sub);save_subscriptions(items)
 return jsonify(ok=True)
@app.route("/api/action",methods=["POST"])
def action():
 d=request.get_json(silent=True) or {}; a=d.get("action"); n=d.get("name"); msg=""; kind="info"; push=None
 if a=="temperature":
  try:state["temperature"]=max(5,min(35,int(d["value"])))
  except (ValueError,TypeError,KeyError):return jsonify(error="Température invalide"),400
  heat();msg=f"Température réglée à {state['temperature']} °C"
  if state["temperature"]<18:push=("SmartHome : température basse",f"La maison est à {state['temperature']} °C.")
 elif a=="toggle_light" and n in state["lights"]:
  state["lights"][n]=not state["lights"][n];msg=f"Lumière {n} {'allumée' if state['lights'][n] else 'éteinte'}"
 elif a=="toggle_heating":state["heating"]=not state["heating"];msg="Chauffage modifié"
 elif a=="toggle_heating_auto":state["heating_auto"]=not state["heating_auto"];heat();msg="Mode automatique du chauffage modifié"
 elif a=="toggle_shutter" and n in state["shutters"]:
  state["shutters"][n]="fermé" if state["shutters"][n]=="ouvert" else "ouvert";msg=f"Volet {n} {state['shutters'][n]}"
 elif a=="toggle_alarm":state["alarm"]=not state["alarm"];msg="Alarme "+("activée" if state["alarm"] else "désactivée")
 elif a=="intrusion":state["intrusion"]=True;msg="Intrusion simulée détectée !";kind="alert";push=("SmartHome : intrusion détectée","Une intrusion simulée a été détectée.")
 elif a=="reset_alarm":state["intrusion"]=False;msg="Alarme réinitialisée"
 elif a=="toggle_smoke":
  state["smoke"]=not state["smoke"];msg="Alerte fumée/incendie simulée" if state["smoke"] else "Alerte fumée réinitialisée";kind="alert" if state["smoke"] else "info"
  if state["smoke"]:push=("SmartHome : alerte fumée","Une alerte fumée/incendie a été simulée.")
 elif a=="toggle_water":
  state["water_leak"]=not state["water_leak"];msg="Fuite d'eau simulée détectée" if state["water_leak"] else "Alerte fuite d'eau réinitialisée";kind="alert" if state["water_leak"] else "info"
  if state["water_leak"]:push=("SmartHome : fuite d'eau","Une fuite d'eau simulée a été détectée.")
 elif a=="toggle_absence":
  state["absence"]=not state["absence"]
  if state["absence"]:
   for r in state["lights"]:state["lights"][r]=False
   for r in state["shutters"]:state["shutters"][r]="fermé"
   state["temperature"]=17;state["alarm"]=True;heat();msg="Mode absence activé";push=("SmartHome : mode absence","Le mode absence a été activé.")
  else:msg="Mode absence désactivé"
 elif a=="reset_all":
  state.update({"temperature":20,"heating":False,"heating_auto":True,"lights":{"Salon":False,"Cuisine":False,"Chambre":False,"Garage":False},"shutters":{"Salon":"ouvert","Chambre":"ouvert"},"alarm":False,"intrusion":False,"absence":False,"smoke":False,"water_leak":False});msg="Tous les appareils réinitialisés"
 else:return jsonify(error="Action inconnue"),400
 log(msg,kind)
 if push:send_push(*push)
 return jsonify(state)
if __name__=="__main__":app.run(debug=True)

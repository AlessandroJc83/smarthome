let S=null, selected="Salon";
async function act(action,extra={}){try{let r=await fetch("/api/action",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action,...extra})});let d=await r.json();if(!r.ok)throw Error(d.error);render(d)}catch(e){alert("Erreur de communication avec le serveur : "+e.message)}}
async function load(){try{let r=await fetch("/api/state");render(await r.json())}catch(e){console.error(e)}}
function esc(x){return String(x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function render(s){S=s;document.querySelector("#temp").textContent=s.temperature;document.querySelector("#heat").textContent=s.heating?"ON":"OFF";document.querySelector("#auto").textContent=s.heating_auto?"ON":"OFF";document.querySelector("#alarm").textContent=s.alarm?"ACTIVÉE":"DÉSACTIVÉE";
let a=[];if(s.intrusion)a.push("🚨 INTRUSION DÉTECTÉE");if(s.smoke)a.push("🔥 FUMÉE / INCENDIE");if(s.water_leak)a.push("💧 FUITE D'EAU");let al=document.querySelector("#alerts");al.textContent=a.join(" · ");al.classList.toggle("hidden",!a.length);
document.querySelector("#absence").textContent=s.absence?"Désactiver le mode absence":"Activer le mode absence";document.querySelector("#absenceText").textContent=s.absence?"Mode absence activé":"Mode absence désactivé";
Object.entries(s.lights).forEach(([n,on])=>{let e=document.querySelector("#light-"+n);if(e)e.textContent=on?"💡 Allumée":"💡 Éteinte";let b=document.querySelector(`[data-room="${n}"]`);if(b)b.style.background=on?"#fde68a":""});
Object.entries(s.shutters).forEach(([n,v])=>{let e=document.querySelector("#shutter-"+n);if(e)e.textContent="🪟 Volet "+v});
document.querySelector("#lights").innerHTML=Object.entries(s.lights).map(([n,v])=>`<div class="control"><div><b>${n}</b><small>${v?"Allumée":"Éteinte"}</small></div><button class="secondary" data-light="${n}">${v?"Éteindre":"Allumer"}</button></div>`).join("");
document.querySelector("#shutters").innerHTML=Object.entries(s.shutters).map(([n,v])=>`<div class="control"><div><b>${n}</b><small>${v}</small></div><button class="secondary" data-shutter="${n}">${v==="ouvert"?"Fermer":"Ouvrir"}</button></div>`).join("");
document.querySelectorAll("[data-light]").forEach(b=>b.onclick=()=>act("toggle_light",{name:b.dataset.light}));document.querySelectorAll("[data-shutter]").forEach(b=>b.onclick=()=>act("toggle_shutter",{name:b.dataset.shutter}));
document.querySelectorAll(".room[data-room]").forEach(b=>b.classList.toggle("selected",b.dataset.room===selected));document.querySelector("#selectedTitle").textContent="Commandes rapides — "+selected;
document.querySelector("#roomLight").disabled=!Object.hasOwn(s.lights,selected);document.querySelector("#roomShutter").disabled=!Object.hasOwn(s.shutters,selected);
document.querySelector("#roomLight").textContent=s.lights[selected]?"💡 Éteindre la lumière":"💡 Allumer la lumière";document.querySelector("#roomShutter").textContent=s.shutters[selected]==="fermé"?"🪟 Ouvrir le volet":"🪟 Fermer le volet";
document.querySelector("#events").innerHTML=s.events.length?s.events.map(e=>`<div class="event ${e.kind}"><time>${e.time}</time>${esc(e.message)}</div>`).join(""):"<p>Aucun événement pour le moment.</p>";
}
document.querySelectorAll(".room[data-room]").forEach(b=>b.onclick=()=>{selected=b.dataset.room;render(S)});document.querySelector("#roomLight").onclick=()=>act("toggle_light",{name:selected});document.querySelector("#roomShutter").onclick=()=>act("toggle_shutter",{name:selected});
document.querySelector("#down").onclick=()=>act("temperature",{value:S.temperature-1});document.querySelector("#up").onclick=()=>act("temperature",{value:S.temperature+1});document.querySelector("#heatBtn").onclick=()=>act("toggle_heating");document.querySelector("#autoBtn").onclick=()=>act("toggle_heating_auto");document.querySelector("#alarmBtn").onclick=()=>act("toggle_alarm");document.querySelector("#intrusion").onclick=()=>act("intrusion");document.querySelector("#resetAlarm").onclick=()=>act("reset_alarm");document.querySelector("#smoke").onclick=()=>act("toggle_smoke");document.querySelector("#water").onclick=()=>act("toggle_water");document.querySelector("#absence").onclick=()=>act("toggle_absence");document.querySelector("#reset").onclick=()=>{if(confirm("Réinitialiser tous les appareils ?"))act("reset_all")};
function base64ToBytes(key){const pad="=".repeat((4-key.length%4)%4);const raw=atob((key+pad).replace(/-/g,"+").replace(/_/g,"/"));return Uint8Array.from([...raw].map(c=>c.charCodeAt(0)))}
document.querySelector("#notify").onclick=async()=>{try{
 if(!("serviceWorker"in navigator)||!("PushManager"in window)||!("Notification"in window)){alert("Ce navigateur ne prend pas en charge les notifications push.");return}
 const key=window.SMART_HOME_VAPID_PUBLIC_KEY;if(!key){alert("Clés VAPID absentes. Suis les étapes du README.");return}
 if(await Notification.requestPermission()!=="granted"){alert("Autorisation refusée dans les paramètres du navigateur.");return}
 const reg=await navigator.serviceWorker.register("/service-worker.js");
 let sub=await reg.pushManager.getSubscription();if(!sub)sub=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:base64ToBytes(key)});
 const res=await fetch("/api/subscribe",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(sub)});if(!res.ok)throw Error("Abonnement refusé par le serveur");
 document.querySelector("#notify").textContent="✅ Notifications push activées";alert("Appareil inscrit ! Teste ensuite « Simuler une intrusion ».");
 }catch(e){alert("Activation impossible : "+e.message+"\\nVérifie que le site est en HTTPS et que les clés VAPID sont configurées.")}};

load();

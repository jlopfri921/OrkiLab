/* Opt-in local AI viewpoint hint: never writes geometry or saves without a second click. */
(function(){
"use strict";
const strings={
 es:{title:"Detectar punto de vista (IA local)",intro:"Clasificación orientativa: no es una medición de azimut ni una posición 3D. La referencia frontal debe decidirla una persona.",model:"Modelo de visión Ollama",find:"Cargar modelos locales",run:"Analizar esta foto",save:"Confirmar y guardar orientación",direction:"Orientación sugerida (editable)",elevation:"Altura de cámara sugerida",distance:"Distancia aparente",confidence:"Confianza declarada por el modelo",unknown:"Desconocida",none:"No hay modelos locales de visión disponibles. Instala y configura un modelo multimodal en Ollama; no se descargará automáticamente.",ready:"Elige un modelo de visión local y pulsa Analizar.",running:"Analizando en Ollama local…",review:"Revisa y corrige la orientación antes de confirmar. No se guardan grados numéricos ni se cambia la revisión de la foto.",done:"Orientación cualitativa guardada como estimación. Ningún ángulo numérico se ha añadido.",confirm:"¿Guardar esta etiqueta como estimación de IA? No se alterarán los grados ni la imagen original.",error:"No ha sido posible analizar la fotografía.",front:"Frontal",front_right:"Frontal derecha",right:"Derecha",back_right:"Trasera derecha",back:"Trasera",back_left:"Trasera izquierda",left:"Izquierda",front_left:"Frontal izquierda",top:"Superior",bottom:"Inferior",above:"Desde arriba",level:"A su altura",below:"Desde abajo",close:"Cerca",medium:"Media",far:"Lejos",low:"Baja",high:"Alta"},
 en:{title:"Detect viewpoint (local AI)",intro:"Qualitative guess, NOT measured azimuth or 3D camera position. A human must define what counts as front.",model:"Ollama vision model",find:"Load local models",run:"Analyze this photo",save:"Confirm and save orientation",direction:"Suggested view (editable)",elevation:"Suggested camera height",distance:"Apparent distance",confidence:"Model-stated confidence",unknown:"Unknown",none:"No local vision models found. Install/configure a multimodal Ollama model; nothing is downloaded automatically.",ready:"Choose a local vision model, then click Analyze.",running:"Analyzing with local Ollama…",review:"Review and correct the view before confirming. No numeric angles are saved and photo review stays unchanged.",done:"Qualitative orientation saved as an estimate. No numeric camera angle was added.",confirm:"Save this label as an AI estimate? Numeric degrees and original photos will not change.",error:"Could not analyze the photograph.",front:"Front",front_right:"Front right",right:"Right",back_right:"Back right",back:"Back",back_left:"Back left",left:"Left",front_left:"Front left",top:"Top",bottom:"Bottom",above:"Above",level:"Level",below:"Below",close:"Close",medium:"Medium",far:"Far",low:"Low",high:"High"},
 pt:{title:"Detetar ponto de vista (IA local)",intro:"Estimativa qualitativa, não um azimute medido nem uma posição 3D. Defina manualmente a orientação frontal.",model:"Modelo de visão Ollama",find:"Carregar modelos locais",run:"Analisar esta foto",save:"Confirmar e guardar orientação",direction:"Vista sugerida (editável)",elevation:"Altura da câmara sugerida",distance:"Distância aparente",confidence:"Confiança indicada pelo modelo",unknown:"Desconhecida",none:"Não existem modelos de visão locais. Instale um modelo multimodal no Ollama; nada será descarregado automaticamente.",ready:"Escolha um modelo de visão local e clique em Analisar.",running:"A analisar com Ollama local…",review:"Revise e corrija a vista antes de confirmar. Não são guardados ângulos numéricos nem alterada a revisão da foto.",done:"Orientação qualitativa guardada como estimativa. Não foram adicionados ângulos numéricos.",confirm:"Guardar esta etiqueta como estimativa de IA? Os graus numéricos e as fotos originais não serão alterados.",error:"Não foi possível analisar a fotografia.",front:"Frontal",front_right:"Frontal direita",right:"Direita",back_right:"Traseira direita",back:"Traseira",back_left:"Traseira esquerda",left:"Esquerda",front_left:"Frontal esquerda",top:"Superior",bottom:"Inferior",above:"De cima",level:"Ao nível",below:"De baixo",close:"Perto",medium:"Média",far:"Longe",low:"Baixa",high:"Alta"},
 fr:{title:"Détecter le point de vue (IA locale)",intro:"Estimation qualitative, pas un azimut mesuré ni une position 3D. Définissez manuellement la face avant.",model:"Modèle de vision Ollama",find:"Charger les modèles locaux",run:"Analyser cette photo",save:"Confirmer et enregistrer l'orientation",direction:"Vue suggérée (modifiable)",elevation:"Hauteur de caméra suggérée",distance:"Distance apparente",confidence:"Confiance annoncée par le modèle",unknown:"Inconnue",none:"Aucun modèle de vision local. Installez un modèle multimodal dans Ollama ; aucun téléchargement automatique.",ready:"Choisissez un modèle de vision local, puis cliquez sur Analyser.",running:"Analyse par Ollama local…",review:"Vérifiez et corrigez la vue avant confirmation. Aucun angle numérique n'est enregistré et la validation de la photo reste inchangée.",done:"Orientation qualitative enregistrée comme estimation. Aucun angle numérique ajouté.",confirm:"Enregistrer cette étiquette comme estimation de l'IA ? Les degrés et les photos originales ne changeront pas.",error:"Impossible d'analyser la photographie.",front:"Face",front_right:"Avant droite",right:"Droite",back_right:"Arrière droite",back:"Arrière",back_left:"Arrière gauche",left:"Gauche",front_left:"Avant gauche",top:"Dessus",bottom:"Dessous",above:"D'en haut",level:"À hauteur",below:"D'en bas",close:"Proche",medium:"Moyenne",far:"Loin",low:"Faible",high:"Élevée"},
 de:{title:"Blickwinkel erkennen (lokale KI)",intro:"Qualitative Schätzung, kein gemessener Azimut oder 3D-Kamerastandort. Die Vorderseite muss manuell festgelegt werden.",model:"Ollama-Visionmodell",find:"Lokale Modelle laden",run:"Dieses Foto analysieren",save:"Ausrichtung bestätigen und speichern",direction:"Vorgeschlagene Ansicht (bearbeitbar)",elevation:"Geschätzte Kamerahöhe",distance:"Scheinbare Entfernung",confidence:"Vom Modell angegebene Sicherheit",unknown:"Unbekannt",none:"Keine lokalen Visionmodelle vorhanden. Installieren Sie ein multimodales Ollama-Modell; kein automatischer Download.",ready:"Wählen Sie ein lokales Visionmodell und klicken Sie auf Analysieren.",running:"Analyse mit lokalem Ollama…",review:"Prüfen und korrigieren Sie die Ansicht vor dem Speichern. Es werden keine Winkel in Grad gespeichert oder Fotoprüfungen geändert.",done:"Qualitative Ausrichtung als Schätzung gespeichert. Keine numerischen Winkel hinzugefügt.",confirm:"Diese Bezeichnung als KI-Schätzung speichern? Gradangaben und Originalfotos bleiben unverändert.",error:"Foto konnte nicht analysiert werden.",front:"Vorne",front_right:"Vorne rechts",right:"Rechts",back_right:"Hinten rechts",back:"Hinten",back_left:"Hinten links",left:"Links",front_left:"Vorne links",top:"Oben",bottom:"Unten",above:"Von oben",level:"Auf gleicher Höhe",below:"Von unten",close:"Nah",medium:"Mittel",far:"Fern",low:"Niedrig",high:"Hoch"},
 it:{title:"Rileva punto di vista (IA locale)",intro:"Stima qualitativa, non un azimut misurato né una posizione 3D. La vista frontale va definita manualmente.",model:"Modello visivo Ollama",find:"Carica modelli locali",run:"Analizza questa foto",save:"Conferma e salva orientamento",direction:"Vista suggerita (modificabile)",elevation:"Altezza camera suggerita",distance:"Distanza apparente",confidence:"Affidabilità dichiarata dal modello",unknown:"Sconosciuta",none:"Nessun modello visivo locale disponibile. Installa un modello multimodale in Ollama; nessun download automatico.",ready:"Scegli un modello visivo locale e premi Analizza.",running:"Analisi con Ollama locale…",review:"Controlla e correggi la vista prima di confermare. Nessun angolo numerico viene salvato e la revisione della foto non cambia.",done:"Orientamento qualitativo salvato come stima. Nessun angolo numerico aggiunto.",confirm:"Salvare questa etichetta come stima IA? Gradi numerici e foto originali non cambieranno.",error:"Impossibile analizzare la fotografia.",front:"Frontale",front_right:"Anteriore destra",right:"Destra",back_right:"Posteriore destra",back:"Posteriore",back_left:"Posteriore sinistra",left:"Sinistra",front_left:"Anteriore sinistra",top:"Superiore",bottom:"Inferiore",above:"Dall'alto",level:"All'altezza",below:"Dal basso",close:"Vicino",medium:"Media",far:"Lontano",low:"Bassa",high:"Alta"},
 ja:{title:"視点を検出（ローカルAI）",intro:"定性的な推定です。測定した方位角や3Dカメラ位置ではありません。正面は手動で決めてください。",model:"Ollama画像認識モデル",find:"ローカルモデルを読み込む",run:"この写真を分析",save:"方向を確認して保存",direction:"推定視点（編集可能）",elevation:"推定カメラ高さ",distance:"見かけの距離",confidence:"モデルの信頼度",unknown:"不明",none:"ローカル画像認識モデルがありません。Ollamaにマルチモーダルモデルを導入してください。自動ダウンロードはしません。",ready:"ローカル画像認識モデルを選び、分析を押してください。",running:"ローカルOllamaで分析中…",review:"保存前に視点を確認・修正してください。数値の角度や写真のレビュー状態は変更しません。",done:"推定方向を保存しました。数値の角度は追加されていません。",confirm:"このラベルをAI推定として保存しますか？角度の数値と元の写真は変更しません。",error:"写真を分析できませんでした。",front:"正面",front_right:"右前",right:"右側",back_right:"右後",back:"背面",back_left:"左後",left:"左側",front_left:"左前",top:"上面",bottom:"下面",above:"上から",level:"同じ高さ",below:"下から",close:"近い",medium:"中程度",far:"遠い",low:"低い",high:"高い"},
 ko:{title:"시점 감지(로컬 AI)",intro:"정성적 추정으로, 측정된 방위각이나 3D 카메라 위치가 아닙니다. 정면 기준은 사용자가 정해야 합니다.",model:"Ollama 비전 모델",find:"로컬 모델 불러오기",run:"사진 분석",save:"방향 확인 후 저장",direction:"추천 시점(수정 가능)",elevation:"추천 카메라 높이",distance:"겉보기 거리",confidence:"모델이 제시한 신뢰도",unknown:"알 수 없음",none:"로컬 비전 모델이 없습니다. Ollama에 멀티모달 모델을 설치하세요. 자동 다운로드하지 않습니다.",ready:"로컬 비전 모델을 선택한 뒤 분석을 누르세요.",running:"로컬 Ollama로 분석 중…",review:"저장 전 시점을 확인하고 수정하세요. 수치 각도와 사진 검토 상태는 변경하지 않습니다.",done:"정성적 방향을 추정값으로 저장했습니다. 수치 각도는 추가되지 않았습니다.",confirm:"이 라벨을 AI 추정값으로 저장할까요? 각도 수치와 원본 사진은 변경되지 않습니다.",error:"사진을 분석할 수 없습니다.",front:"정면",front_right:"오른쪽 앞",right:"오른쪽",back_right:"오른쪽 뒤",back:"뒷면",back_left:"왼쪽 뒤",left:"왼쪽",front_left:"왼쪽 앞",top:"위쪽",bottom:"아래쪽",above:"위에서",level:"같은 높이",below:"아래에서",close:"가까움",medium:"중간",far:"멀리",low:"낮음",high:"높음"}
};
const directions=["front","front_right","right","back_right","back","back_left","left","front_left","top","bottom","unknown"];
function lang(){const locale=typeof I18N!=="undefined"?I18N.lang:"en";return strings[locale]?locale:"en"}
function tr(k){return strings[lang()][k]||k}
function el(tag,value){const n=document.createElement(tag);if(value!==undefined)n.textContent=value;return n}
function mount(host,getProject,captureId,api,afterSave,capture){
 const project=getProject();
 const box=el("section");box.className="mv-viewpoint-panel no-i18n";
 const title=el("h3",tr("title")),intro=el("p",tr("intro"));
 const modelLabel=el("label",tr("model")),model=el("select"),lookup=el("button",tr("find"));
 lookup.type="button";modelLabel.append(model);
 const analyze=el("button",tr("run"));analyze.type="button";analyze.disabled=true;
 const status=el("p",tr("ready"));status.className="muted";status.setAttribute("role","status");
 const result=el("div");result.hidden=true;
 const dirLabel=el("label",tr("direction")),direction=el("select");
 for(const key of directions)direction.add(new Option(tr(key),key));
 dirLabel.append(direction);
 const details=el("p");details.className="muted";
 const warning=el("p",tr("review"));const save=el("button",tr("save"));save.type="button";
 result.append(dirLabel,details,warning,save);
 box.append(title,intro,modelLabel,lookup,analyze,status,result);host.append(box);
 let busy=false,ready=false,verified=null;
 async function models(){
  if(busy)return;
  lookup.disabled=true;status.textContent=tr("running");
  try{
   const response=await api("/api/workspace/ollama/vision-models");
   model.replaceChildren(new Option(tr("model"),""));
   for(const m of response.models||[])model.add(new Option(m.name,m.name));
   analyze.disabled=!response.models?.length;
   status.textContent=response.models?.length?tr("ready"):tr("none");
  }catch(e){status.textContent=e.message||tr("none");analyze.disabled=true}
  finally{lookup.disabled=false}
 }
 analyze.onclick=async()=>{
  if(busy||!model.value||getProject()!==project)return;
  busy=true;analyze.disabled=true;save.disabled=true;result.hidden=true;verified=null;
  status.textContent=tr("running");
  try{
   const data=await api("/api/workspace/multiview/projects/"+encodeURIComponent(project)+
       "/captures/"+encodeURIComponent(captureId)+"/viewpoint/suggest",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({confirm:true,model:model.value})});
   if(getProject()!==project||!box.isConnected)return;
   if(!directions.includes(data.direction))throw Error("Invalid viewpoint suggestion");
   direction.value=data.direction;
   details.textContent=tr("elevation")+": "+tr(data.elevation||"unknown")+" · "+
     tr("distance")+": "+tr(data.distance||"unknown")+" · "+
     tr("confidence")+": "+tr(data.confidence||"low");
   verified={model:data.model};result.hidden=false;save.disabled=false;
   status.textContent=tr("review");
  }catch(e){status.textContent=(e.message||tr("error"));result.hidden=true}
  finally{busy=false;analyze.disabled=!model.value}
 };
 save.onclick=async()=>{
  if(!verified||busy||getProject()!==project)return;
  if(!window.confirm(tr("confirm")))return;
  busy=true;save.disabled=true;
  try{
   // Do not overwrite measured/manual/workflow camera provenance with an AI guess.
   const hasGeometry=capture.azimuth_deg!==null||capture.elevation_deg!==null||capture.distance_m!==null;
   const proposed={view_name:tr(direction.value)};
   if(!hasGeometry&&(capture.provenance==="unknown"||capture.provenance==="estimated")){
     proposed.provenance="estimated";
   }
   await api("/api/workspace/multiview/projects/"+encodeURIComponent(project)+
       "/captures/"+encodeURIComponent(captureId),{
        method:"PATCH",headers:{"Content-Type":"application/json"},
        body:JSON.stringify(proposed)});
   status.textContent=tr("done");verified=null;result.hidden=true;
   await afterSave();
  }catch(e){status.textContent=e.message||tr("error");save.disabled=false}
  finally{busy=false}
 };
 lookup.onclick=models;
 return {refreshModels:models};
}
window.OrkiViewpointAI={mount};
})();

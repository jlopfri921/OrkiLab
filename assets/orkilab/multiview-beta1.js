/* Opt-in Multiview Studio beta.1 — reuses validated OrkiLab generation API.
   No automatic runs, model downloads, arbitrary ComfyUI endpoints or invented angles.
   Generated outputs remain unreviewed until an explicit user action. */
(function(){
"use strict";
const translations={
 es:{title:"Generación asistida de perspectivas · ComfyUI",intro:"Selecciona un workflow de imagen que ya funcione con tu instalación. OrkiLab no garantiza una nueva perspectiva 3D: dependerá del modelo y del workflow. No descargamos modelos ni ejecutamos nada automáticamente.",workflow:"Workflow instalado",refresh:"Actualizar workflows",prepare:"Preparar y validar",prompt:"Texto o indicación de perspectiva",seed:"Semilla (opcional)",selectInput:"Campo de texto editable del workflow",selectSeed:"Campo de semilla editable",noInput:"No modificar texto",noSeed:"Conservar semilla",instruction:"Ejemplo: vista lateral derecha de la misma figura. Verifica que tu workflow admita imágenes de referencia.",run:"Generar ahora",cancel:"Cancelar trabajo",state:"Estado",queued:"En cola",running:"Generando",completed:"Terminado",cancelled:"Cancelado",error:"Error",unknown:"Estado desconocido",cancelling:"Cancelando",ready:"Workflow preparado. Revisa los campos y confirma antes de ejecutar.",notReady:"Prepara un workflow antes de generar.",needImage:"No hay un workflow de imagen guardado. Importa uno desde Zona ComfyUI → Workflows.",none:"No hay imágenes PNG/JPEG/WebP de salida para incorporar.",results:"Imágenes generadas",add:"Incorporar al sujeto",angle:"Azimut (°), si lo conoces",elevation:"Elevación (°), opcional",distance:"Distancia (m), opcional",view:"Nombre de vista",saved:"Imagen sintética incorporada para revisión. Los originales se mantienen.",lineage:"Procedencia: workflow, generación, semilla y salida guardadas en OrkiLab. No se altera la imagen original.",confirm:"¿Confirmas ejecutar este workflow en ComfyUI con los parámetros indicados?",importConfirm:"¿Incorporar esta salida como imagen sintética sin aprobar?",selectFirst:"Selecciona un workflow.",saveError:"No se pudo importar la imagen.",note:"Solo funciona desde el ordenador del lanzador; la interfaz móvil remota no puede ejecutar ni importar generaciones.",inspect:"Selecciona un campo de texto del workflow para modificarlo; si es necesario, configura referencias dentro de ComfyUI.",waiting:"ComfyUI está ejecutando el trabajo; estado actualizado automáticamente."},
 en:{title:"Assisted viewpoint generation · ComfyUI",intro:"Choose a saved image workflow that works in your ComfyUI installation. A new 3D viewpoint is not guaranteed: it depends on the model and workflow. No model downloads or automatic execution.",workflow:"Installed workflow",refresh:"Refresh workflows",prepare:"Prepare and validate",prompt:"Viewpoint prompt or instruction",seed:"Seed (optional)",selectInput:"Editable workflow text field",selectSeed:"Editable seed field",noInput:"Do not change text",noSeed:"Keep original seed",instruction:"Example: right-side view of the same sculpture. Make sure your workflow supports reference images.",run:"Generate now",cancel:"Cancel job",state:"Status",queued:"Queued",running:"Running",completed:"Completed",cancelled:"Cancelled",error:"Error",unknown:"Unknown status",cancelling:"Cancelling",ready:"Workflow prepared. Review fields and explicitly confirm execution.",notReady:"Prepare a workflow before generating.",needImage:"No saved image workflow. Import one from ComfyUI Zone → Workflows.",none:"No PNG/JPEG/WebP output images available to register.",results:"Generated images",add:"Register with subject",angle:"Azimuth (°), if known",elevation:"Elevation (°), optional",distance:"Distance (m), optional",view:"View name",saved:"Synthetic image registered for review; originals unchanged.",lineage:"Lineage: workflow, generation, seed and output stored by OrkiLab. Source files unchanged.",confirm:"Execute this workflow in ComfyUI with the selected parameters?",importConfirm:"Register this output as unreviewed synthetic image?",selectFirst:"Select a workflow.",saveError:"Image could not be imported.",note:"Runs only from the launcher computer. Remote phones cannot launch or import generations.",inspect:"Choose an editable workflow text input for the prompt; configure references in ComfyUI if required.",waiting:"ComfyUI is processing; status updates automatically."},
 pt:{title:"Geração assistida de perspetivas · ComfyUI",intro:"Escolha um workflow de imagem já validado. Uma nova perspetiva 3D não é garantida; depende do modelo. Sem downloads nem execução automática.",workflow:"Workflow instalado",refresh:"Atualizar workflows",prepare:"Preparar e validar",prompt:"Indicação de perspetiva",seed:"Semente (opcional)",selectInput:"Campo de texto editável",selectSeed:"Campo de semente",noInput:"Manter texto",noSeed:"Manter semente",instruction:"Exemplo: vista lateral da mesma figura. Confirme que o workflow aceita referências.",run:"Gerar agora",cancel:"Cancelar",state:"Estado",queued:"Na fila",running:"A gerar",completed:"Concluído",cancelled:"Cancelado",error:"Erro",unknown:"Desconhecido",cancelling:"A cancelar",ready:"Workflow preparado. Confirme a execução.",notReady:"Prepare um workflow.",needImage:"Importe um workflow de imagem na Zona ComfyUI.",none:"Sem imagens de saída compatíveis.",results:"Imagens geradas",add:"Associar ao sujeito",angle:"Azimute (°)",elevation:"Elevação (°)",distance:"Distância (m)",view:"Nome da vista",saved:"Imagem sintética adicionada para revisão.",lineage:"Workflow, geração e semente guardados; originais intactos.",confirm:"Executar o workflow no ComfyUI?",importConfirm:"Importar como sintética não aprovada?",selectFirst:"Escolha um workflow.",saveError:"Falha ao importar.",note:"A execução funciona apenas no computador principal.",inspect:"Escolha o campo editável para a instrução.",waiting:"ComfyUI está a executar."},
 fr:{title:"Génération assistée de vues · ComfyUI",intro:"Choisissez un workflow d'image enregistré et compatible. Une véritable nouvelle vue 3D n'est pas garantie. Aucun téléchargement ni exécution automatique.",workflow:"Workflow installé",refresh:"Actualiser",prepare:"Préparer et valider",prompt:"Consigne de vue",seed:"Graine (facultatif)",selectInput:"Champ texte modifiable",selectSeed:"Champ graine",noInput:"Conserver le texte",noSeed:"Conserver la graine",instruction:"Exemple : profil droit de la même sculpture.",run:"Générer",cancel:"Annuler",state:"État",queued:"En attente",running:"En cours",completed:"Terminé",cancelled:"Annulé",error:"Erreur",unknown:"Inconnu",cancelling:"Annulation",ready:"Workflow préparé. Confirmez pour exécuter.",notReady:"Préparez un workflow.",needImage:"Importez un workflow image dans la Zone ComfyUI.",none:"Aucune image de sortie compatible.",results:"Images générées",add:"Ajouter au sujet",angle:"Azimut (°)",elevation:"Élévation (°)",distance:"Distance (m)",view:"Nom de vue",saved:"Image synthétique ajoutée pour validation.",lineage:"Provenance enregistrée sans modifier les originaux.",confirm:"Exécuter ce workflow dans ComfyUI ?",importConfirm:"Ajouter cette image synthétique non approuvée ?",selectFirst:"Choisissez un workflow.",saveError:"Importation impossible.",note:"Exécution réservée à l'ordinateur du lanceur.",inspect:"Choisissez un champ de texte du workflow.",waiting:"ComfyUI traite la demande."},
 de:{title:"Assistierte Ansichten · ComfyUI",intro:"Wählen Sie einen gespeicherten Bild-Workflow. Neue 3D-Perspektiven sind nicht garantiert. Kein automatischer Download oder Start.",workflow:"Installierter Workflow",refresh:"Workflows laden",prepare:"Vorbereiten und prüfen",prompt:"Ansichtsanweisung",seed:"Seed (optional)",selectInput:"Textfeld wählen",selectSeed:"Seed-Feld",noInput:"Text beibehalten",noSeed:"Seed beibehalten",instruction:"Beispiel: rechte Seitenansicht derselben Skulptur.",run:"Jetzt erzeugen",cancel:"Abbrechen",state:"Status",queued:"Wartend",running:"Läuft",completed:"Fertig",cancelled:"Abgebrochen",error:"Fehler",unknown:"Unbekannt",cancelling:"Abbruch läuft",ready:"Workflow vorbereitet. Ausführung bestätigen.",notReady:"Workflow vorbereiten.",needImage:"Bild-Workflow aus der ComfyUI-Zone importieren.",none:"Keine passenden Ausgabebilder.",results:"Erzeugte Bilder",add:"Zum Objekt hinzufügen",angle:"Azimut (°)",elevation:"Höhe (°)",distance:"Abstand (m)",view:"Ansichtsname",saved:"Synthetisches Bild zur Prüfung registriert.",lineage:"Herkunft gespeichert, Originale unverändert.",confirm:"Workflow in ComfyUI ausführen?",importConfirm:"Als ungeprüftes synthetisches Bild speichern?",selectFirst:"Workflow wählen.",saveError:"Import fehlgeschlagen.",note:"Nur am Launcher-Rechner verfügbar.",inspect:"Textfeld für die Anweisung wählen.",waiting:"ComfyUI verarbeitet."},
 it:{title:"Generazione assistita di viste · ComfyUI",intro:"Scegli un workflow immagine già configurato. Le prospettive 3D non sono garantite. Nessun download o avvio automatico.",workflow:"Workflow installato",refresh:"Aggiorna",prepare:"Prepara e convalida",prompt:"Descrizione prospettiva",seed:"Seed (facoltativo)",selectInput:"Campo testo modificabile",selectSeed:"Campo seed",noInput:"Mantieni testo",noSeed:"Mantieni seed",instruction:"Esempio: vista laterale destra della stessa scultura.",run:"Genera ora",cancel:"Annulla",state:"Stato",queued:"In coda",running:"In esecuzione",completed:"Completato",cancelled:"Annullato",error:"Errore",unknown:"Sconosciuto",cancelling:"Annullamento",ready:"Workflow pronto. Conferma per eseguire.",notReady:"Prepara il workflow.",needImage:"Importa un workflow immagine dalla Zona ComfyUI.",none:"Nessuna immagine compatibile.",results:"Immagini generate",add:"Aggiungi al soggetto",angle:"Azimut (°)",elevation:"Elevazione (°)",distance:"Distanza (m)",view:"Nome vista",saved:"Immagine sintetica aggiunta per la revisione.",lineage:"Origine registrata, originali intatti.",confirm:"Eseguire il workflow in ComfyUI?",importConfirm:"Importare come sintetica non approvata?",selectFirst:"Scegli il workflow.",saveError:"Importazione fallita.",note:"Disponibile solo sul computer principale.",inspect:"Scegli il campo di testo del workflow.",waiting:"ComfyUI sta elaborando."},
 ja:{title:"ComfyUI 補助視点生成",intro:"保存済みの画像ワークフローを選択します。3D視点の生成はモデルに依存し、保証されません。自動ダウンロードや実行はありません。",workflow:"ワークフロー",refresh:"更新",prepare:"準備・検証",prompt:"視点指示",seed:"シード（任意）",selectInput:"テキスト入力",selectSeed:"シード入力",noInput:"テキスト維持",noSeed:"シード維持",instruction:"例: 同じ彫刻の右側面図。",run:"生成",cancel:"中止",state:"状態",queued:"待機中",running:"実行中",completed:"完了",cancelled:"中止済み",error:"エラー",unknown:"不明",cancelling:"中止中",ready:"準備完了。実行を確認してください。",notReady:"準備してください。",needImage:"ComfyUI ゾーンからワークフローを追加してください。",none:"対応画像がありません。",results:"生成画像",add:"被写体へ追加",angle:"方位角 (°)",elevation:"仰角 (°)",distance:"距離 (m)",view:"視点名",saved:"合成画像を未承認で追加しました。",lineage:"生成履歴を保存し、元画像は変更しません。",confirm:"ComfyUI で実行しますか？",importConfirm:"未承認の合成画像として追加しますか？",selectFirst:"ワークフローを選択。",saveError:"画像追加エラー",note:"起動元PCのみ利用可能です。",inspect:"編集可能なテキスト入力を選択。",waiting:"ComfyUI 処理中。"},
 ko:{title:"ComfyUI 보조 시점 생성",intro:"저장된 이미지 워크플로를 선택하세요. 새로운 3D 시점은 모델에 따라 달라지며 보장되지 않습니다. 자동 다운로드/실행은 없습니다.",workflow:"워크플로",refresh:"새로고침",prepare:"준비 및 확인",prompt:"시점 지시",seed:"시드 (선택)",selectInput:"텍스트 입력",selectSeed:"시드 입력",noInput:"텍스트 유지",noSeed:"시드 유지",instruction:"예: 동일한 조각품의 오른쪽 측면.",run:"생성",cancel:"취소",state:"상태",queued:"대기",running:"실행",completed:"완료",cancelled:"취소됨",error:"오류",unknown:"알 수 없음",cancelling:"취소 중",ready:"준비 완료. 실행을 확인하세요.",notReady:"워크플로를 준비하세요.",needImage:"ComfyUI 영역에서 이미지 워크플로를 추가하세요.",none:"호환되는 출력 이미지가 없습니다.",results:"생성 이미지",add:"피사체에 추가",angle:"방위각 (°)",elevation:"고도 (°)",distance:"거리 (m)",view:"시점 이름",saved:"합성 이미지를 미승인으로 등록했습니다.",lineage:"출처 기록, 원본 유지.",confirm:"ComfyUI에서 실행할까요?",importConfirm:"미승인 합성 이미지로 추가할까요?",selectFirst:"워크플로를 선택하세요.",saveError:"가져오기 실패",note:"런처 컴퓨터에서만 사용할 수 있습니다.",inspect:"워크플로의 텍스트 입력을 선택하세요.",waiting:"ComfyUI 실행 중."}
};
const lang=()=>typeof I18N!=="undefined"&&translations[I18N.lang]?I18N.lang:"en";
const t=key=>translations[lang()][key]||translations.en[key]||key;
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
function labeled(key,control){const l=el("label");l.append(el("span",t(key)),control);return l}
function option(select,value,label){select.add(new Option(label,value))}
function imageUrl(id,index){return "/api/workspace/generation/media/"+encodeURIComponent(id)+"/"+index}
function positive(input){const value=input.value.trim();return value===""?null:Number(value)}
function mount(host,getProject,subjectId,api,report,refreshLibrary){
 const section=el("section",undefined,"mv-assisted-panel");
 section.setAttribute("aria-label",t("title"));
 section.append(el("h2",t("title")),el("p",t("intro"),"muted"),el("p",t("note"),"muted"));
 const workflow=el("select"),refresh=el("button",t("refresh")),prepare=el("button",t("prepare"),"primary");
 refresh.type=prepare.type="button";
 const row=el("div",undefined,"row");row.append(labeled("workflow",workflow),refresh,prepare);
 section.append(row);
 const editor=el("div",undefined,"mv-assisted-editor");editor.hidden=true;
 const field=el("select"),seed=el("select"),prompt=el("textarea"),seedValue=el("input");
 prompt.rows=3;prompt.maxLength=3500;prompt.placeholder=t("instruction");
 seedValue.type="number";seedValue.step="1";
 editor.append(labeled("selectInput",field),labeled("prompt",prompt),
               labeled("selectSeed",seed),labeled("seed",seedValue));
 const buttons=el("div",undefined,"row");
 const run=el("button",t("run"),"primary"),cancel=el("button",t("cancel"),"danger");
 run.type=cancel.type="button";cancel.disabled=true;
 buttons.append(run,cancel);editor.append(buttons);
 const status=el("p",undefined,"muted");status.setAttribute("role","status");status.setAttribute("aria-live","polite");
 const outputs=el("div",undefined,"mv-assisted-outputs");const results=el("h3",t("results"));
 section.append(editor,status,results,outputs);
 host.append(section);
 let token="",workflowId="",generationId="",poll=null,fields=[],jobActive=false,requestId=0,abandoned=false;
 const stateLabels={queued:"queued",running:"running",completed:"completed",cancelled:"cancelled",error:"error",unknown:"unknown",cancelling:"cancelling"};
 function state(text){status.textContent=text}
 function stop(){if(poll){clearTimeout(poll);poll=null}jobActive=false;cancel.disabled=true;run.disabled=!token}
 function reset(){stop();token="";workflowId="";generationId="";fields=[];editor.hidden=true;outputs.replaceChildren();state("")}
 async function workflows(){
   reset();workflow.replaceChildren();
   try{
     const [cfg,data]=await Promise.all([api("/api/workspace/comfyui"),api("/api/workspace/workflows")]);
     if(cfg.mode==="native")throw Error("ComfyUI disabled in native mode");
     const list=(data.workflows||[]).filter(w=>w.category==="image");
     option(workflow,"",list.length?t("selectFirst"):t("needImage"));
     for(const w of list)option(workflow,w.id,w.name);
   }catch(e){option(workflow,"",t("needImage"));state(e.message)}
 }
 function inputField(selection,filter,emptyLabel){
   selection.replaceChildren();option(selection,"",t(emptyLabel));
   for(const f of fields.filter(filter))option(selection,f.node+"|"+f.name,
      f.class_type+" #"+f.node+" · "+f.name);
 }
 prepare.onclick=async()=>{
   const id=workflow.value;if(!id){state(t("selectFirst"));return}
   reset();prepare.disabled=true;
   try{
     const prepared=await api("/api/workspace/generation/prepare",{
       method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({workflow_id:id})
     });
     token=prepared.token;workflowId=id;fields=prepared.fields||[];
     inputField(field,f=>f.kind==="text","noInput");
     inputField(seed,f=>f.kind==="integer"&&(/seed/i.test(f.name)),"noSeed");
     prompt.value="";seedValue.value="";
     editor.hidden=false;run.disabled=false;
     state(t("ready")+" "+t("inspect"));
   }catch(e){state(e.message)}finally{prepare.disabled=false}
 };
 field.onchange=()=>{
   const f=fields.find(f=>f.node+"|"+f.name===field.value);
   prompt.value=f?String(f.value):"";
 };
 seed.onchange=()=>{
   const f=fields.find(f=>f.node+"|"+f.name===seed.value);
   seedValue.value=f?String(f.value):"";
 };
 async function checkStatus(){
   const id=generationId,sequence=++requestId;
   if(!id||abandoned||!host.isConnected){stop();return}
   try{
     const result=await api("/api/workspace/generation/"+encodeURIComponent(id));
     if(id!==generationId||sequence!==requestId)return;
     state(t("state")+": "+t(stateLabels[result.state]||"unknown")+
          (["running","queued"].includes(result.state)?" · "+t("waiting"):""));
     if(["completed","cancelled","error"].includes(result.state)){
       stop();
       if(result.state==="completed")renderOutputs(id,result.outputs||[]);
       return;
     }
     // The OrkiLab generation endpoint performs queue polling; no fake percent.
     poll=setTimeout(checkStatus,2500);
   }catch(e){state(e.message);poll=setTimeout(checkStatus,4000)}
 }
 run.onclick=async()=>{
   if(!token||!workflowId){state(t("notReady"));return}
   if(!window.confirm(t("confirm")))return;
   run.disabled=true;prepare.disabled=true;
   try{
     let preparedToken=token;
     const edits=[];
     for(const [selector,input] of [[field,prompt],[seed,seedValue]]){
       if(!selector.value)continue;
       const f=fields.find(x=>x.node+"|"+x.name===selector.value);
       if(!f)continue;
       let value=f.kind==="integer"?Number(input.value):input.value;
       if(f.kind==="integer"&&(!Number.isSafeInteger(value)||!input.value.trim()))throw Error("Invalid integer seed");
       edits.push({node:f.node,name:f.name,value});
     }
     if(edits.length){
       const changed=await api("/api/workspace/generation/parameters",{
         method:"POST",headers:{"Content-Type":"application/json"},
         body:JSON.stringify({token:preparedToken,edits})
       });
       preparedToken=changed.token;token=preparedToken;
     }
     const result=await api("/api/workspace/generation",{
       method:"POST",headers:{"Content-Type":"application/json"},
       body:JSON.stringify({token:preparedToken,workflow_id:workflowId,confirm:true})
     });
     token="";generationId=result.id;jobActive=true;cancel.disabled=false;
     editor.hidden=false;outputs.replaceChildren();state(t("queued"));
     checkStatus();
   }catch(e){run.disabled=false;state(e.message)}
   finally{prepare.disabled=false}
 };
 cancel.onclick=async()=>{
   if(!generationId||!jobActive)return;
   cancel.disabled=true;
   try{
     await api("/api/workspace/generation/"+encodeURIComponent(generationId)+"/cancel",{
       method:"POST",headers:{"Content-Type":"application/json"},body:"{}"
     });
     state(t("cancelling"));
     checkStatus();
   }catch(e){cancel.disabled=false;state(e.message)}
 };
 function renderOutputs(id,items){
   outputs.replaceChildren();
   const images=items.map((item,index)=>({item,index})).filter(({item})=>
      ["image/png","image/jpeg","image/webp"].includes(item.mime)&&item.type==="output");
   if(!images.length){outputs.append(el("p",t("none"),"muted"));return}
   outputs.append(el("p",t("lineage"),"muted"));
   for(const {item,index} of images){
     const card=el("article",undefined,"mv-assisted-card");
     const img=el("img");img.loading="lazy";img.src=imageUrl(id,index);img.alt=item.filename;
     const name=el("p",item.filename,"muted");
     const form=el("form");
     const view=el("input"),angle=el("input"),elevation=el("input"),distance=el("input");
     view.maxLength=100;
     for(const input of [angle,elevation,distance]){input.type="number";input.step="any"}
     angle.min="0";angle.max="359.9999";elevation.min="-90";elevation.max="90";
     distance.min="0.0001";
     form.append(labeled("view",view),labeled("angle",angle),
                 labeled("elevation",elevation),labeled("distance",distance));
     const add=el("button",t("add"),"primary");add.type="submit";form.append(add);
     const feedback=el("p",undefined,"muted");feedback.setAttribute("role","status");
     form.onsubmit=async event=>{
       event.preventDefault();
       if(!window.confirm(t("importConfirm")))return;
       add.disabled=true;
       try{
         const project=getProject();
         await api("/api/workspace/multiview/projects/"+encodeURIComponent(project)+
           "/subjects/"+encodeURIComponent(subjectId)+"/generated",{
           method:"POST",headers:{"Content-Type":"application/json"},
           body:JSON.stringify({confirm:true,generation_id:id,output_index:index,
             view_name:view.value,azimuth_deg:positive(angle),
             elevation_deg:positive(elevation),distance_m:positive(distance)})
         });
         feedback.textContent=t("saved");
         if(typeof refreshLibrary==="function")await refreshLibrary();
       }catch(e){feedback.textContent=t("saveError")+": "+e.message;add.disabled=false}
     };
     card.append(img,name,form,feedback);outputs.append(card);
   }
 }
 workflow.onchange=reset;
 refresh.onclick=workflows;
 workflows();
 return {dispose:()=>{abandoned=true;stop();}};
}
window.OrkiMultiviewAssist={mount};
})();
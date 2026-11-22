/* Multiview requested-view generator. Reuses OrkiLab's validated ComfyUI job API. */
(function(){
"use strict";
const words={
 es:{title:"Generar vista faltante",intro:"Selecciona fotografías reales, asigna cada una a una entrada de imagen del workflow y solicita una vista. El workflow debe aceptar referencias: un modelo de texto a imagen no garantiza conservar el sujeto.",photos:"Fotografías de referencia (1–4)",workflow:"Workflow ComfyUI compatible",refresh:"Actualizar referencias y workflows",direction:"Vista solicitada",height:"Altura de cámara",distance:"Distancia aparente",extra:"Indicaciones adicionales (opcional)",stage:"Preparar fotos y workflow",mapping:"Asignación de imágenes a nodos LoadImage",prompt:"Campo de texto editable",run:"Generar nueva vista",cancel:"Cancelar generación",pending:"Selecciona fotos reales y un workflow compatible antes de continuar.",noRefs:"Vincula primero fotografías reales al sujeto.",noWorkflow:"Importa primero un workflow de imagen con nodos LoadImage conectados desde Zona ComfyUI.",badNodes:"El workflow necesita al menos una entrada LoadImage editable por cada foto elegida; selecciona menos fotos u otro workflow.",badPrompt:"Elige una entrada de texto editable; el workflow no tiene campos adecuados.",ready:"Las referencias se han copiado a ComfyUI/input. Configura las asignaciones y confirma para generar.",running:"Generando en ComfyUI…",finished:"Generación terminada. Revisa la imagen antes de incorporarla.",register:"Incorporar como sintética pendiente de revisión",saved:"Imagen sintética vinculada con su vista solicitada; los grados siguen desconocidos.",note:"Los modelos pueden inventar partes ocultas. Las copias subidas a ComfyUI/input no se eliminan automáticamente; tus originales siguen intactos.",confirmStage:"¿Copiar estas fotos a la carpeta input del ComfyUI configurado? Aún no se generará nada.",confirmRun:"¿Ejecutar este workflow con las fotos y la vista indicadas?",confirmImport:"¿Registrar esta imagen sintética en el sujeto sin aprobarla?",front:"Frontal",front_right:"Frontal derecha",right:"Derecha",back_right:"Trasera derecha",back:"Trasera",back_left:"Trasera izquierda",left:"Izquierda",front_left:"Frontal izquierda",top:"Superior",bottom:"Inferior",above:"Desde arriba",level:"A nivel",below:"Desde abajo",close:"Cerca",medium:"Media",far:"Lejos",none:"No modificar",stop:"Trabajo cancelado",mismatch:"Cambió el proyecto; la operación no se ha continuado."},
 en:{title:"Generate missing viewpoint",intro:"Select real photographs, map each to an image input in a reference-capable workflow, and request a view. Text-to-image models cannot guarantee subject fidelity.",photos:"Reference photos (1–4)",workflow:"Compatible ComfyUI workflow",refresh:"Refresh references and workflows",direction:"Requested view",height:"Camera height",distance:"Apparent distance",extra:"Extra instructions (optional)",stage:"Stage photos and prepare workflow",mapping:"Map images to LoadImage nodes",prompt:"Editable text input",run:"Generate new view",cancel:"Cancel generation",pending:"Select real photos and a compatible workflow to continue.",noRefs:"Link real photos to this subject first.",noWorkflow:"Import an image workflow with connected LoadImage nodes in ComfyUI Zone.",badNodes:"Workflow needs an editable LoadImage input for each selected photo; select fewer photos or another workflow.",badPrompt:"Choose an editable prompt input; no compatible field found.",ready:"Reference copies are now in ComfyUI/input. Map them and confirm to generate.",running:"Generating with ComfyUI…",finished:"Generation completed. Review before importing.",register:"Register as synthetic and unreviewed",saved:"Synthetic image linked with its requested view; measured degrees remain unknown.",note:"Models can hallucinate hidden details. Copies staged in ComfyUI/input are not automatically removed; your originals remain intact.",confirmStage:"Copy these photos into the configured ComfyUI input folder? No generation yet.",confirmRun:"Execute the workflow with these references and requested view?",confirmImport:"Import this result as an unreviewed synthetic image?",front:"Front",front_right:"Front right",right:"Right",back_right:"Back right",back:"Back",back_left:"Back left",left:"Left",front_left:"Front left",top:"Top",bottom:"Bottom",above:"Above",level:"Level",below:"Below",close:"Close",medium:"Medium",far:"Far",none:"Do not change",stop:"Job cancelled",mismatch:"Project changed; operation stopped."}
};
const directions=["front","front_right","right","back_right","back","back_left","left","front_left","top","bottom"];
const elevations=["level","above","below"],distances=["medium","close","far"];
function t(k){const lang=typeof I18N!=="undefined"&&I18N.lang==="es"?"es":"en";return words[lang][k]||k}
function elt(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e}
function choose(label,options){const wrap=elt("label");wrap.append(elt("span",label));const select=elt("select");for(const key of options)select.add(new Option(t(key),key));wrap.append(select);return [wrap,select]}
function u(project,suffix){return "/api/workspace/multiview/projects/"+encodeURIComponent(project)+suffix}
function post(api,url,data){return api(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)})}
function mount(host,getProject,subjectId,api,onImport){
 const originalProject=getProject(),panel=elt("section");panel.className="mv-requested-generation no-i18n";
 panel.append(elt("h2",t("title")),elt("p",t("intro")));
 const refresh=elt("button",t("refresh"));refresh.type="button";
 const refs=elt("div");const flowSelect=elt("select");
 const flowLabel=elt("label",t("workflow"));flowLabel.append(flowSelect);
 const [directionLabel,direction]=choose(t("direction"),directions);
 const [heightLabel,height]=choose(t("height"),elevations);
 const [distanceLabel,distance]=choose(t("distance"),distances);
 const extra=elt("textarea");extra.maxLength=500;extra.rows=2;
 const extraLabel=elt("label",t("extra"));extraLabel.append(extra);
 const stage=elt("button",t("stage"));stage.type="button";
 const controls=elt("div");controls.className="mv-request-controls";
 controls.append(flowLabel,directionLabel,heightLabel,distanceLabel,extraLabel,stage);
 const message=elt("p",t("pending"));message.setAttribute("role","status");
 const mapping=elt("div");mapping.hidden=true;
 const mappingTitle=elt("h3",t("mapping"));mapping.append(mappingTitle);
 const fieldsWrap=elt("div");mapping.append(fieldsWrap);
 const promptWrap=elt("label",t("prompt")),promptField=elt("select");
 promptWrap.append(promptField);mapping.append(promptWrap);
 const edit=elt("textarea");edit.rows=4;edit.maxLength=3500;mapping.append(edit);
 const run=elt("button",t("run"));run.type="button";const cancel=elt("button",t("cancel"));cancel.type="button";cancel.disabled=true;
 mapping.append(run,cancel);
 const outputs=elt("div");
 panel.append(refresh,elt("h3",t("photos")),refs,controls,message,mapping,outputs,elt("p",t("note")));host.append(panel);
 let candidates=[],installed=[],chosen=[],upload=[],prepared=null,active="",timer=null,disposed=false,stagedRequest=null;
 const ok=()=>!disposed&&host.isConnected&&getProject()===originalProject;
 const status=x=>message.textContent=x;
 function stop(){if(timer)clearTimeout(timer);timer=null;cancel.disabled=true;}
 function dispose(){disposed=true;stop();}
 function resetPrepared(){prepared=null;mapping.hidden=true;fieldsWrap.replaceChildren();outputs.replaceChildren();stop();}
 function checked(){return [...refs.querySelectorAll("input:checked")].map(x=>x.value)}
 function selectOne(){return [direction.value,height.value,distance.value]}
 async function refreshAll(){
  if(!ok())return;
  resetPrepared();refs.replaceChildren();flowSelect.replaceChildren(new Option(t("workflow"),""));
  try{
   const [photos,workflows,settings]=await Promise.all([
    api(u(originalProject,"/subjects/"+subjectId+"/captures?sort=oldest")),
    api("/api/workspace/workflows"),api("/api/workspace/comfyui")]);
   if(!ok())return;
   if(settings.mode==="native"){panel.hidden=true;return}panel.hidden=false;
   candidates=(photos.captures||[]).filter(x=>["real_photo","unknown","video_frame"].includes(x.source_type)&&x.review!=="rejected");
   for(const c of candidates){
     const label=elt("label"),box=elt("input");box.type="checkbox";box.value=c.id;
     label.append(box,elt("span",c.view_name||c.name));refs.append(label);
     box.onchange=()=>{if(checked().length>4){box.checked=false;status(typeof I18N!=="undefined"&&I18N.lang==="es"?"Selecciona un máximo de cuatro fotografías de referencia.":"Select up to four reference photographs.")}resetPrepared()};
   }
   if(!candidates.length)refs.append(elt("p",t("noRefs")));
   installed=(workflows.workflows||[]).filter(x=>x.category==="image");
   for(const f of installed)flowSelect.add(new Option(f.name,f.id));
   if(!installed.length)status(t("noWorkflow"));else status(t("pending"));
  }catch(e){status(e.message)}
 }
 function connectedImageInputs(p){
  const connected=new Set();
  for(const node of Object.values(p.graph||{})){
   if(!node||!node.inputs)continue;
   for(const value of Object.values(node.inputs)){
    if(Array.isArray(value)&&value.length===2&&
       (typeof value[0]==="string"||typeof value[0]==="number")&&Number.isInteger(value[1]))
     connected.add(String(value[0]));
   }
  }
  return (p.fields||[]).filter(f=>inputType(f)&&connected.has(String(f.node)));
 }
 function editablePromptFields(p){
  return (p.fields||[]).filter(f=>f.kind==="text"&&/text|prompt/i.test(f.name));
 }
 function inputType(f){return f.kind==="choice"&&/loadimage/i.test(f.class_type)&&f.name==="image"}
 function matches(f,name){return (f.choices||[]).includes(name)}
 let assigned=[];
 stage.onclick=async()=>{
  const ids=checked(),flow=flowSelect.value;
  if(!ok()||!ids.length||ids.length>4||!flow){status(t("pending"));return}
  if(!window.confirm(t("confirmStage")))return;
  stage.disabled=true;resetPrepared();
  try{
   // Fail before copying photos to ComfyUI when the workflow cannot consume
   // the selected references or has no editable view instruction.
   const inspected=await post(api,"/api/workspace/generation/prepare",{workflow_id:flow});
   if(!ok())throw Error(t("mismatch"));
   if(connectedImageInputs(inspected).length<ids.length)throw Error(t("badNodes"));
   if(!editablePromptFields(inspected).length)throw Error(t("badPrompt"));
   const result=await post(api,u(originalProject,"/subjects/"+subjectId+"/reference-upload"),
                      {confirm:true,capture_ids:ids});
   if(!ok())throw Error(t("mismatch"));
   upload=result.references;chosen=ids;stagedRequest={direction:direction.value,height:height.value,distance:distance.value,extra:extra.value};
   const p=await post(api,"/api/workspace/generation/prepare",{workflow_id:flow});
   if(!ok())throw Error(t("mismatch"));
   // Re-check against ComfyUI's image choices refreshed after upload.
   const inputs=connectedImageInputs(p);
   if(inputs.length<ids.length||!upload.every(x=>inputs.some(f=>matches(f,x.comfy_name))))throw Error(t("badNodes"));
   prepared={token:p.token,workflowId:flow,fields:p.fields||[]};
   fieldsWrap.replaceChildren();assigned=[];
   for(const [i,r] of upload.entries()){
    const label=elt("label",(candidates.find(x=>x.id===r.capture_id)?.name||"Foto")+" → LoadImage");
    const chooser=elt("select");
    chooser.add(new Option(t("none"),""));
    for(const input of inputs.filter(f=>matches(f,r.comfy_name)))
     chooser.add(new Option(f.class_type+" #"+f.node+" · "+f.name,input.node+"|"+input.name));
    // Default to unique distinct node, when available.
    const first=[...chooser.options].find(x=>x.value&&!assigned.some(s=>s.value===x.value));
    if(first)chooser.value=first.value;
    label.append(chooser);fieldsWrap.append(label);assigned.push(chooser);
   }
   const texts=editablePromptFields(prepared);
   promptField.replaceChildren(new Option(t("none"),""));
   for(const f of texts)promptField.add(new Option(f.class_type+" #"+f.node+" · "+f.name,f.node+"|"+f.name));
   const preferred=texts.find(f=>/CLIPTextEncode|TextEncode|Prompt/i.test(f.class_type))||texts[0];
   if(preferred)promptField.value=preferred.node+"|"+preferred.name;
   const selected=preferred?.value||"";
   edit.value=selected+"\n"+makePrompt(stagedRequest);
   mapping.hidden=false;status(t("ready"));
  }catch(e){status(e.message);resetPrepared()}finally{stage.disabled=false}
 };
 function makePrompt(p){
  return "Render the same subject shown in the supplied reference images, preserving identity, materials, proportions, colors and visible identifying details. "+
   "Requested camera viewpoint: "+p.direction.replaceAll("_"," ")+", camera height "+p.height+", apparent distance "+p.distance+
   ". Clean single-subject image. Do not invent accessories or alter the subject. This is a synthetic view; hidden geometry may be unknown. "+
   p.extra;
 }
 promptField.onchange=()=>{const f=prepared?.fields.find(x=>x.node+"|"+x.name===promptField.value);edit.value=(f?.value||"")+"\n"+makePrompt(stagedRequest)};
 async function poll(){
  if(!active||!ok())return;
  try{
   const x=await api("/api/workspace/generation/"+encodeURIComponent(active));
   if(!ok())return;
   status(x.state==="completed"?t("finished"):t("running")+" · "+x.state);
   if(["completed","cancelled","error"].includes(x.state)){
     stop();if(x.state==="completed")showOutputs(x.outputs||[],active);else status(x.state);
     return;
   }
  }catch(e){status(e.message)}
  timer=setTimeout(poll,3000);
 }
 run.onclick=async()=>{
  if(!prepared||!ok()||!stagedRequest)return;
  const fieldKeys=assigned.map(x=>x.value);
  if(fieldKeys.some(x=>!x)||new Set(fieldKeys).size!==fieldKeys.length){status(t("badNodes"));return}
  if(!promptField.value){status(t("badPrompt"));return}
  if(!window.confirm(t("confirmRun")))return;
  run.disabled=true;cancel.disabled=true;
  try{
   const edits=assigned.map((sel,i)=>{
     const f=prepared.fields.find(x=>x.node+"|"+x.name===sel.value);
     if(!f||!matches(f,upload[i].comfy_name))throw Error(t("badNodes"));
     return {node:f.node,name:f.name,value:upload[i].comfy_name};
   });
   const prompt=prepared.fields.find(x=>x.node+"|"+x.name===promptField.value);
   if(!prompt||prompt.kind!=="text")throw Error(t("badPrompt"));
   if(edits.some(e=>e.node===prompt.node&&e.name===prompt.name))throw Error(t("badPrompt"));
   edits.push({node:prompt.node,name:prompt.name,value:edit.value});
   const preparedUpdate=await post(api,"/api/workspace/generation/parameters",{token:prepared.token,edits});
   const launched=await post(api,"/api/workspace/generation",{token:preparedUpdate.token,workflow_id:prepared.workflowId,confirm:true});
   active=launched.id;prepared=null;cancel.disabled=false;mapping.hidden=true;
   status(t("running"));poll();
  }catch(e){status(e.message)}finally{run.disabled=false}
 };
 cancel.onclick=async()=>{
  if(!active)return;
  cancel.disabled=true;
  try{await post(api,"/api/workspace/generation/"+encodeURIComponent(active)+"/cancel",{});status(t("stop"));poll()}
  catch(e){status(e.message);cancel.disabled=false}
 };
 function showOutputs(items,generationId){
  outputs.replaceChildren();
  const targets={...stagedRequest},ids=[...chosen];
  items.forEach((item,index)=>{
   if(!["image/png","image/jpeg","image/webp"].includes(item.mime)||item.type!=="output")return;
   const card=elt("article");card.className="mv-requested-output";
   const img=elt("img");img.alt=item.filename||"generated";img.loading="lazy";
   img.src="/api/workspace/generation/media/"+encodeURIComponent(generationId)+"/"+index;
   const importBtn=elt("button",t("register"));importBtn.type="button";
   const feedback=elt("p");
   importBtn.onclick=async()=>{
    if(!ok()||!window.confirm(t("confirmImport")))return;
    importBtn.disabled=true;
    try{
     await post(api,u(originalProject,"/subjects/"+subjectId+"/generated"),{
      confirm:true,generation_id:generationId,output_index:index,
      view_name:t(targets.direction),requested_direction:targets.direction,
      requested_elevation:targets.height,requested_distance:targets.distance,
      reference_capture_ids:ids,azimuth_deg:null,elevation_deg:null,distance_m:null});
     feedback.textContent=t("saved");await onImport();
    }catch(e){feedback.textContent=e.message;importBtn.disabled=false}
   };
   card.append(img,importBtn,feedback);outputs.append(card);
  });
 }
 flowSelect.onchange=resetPrepared;for(const select of [direction,height,distance])select.onchange=resetPrepared;
 extra.oninput=resetPrepared;refresh.onclick=refreshAll;
 refreshAll();
 return {dispose};
}
window.OrkiMultiviewGenerateViews={mount};
})();

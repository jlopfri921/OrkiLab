/* Opt-in local AI viewpoint hint: never writes geometry or saves without a second click. */
(function(){
"use strict";
const strings={
 es:{title:"Detectar punto de vista (IA local)",intro:"Clasificación orientativa: no es una medición de azimut ni una posición 3D. La referencia frontal debe decidirla una persona.",model:"Modelo de visión Ollama",find:"Cargar modelos locales",run:"Analizar esta foto",save:"Confirmar y guardar orientación",direction:"Orientación sugerida (editable)",elevation:"Altura de cámara sugerida",distance:"Distancia aparente",confidence:"Confianza declarada por el modelo",unknown:"Desconocida",none:"No hay modelos locales de visión disponibles. Instala y configura un modelo multimodal en Ollama; no se descargará automáticamente.",ready:"Elige un modelo de visión local y pulsa Analizar.",running:"Analizando en Ollama local…",review:"Revisa y corrige la orientación antes de confirmar. No se guardan grados numéricos ni se cambia la revisión de la foto.",done:"Orientación cualitativa guardada como estimación. Ningún ángulo numérico se ha añadido.",confirm:"¿Guardar esta etiqueta como estimación de IA? No se alterarán los grados ni la imagen original.",error:"No ha sido posible analizar la fotografía.",front:"Frontal",front_right:"Frontal derecha",right:"Derecha",back_right:"Trasera derecha",back:"Trasera",back_left:"Trasera izquierda",left:"Izquierda",front_left:"Frontal izquierda",top:"Superior",bottom:"Inferior",above:"Desde arriba",level:"A su altura",below:"Desde abajo",close:"Cerca",medium:"Media",far:"Lejos",low:"Baja",high:"Alta"},
 en:{title:"Detect viewpoint (local AI)",intro:"Qualitative guess, NOT measured azimuth or 3D camera position. A human must define what counts as front.",model:"Ollama vision model",find:"Load local models",run:"Analyze this photo",save:"Confirm and save orientation",direction:"Suggested view (editable)",elevation:"Suggested camera height",distance:"Apparent distance",confidence:"Model-stated confidence",unknown:"Unknown",none:"No local vision models found. Install/configure a multimodal Ollama model; nothing is downloaded automatically.",ready:"Choose a local vision model, then click Analyze.",running:"Analyzing with local Ollama…",review:"Review and correct the view before confirming. No numeric angles are saved and photo review stays unchanged.",done:"Qualitative orientation saved as an estimate. No numeric camera angle was added.",confirm:"Save this label as an AI estimate? Numeric degrees and original photos will not change.",error:"Could not analyze the photograph.",front:"Front",front_right:"Front right",right:"Right",back_right:"Back right",back:"Back",back_left:"Back left",left:"Left",front_left:"Front left",top:"Top",bottom:"Bottom",above:"Above",level:"Level",below:"Below",close:"Close",medium:"Medium",far:"Far",low:"Low",high:"High"}
};
const directions=["front","front_right","right","back_right","back","back_left","left","front_left","top","bottom","unknown"];
function lang(){return typeof I18N!=="undefined"&&I18N.lang==="es"?"es":"en"}
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

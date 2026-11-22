/* Shared mode-aware navigation + guide link. Never removes project/trainer controls. */
(function(){
"use strict";
let native=false,settings=null,busy=false;
const anchorText={es:"Guía y ayuda",en:"Guide & help",pt:"Guia e ajuda",fr:"Guide et aide",de:"Hilfe & Anleitung",it:"Guida e aiuto",ja:"ガイドとヘルプ",ko:"가이드 및 도움말"};
function language(){const code=typeof I18N!=="undefined"?I18N.lang:"en";return anchorText[code]?code:"en"}
function label(){return anchorText[language()]}
function hide(node,on){if(!node)return;if(node.hidden!==on)node.hidden=on;if(on){if(!node.hasAttribute("data-orki-native-hidden"))node.setAttribute("data-orki-native-hidden","");node.style.setProperty("display","none","important")}else{node.removeAttribute("data-orki-native-hidden");node.style.removeProperty("display")}}
function reconcile(){
 if(busy)return;busy=true;
 try{
  const menus=["#home-navigation","#comfy-navigation",".studio-navigation",".queue-sidebar",".orki-app-nav"];
  document.querySelectorAll(menus.join(",")).forEach(nav=>{
   if(nav.closest("#orki-mobile-sheet"))return;
   if(!nav.querySelector('a[href="/workspace/guide"]')){
    const a=document.createElement("a");a.href="/workspace/guide";a.textContent=label();a.className="orki-guide-link";
    if(location.pathname.replace(/[/]$/,"")==="/workspace/guide")a.setAttribute("aria-current","page");
    const version=nav.querySelector(".orki-nav-version, #version, #orki-shell-version");
    if(version)nav.insertBefore(a,version);else nav.append(a);
   }else nav.querySelectorAll('a[href="/workspace/guide"]').forEach(a=>{
    if(a.textContent!==label())a.textContent=label();
   });
   // In every navigation the version is always the final element. Reconcile
   // after the canonical menu is cloned and after mobile/locale updates.
   const indicator=nav.querySelector(".orki-nav-version, #version, #orki-shell-version");
   if(indicator&&indicator.nextElementSibling)nav.append(indicator);
  });
  document.querySelectorAll('a[href^="/workspace/comfyui"]').forEach(a=>hide(a,native));
  // Avoid hiding other controls in these cards; they are ComfyUI-only overview tiles.
  for(const id of ["control-comfy","control-workflows","control-loras"]){
   const node=document.getElementById(id);if(node)hide(node.closest("article"),native);
  }
  document.querySelectorAll(".orki-quick-grid>a[href^='/workspace/comfyui']").forEach(a=>hide(a,native));
  document.querySelectorAll(".mv-assisted-panel,.mv-requested-generation").forEach(x=>hide(x,native));
  document.querySelectorAll("#orki-mobile-sheet a[href^='/workspace/comfyui']").forEach(a=>hide(a,native));
  const mode=document.getElementById("orki-mode-setting");
  if(mode&&document.activeElement!==mode)mode.value=native?"native":settings?.mode||"hybrid";
 }finally{busy=false}
}
async function load(){
 try{
  const response=await fetch("/api/workspace/comfyui",{cache:"no-store",credentials:"same-origin"});
  if(!response.ok)return;
  settings=await response.json();native=settings.mode==="native";
  document.documentElement.dataset.orkiEngineMode=settings.mode||"hybrid";
  if(native&&location.pathname.replace(/\/$/,"")==="/workspace/comfyui"){
   location.replace("/workspace?dialog=settings");return;
  }
  reconcile();
 }catch(e){console.warn("OrkiLab mode visibility:",e)}
}
function attachModeSetting(){
 const settingsDialog=document.getElementById("settings-dialog");
 if(!settingsDialog||document.getElementById("orki-mode-setting"))return;
 const form=document.createElement("form");form.id="orki-mode-form";
 form.style.cssText="display:grid;gap:10px;margin:12px 0;padding:12px;border:1px solid #45617b;border-radius:10px";
 const heading=document.createElement("h3");heading.textContent=language()==="es"?"Modo de funcionamiento":"Operating mode";
 const description=document.createElement("p");description.textContent=language()==="es"
  ?"En modo independiente se ocultan las funciones de ComfyUI, sin borrar proyectos ni configuraciones. Puedes volver a activarlas aquí."
  :"Native mode hides ComfyUI tools without deleting projects or configuration. Re-enable them here.";
 const select=document.createElement("select");select.id="orki-mode-setting";
 for(const [value,es,en] of [["native","Solo OrkiLab (independiente)","OrkiLab only (native)"],["comfy","Con ComfyUI","ComfyUI connected"],["hybrid","Híbrido","Hybrid"]]){
  select.add(new Option(language()==="es"?es:en,value));
 }
 select.value=settings?.mode||"hybrid";
 const save=document.createElement("button");save.className="primary";save.type="submit";
 save.textContent=language()==="es"?"Guardar modo":"Save mode";
 const feedback=document.createElement("p");feedback.setAttribute("role","status");
 form.append(heading,description,select,save,feedback);
 settingsDialog.querySelector(".settings-dialog-head")?.after(form);
 form.onsubmit=async event=>{
  event.preventDefault();save.disabled=true;
  try{
   const response=await fetch("/api/workspace/comfyui",{method:"POST",credentials:"same-origin",
    headers:{"Content-Type":"application/json"},body:JSON.stringify({mode:select.value})});
   const data=await response.json();
   if(!response.ok)throw Error(data.error||"Could not save mode");
   settings=data;native=data.mode==="native";feedback.textContent=language()==="es"?"Modo guardado":"Mode saved";
   document.documentElement.dataset.orkiEngineMode=data.mode;
   reconcile();window.dispatchEvent(new Event("orkilab:engine-mode-changed"));
   // Rebuild shell and cards consistently without leaving stale modal links.
   location.reload();
  }catch(e){feedback.textContent=e.message;save.disabled=false}
 };
}
function install(){
 attachModeSetting();load();
 const observer=new MutationObserver(changes=>{
  if(changes.some(x=>x.addedNodes.length)){queueMicrotask(()=>{attachModeSetting();reconcile()})}
 });
 observer.observe(document.body,{subtree:true,childList:true});
 document.addEventListener("orkilab:language-changed",reconcile);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",install);else install();
})();

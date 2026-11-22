/* Shared manual theme selector; local browser preference, no account/server calls.
   The selected value is shared by same-origin standalone pages and embedded frames. */
(function(){
 "use strict";
 const KEY="orkilab.ui.theme.v1";
 const names={
  es:["☾ Oscuro","☀ Claro","Cambiar a modo oscuro","Cambiar a modo claro"],
  en:["☾ Dark","☀ Light","Switch to dark mode","Switch to light mode"],
  pt:["☾ Escuro","☀ Claro","Mudar para modo escuro","Mudar para modo claro"],
  fr:["☾ Sombre","☀ Clair","Passer en mode sombre","Passer en mode clair"],
  de:["☾ Dunkel","☀ Hell","Zum dunklen Modus wechseln","Zum hellen Modus wechseln"],
  it:["☾ Scuro","☀ Chiaro","Passa al tema scuro","Passa al tema chiaro"],
  ja:["☾ ダーク","☀ ライト","ダークモードに変更","ライトモードに変更"],
  ko:["☾ 다크","☀ 라이트","다크 모드로 전환","라이트 모드로 전환"]
 };
 const language=()=>{
  const code=(window.I18N?.lang||document.querySelector("select#language")?.value||document.documentElement.lang||"en").toLowerCase().slice(0,2);
  return names[code]||names.en;
 };
 const root=document.documentElement;
 const read=()=>{try{const v=localStorage.getItem(KEY);return v==="light"||v==="dark"?v:"dark"}catch(e){return "dark"}};
 const apply=(theme,persist)=>{
  const chosen=theme==="light"?"light":"dark";
  root.dataset.orkiTheme=chosen;
  if(persist){try{localStorage.setItem(KEY,chosen)}catch(e){}}
  // Use existing contrasting OrkiLab logo variants in the shared header.
  for(const logo of document.querySelectorAll('header img[src*="orkilab-logo-"]')){
   const current=logo.getAttribute("src")||"";
   if(current.endsWith("orkilab-logo-dark.svg")||current.endsWith("orkilab-logo-light.svg")){
    logo.setAttribute("src",chosen==="light"?
      "/assets/orkilab/orkilab-logo-light.svg":
      "/assets/orkilab/orkilab-logo-dark.svg");
   }
  }
  for(const button of document.querySelectorAll(".orki-theme-toggle")){
   const light=chosen==="light";
   const labels=language();
   button.textContent=light?labels[0]:labels[1];
   button.setAttribute("aria-label",light?labels[2]:labels[3]);
   button.setAttribute("aria-pressed",String(light));
  }
 };
 apply(read(),false);
 function mount(){
  if(document.querySelector(".orki-theme-toggle"))return;
  const header=document.querySelector("body > header, header.orki-shell-header");
  if(!header)return;
  const target=header.querySelector(".row")||header;
  const button=document.createElement("button");
  button.type="button";button.className="orki-theme-toggle no-i18n";
  button.addEventListener("click",()=>apply(root.dataset.orkiTheme==="light"?"dark":"light",true));
  target.appendChild(button);
  apply(read(),false);
 }
 if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);
 else mount();
 window.addEventListener("storage",e=>{if(e.key===KEY)apply(read(),false)});
 document.addEventListener("orkilab:language-changed",()=>apply(root.dataset.orkiTheme,false));
 document.addEventListener("change",e=>{if(e.target?.matches?.("select#language,select#workspace-language"))apply(root.dataset.orkiTheme,false)});
 window.addEventListener("message",e=>{
  if(e.origin!==window.location.origin||!e.data||e.data.type!=="orkilab-theme-request")return;
  apply(read(),false);
 });
 window.OrkiLabTheme={get:()=>root.dataset.orkiTheme,set:theme=>apply(theme,true)};
})();

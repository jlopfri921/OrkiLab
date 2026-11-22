/* Shared manual theme selector; local browser preference, no account/server calls.
   The selected value is shared by same-origin standalone pages and embedded frames. */
(function(){
 "use strict";
 const KEY="orkilab.ui.theme.v1";
 const root=document.documentElement;
 const read=()=>{try{const v=localStorage.getItem(KEY);return v==="light"||v==="dark"?v:"dark"}catch(e){return "dark"}};
 const apply=(theme,persist)=>{
  const chosen=theme==="light"?"light":"dark";
  root.dataset.orkiTheme=chosen;
  if(persist){try{localStorage.setItem(KEY,chosen)}catch(e){}}
  for(const button of document.querySelectorAll(".orki-theme-toggle")){
   const light=chosen==="light";
   button.textContent=light?"☾ Oscuro":"☀ Claro";
   button.setAttribute("aria-label",light?"Cambiar a modo oscuro / Switch to dark mode":"Cambiar a modo claro / Switch to light mode");
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
 window.addEventListener("message",e=>{
  if(e.origin!==window.location.origin||!e.data||e.data.type!=="orkilab-theme-request")return;
  apply(read(),false);
 });
 window.OrkiLabTheme={get:()=>root.dataset.orkiTheme,set:theme=>apply(theme,true)};
})();

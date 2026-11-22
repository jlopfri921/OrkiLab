/* Multiview RC1: explain project state and explicitly link saved Dataset Studio photos.
   Never create/modify files, assign speculative angles, or inherit approval silently. */
(function(){
"use strict";
const dictionary={
es:{title:"Estado del proyecto y recuperación de fotografías",loading:"Comprobando las fotografías guardadas…",subjects:"Sujetos multivista",captures:"Fotografías en Multiview",dataset:"Fotografías en Dataset Studio",missing:"Referencias con originales no encontrados",none:"El proyecto todavía no tiene fotografías en Dataset Studio ni en Multiview.",info:"Las fotos guardadas en Dataset Studio no pasan automáticamente a Multiview. Puedes enlazarlas al sujeto que elijas sin duplicar los archivos.",choose:"Sujeto de destino",emptySubject:"Primero crea un sujeto en Multiview Studio.",select:"Selecciona las fotografías",check:"Seleccionar",linked:"Ya enlazada en Multiview",unavailable:"No disponible",review:"Revisión en Dataset Studio",link:"Enlazar fotos seleccionadas",confirm:"¿Enlazar las fotografías seleccionadas a este sujeto? Quedarán pendientes de revisión; los originales no se modificarán.",done:"Referencias incorporadas",skipped:"Ya existentes",error:"No se pudieron recuperar las fotografías.",status:"Estado de la recuperación",limit:"Se muestran las primeras 300 referencias del proyecto.",refresh:"Actualizar diagnóstico",tip:"Si la lista está vacía, añade primero fotografías a Dataset Studio. Si el proyecto no aparece, verifica que sea de categoría Imagen y que no esté archivado.",limit30:"Selecciona un máximo de 30 fotografías cada vez."},
en:{title:"Project health and photo recovery",loading:"Checking saved image references…",subjects:"Multiview subjects",captures:"Multiview photos",dataset:"Dataset Studio photos",missing:"References with missing originals",none:"No photos yet in either Dataset Studio or Multiview.",info:"Photos saved in Dataset Studio are not automatically added to Multiview. Link them explicitly to a subject without duplicating original files.",choose:"Destination subject",emptySubject:"Create a Multiview subject first.",select:"Choose photos",check:"Select",linked:"Already linked in Multiview",unavailable:"Unavailable",review:"Dataset Studio review",link:"Link selected photos",confirm:"Link the selected photos to this subject? They will be unreviewed, and originals will remain unchanged.",done:"References linked",skipped:"Already in subject",error:"Could not retrieve photographs.",status:"Recovery status",limit:"Showing the first 300 project references.",refresh:"Refresh diagnosis",tip:"If there are no photos, import into Dataset Studio first. If the project is missing, check its Image category and archive state.",limit30:"Select up to 30 photos at a time."},
pt:{title:"Estado do projeto e recuperação de fotos",loading:"A verificar imagens…",subjects:"Objetos multivista",captures:"Fotos multivista",dataset:"Fotos Dataset Studio",missing:"Originais em falta",none:"Sem fotos guardadas.",info:"As fotos Dataset Studio são ligadas manualmente, sem duplicar ficheiros.",choose:"Objeto de destino",emptySubject:"Crie um objeto primeiro.",select:"Selecionar fotos",check:"Selecionar",linked:"Já ligada",unavailable:"Indisponível",review:"Revisão",link:"Ligar fotos selecionadas",confirm:"Ligar estas fotos sem alterar os originais?",done:"Referências ligadas",skipped:"Já existentes",error:"Não foi possível recuperar fotos.",status:"Estado",limit:"Primeiras 300 referências.",refresh:"Atualizar",tip:"Importe fotos no Dataset Studio e verifique a categoria Imagem."},
fr:{title:"État du projet et récupération des photos",loading:"Vérification des photos…",subjects:"Sujets multivues",captures:"Photos multivues",dataset:"Photos Dataset Studio",missing:"Originaux manquants",none:"Aucune photo enregistrée.",info:"Liez les photos de Dataset Studio sans dupliquer les originaux.",choose:"Sujet de destination",emptySubject:"Créez un sujet d'abord.",select:"Sélectionner des photos",check:"Choisir",linked:"Déjà liée",unavailable:"Indisponible",review:"Révision",link:"Lier les photos",confirm:"Lier ces photos sans modifier les fichiers?",done:"Références liées",skipped:"Déjà présentes",error:"Récupération impossible.",status:"État",limit:"300 premières références.",refresh:"Actualiser",tip:"Importez d'abord les photos dans Dataset Studio, puis vérifiez le type Image."},
de:{title:"Projektstatus und Fotowiederherstellung",loading:"Gespeicherte Fotos werden geprüft…",subjects:"Multiview-Motive",captures:"Multiview-Fotos",dataset:"Dataset-Studio-Fotos",missing:"Fehlende Originale",none:"Keine Fotos gespeichert.",info:"Dataset-Studio-Fotos werden nur auf Bestätigung verknüpft; Originale bleiben unverändert.",choose:"Zielmotiv",emptySubject:"Zuerst Motiv erstellen.",select:"Fotos wählen",check:"Auswählen",linked:"Bereits verknüpft",unavailable:"Nicht verfügbar",review:"Prüfung",link:"Fotos verknüpfen",confirm:"Fotos verknüpfen ohne Originale zu ändern?",done:"Verknüpft",skipped:"Bereits vorhanden",error:"Fotos können nicht geladen werden.",status:"Status",limit:"Erste 300 Verweise.",refresh:"Aktualisieren",tip:"Zuerst Bilder in Dataset Studio importieren und Projektkategorie Bild prüfen."},
it:{title:"Stato progetto e recupero foto",loading:"Verifica delle foto salvate…",subjects:"Soggetti multivista",captures:"Foto multivista",dataset:"Foto Dataset Studio",missing:"Originali mancanti",none:"Nessuna foto salvata.",info:"Collega le foto di Dataset Studio senza duplicare i file originali.",choose:"Soggetto destinazione",emptySubject:"Crea prima un soggetto.",select:"Scegli foto",check:"Seleziona",linked:"Già collegata",unavailable:"Non disponibile",review:"Revisione",link:"Collega foto",confirm:"Collegare le foto senza modificare gli originali?",done:"Collegate",skipped:"Già presenti",error:"Impossibile recuperare foto.",status:"Stato",limit:"Prime 300 referenze.",refresh:"Aggiorna",tip:"Importa prima in Dataset Studio e controlla la categoria Immagine."},
ja:{title:"プロジェクト状態と写真の連携",loading:"保存済み画像を確認中…",subjects:"マルチビュー対象",captures:"マルチビュー写真",dataset:"Dataset Studio 写真",missing:"元画像なし",none:"写真はまだありません。",info:"元画像を変更せず、Dataset Studio の写真を選択した対象に登録できます。",choose:"登録先",emptySubject:"先に対象を作成してください。",select:"写真の選択",check:"選択",linked:"登録済み",unavailable:"利用不可",review:"確認状態",link:"選択写真を連携",confirm:"元画像を変更せず写真を連携しますか？",done:"連携完了",skipped:"登録済み",error:"写真を読み込めません。",status:"状態",limit:"先頭300件を表示。",refresh:"再確認",tip:"まず Dataset Studio で写真を登録し、画像カテゴリを確認してください。"},
ko:{title:"프로젝트 상태와 사진 연결",loading:"저장된 사진 확인 중…",subjects:"멀티뷰 피사체",captures:"멀티뷰 사진",dataset:"Dataset Studio 사진",missing:"원본 누락",none:"저장된 사진이 없습니다.",info:"원본을 수정하지 않고 Dataset Studio 사진을 선택한 피사체에 연결할 수 있습니다.",choose:"대상 피사체",emptySubject:"먼저 피사체를 만드세요.",select:"사진 선택",check:"선택",linked:"이미 연결됨",unavailable:"사용 불가",review:"검토",link:"선택 항목 연결",confirm:"원본을 변경하지 않고 사진을 연결할까요?",done:"연결됨",skipped:"이미 있음",error:"사진을 불러오지 못했습니다.",status:"상태",limit:"최초 300건 표시.",refresh:"새로고침",tip:"Dataset Studio에 사진을 먼저 추가하고 이미지 범주인지 확인하세요."}
};
const t=k=>(dictionary[(typeof I18N!=="undefined"&&I18N.lang)||"en"]||dictionary.en)[k]||dictionary.en[k]||k;
const el=(tag,txt,cls)=>{const x=document.createElement(tag);if(txt!==undefined)x.textContent=txt;if(cls)x.className=cls;return x};
function mount(host,getProject,getSubjects,api,onLinked){
 const section=el("section",undefined,"mv-recovery-panel");
 const heading=el("h2",t("title")),status=el("p",t("loading"),"muted");
 status.setAttribute("role","status");status.setAttribute("aria-live","polite");
 const refreshButton=el("button",t("refresh"));refreshButton.type="button";
 const stats=el("div",undefined,"mv-recovery-stats"),info=el("p",t("info"),"muted");
 const actions=el("form",undefined,"mv-recovery-actions");
 const subject=el("select");
 const subjectHolder=el("label");subjectHolder.append(el("span",t("choose")),subject);
 const list=el("div",undefined,"mv-recovery-candidates");
 list.setAttribute("role","group");list.setAttribute("aria-label",t("select"));
 const link=el("button",t("link"),"primary");link.type="submit";
 actions.append(subjectHolder,el("h3",t("select")),list,link);
 section.append(heading,refreshButton,status,stats,info,actions,el("p",t("tip"),"muted"));
 host.append(section);
 let lastProject="",ticket=0,entries=[];
 function renderSubjects(){
    const original=subject.value;
    subject.replaceChildren(new Option(t("choose"),""));
    for(const item of getSubjects())subject.add(new Option(item.name,item.id));
    if([...subject.options].some(o=>o.value===original))subject.value=original;
    else if(getSubjects().length===1)subject.value=getSubjects()[0].id;
    link.disabled=!subject.value||!list.querySelector('input[type="checkbox"]:checked');
 }
 function draw(data){
    stats.replaceChildren();
    for(const [key,value] of [["subjects",data.multiview_subjects],["captures",data.multiview_captures],
       ["dataset",data.dataset_images],["missing",data.missing_originals]]){
      const item=el("div",undefined,"mv-recovery-stat");
      item.append(el("small",t(key)),el("strong",String(value)));stats.append(item);
    }
    if(data.dataset_images===0&&data.multiview_captures===0)status.textContent=t("none");
    else status.textContent=t("status")+": "+data.dataset_images+" / "+data.multiview_captures;
    entries=data.candidates||[];
    list.replaceChildren();
    for(const c of entries){
      const label=el("label",undefined,"mv-recovery-candidate");
      const checkbox=el("input");checkbox.type="checkbox";checkbox.value=c.id;
      checkbox.disabled=!c.available;checkbox.setAttribute("aria-label",t("check")+": "+c.name);
      label.append(checkbox,el("span",c.name,"mv-recovery-name"));
      const marker=c.linked?t("linked"):!c.available?t("unavailable"):t("review")+": "+c.review;
      label.append(el("small",marker,"muted"));
      list.append(label);
    }
    if(data.limited)list.append(el("p",t("limit"),"muted"));
    actions.hidden=!entries.length;
    renderSubjects();
 }
 async function refresh(){
   const project=getProject(),n=++ticket;
   if(!project){section.hidden=true;return}
   section.hidden=false;lastProject=project;
   status.textContent=t("loading");
   try{
     const response=await api("/api/workspace/multiview/projects/"+encodeURIComponent(project)+"/recovery");
     if(n!==ticket||project!==getProject()||!host.isConnected)return;
     draw(response);
   }catch(e){if(n===ticket)status.textContent=t("error")+" "+e.message;actions.hidden=true}
 }
 list.addEventListener("change",()=>{link.disabled=!subject.value||!list.querySelector('input[type="checkbox"]:checked')});
 subject.addEventListener("change",()=>{link.disabled=!subject.value||!list.querySelector('input[type="checkbox"]:checked')});
 actions.addEventListener("submit",async event=>{
   event.preventDefault();
   const project=getProject(),selected=[...list.querySelectorAll('input[type="checkbox"]:checked')].map(x=>x.value);
   if(!project||!subject.value||!selected.length)return;
   if(selected.length>30){status.textContent=t("limit30");return}
   if(!window.confirm(t("confirm")))return;
   link.disabled=true;
   try{
     const response=await api("/api/workspace/multiview/projects/"+encodeURIComponent(project)+
       "/subjects/"+encodeURIComponent(subject.value)+"/link-dataset",{
         method:"POST",headers:{"Content-Type":"application/json"},
         body:JSON.stringify({image_ids:selected,confirm:true})
       });
     status.textContent=t("done")+": "+response.linked+" · "+t("skipped")+": "+response.already_linked;
     await onLinked();
   }catch(e){status.textContent=t("error")+" "+e.message}
   finally{await refresh()}
 });
 refreshButton.addEventListener("click",refresh);
 return {refresh,renderSubjects};
}
window.OrkiMultiviewRecovery={mount};
})();
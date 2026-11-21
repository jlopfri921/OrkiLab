/* Multiview 0.5 beta.2: explicit generic archive preparation and download.
 * Never initiates generation/training, never mutates originals, and never
 * treats individual views of the same subject as independent split samples.
 */
(function(){
"use strict";
const tr={
es:{title:"Preparar dataset multivista",intro:"Exporta exclusivamente imágenes aprobadas. Las vistas del mismo sujeto permanecerán juntas en entrenamiento o validación. Las imágenes originales no se modifican.",validation:"Validación (%)",seed:"Semilla del reparto",synthetic:"Incluir imágenes sintéticas aprobadas",preview:"Comprobar y previsualizar",download:"Descargar ZIP",initial:"Configura las opciones y comprueba el dataset antes de descargar.",empty:"No hay imágenes aprobadas que cumplan los filtros.",warning:"Formato de archivo multivista genérico: no implica que todos los entrenadores admitan condicionamiento por varias vistas.",train:"Entrenamiento",valid:"Validación",subjects:"sujetos",photos:"fotografías",real:"reales",generated:"sintéticas",frames:"fotogramas",unknown:"origen desconocido",size:"Tamaño total",ready:"Dataset preparado",confirm:"¿Descargar el archivo multivista? No se modificarán los originales.",wait:"Comprobando integridad de las fotografías…",saving:"Preparando el ZIP y comprobando los hashes…",saved:"Descarga preparada.",fail:"No se pudo preparar el dataset. Revisa las imágenes originales y vuelve a comprobar.",hint:"Una división del 20 % es determinista por sujeto, no garantiza exactamente ese porcentaje con pocos sujetos. Los sujetos completos permanecen en el mismo grupo.",needsPreview:"Previsualiza de nuevo tras modificar las opciones."},
en:{title:"Prepare multiview dataset",intro:"Export approved images only. Views of the same subject always stay together in training or validation. Originals are unchanged.",validation:"Validation (%)",seed:"Split seed",synthetic:"Include approved synthetic images",preview:"Preflight and preview",download:"Download ZIP",initial:"Choose options and preflight the dataset before downloading.",empty:"No approved images match the filters.",warning:"Generic multiview archive: this does not imply that every trainer supports multi-view conditioning.",train:"Training",valid:"Validation",subjects:"subjects",photos:"photographs",real:"real",generated:"synthetic",frames:"video frames",unknown:"unknown origin",size:"Total bytes",ready:"Dataset prepared",confirm:"Download the multiview archive? Source photos remain unchanged.",wait:"Checking image integrity…",saving:"Building ZIP and verifying hashes…",saved:"Download prepared.",fail:"Unable to prepare the archive. Check original image integrity and preflight again.",hint:"A 20% split is deterministic per subject, not guaranteed exact with few subjects. Entire subjects remain together.",needsPreview:"Run preflight again after changing options."},
pt:{title:"Preparar dataset multivista",intro:"Exporta apenas imagens aprovadas. As vistas do mesmo objeto ficam sempre juntas. Os originais não mudam.",validation:"Validação (%)",seed:"Semente",synthetic:"Incluir imagens sintéticas aprovadas",preview:"Verificar",download:"Descarregar ZIP",initial:"Escolha opções e verifique antes de descarregar.",empty:"Nenhuma imagem aprovada.",warning:"Arquivo genérico, sem garantia de suporte multivista por todos os treinadores.",train:"Treino",valid:"Validação",subjects:"objetos",photos:"fotos",real:"reais",generated:"sintéticas",frames:"fotogramas",unknown:"desconhecidas",size:"Tamanho",ready:"Dataset preparado",confirm:"Descarregar sem alterar os originais?",wait:"A verificar integridade…",saving:"A criar ZIP…",saved:"Descarregamento preparado.",fail:"Falha ao preparar o arquivo.",hint:"A divisão por objeto é determinística; com poucos objetos a proporção pode variar.",needsPreview:"Verifique novamente após alterar."},
fr:{title:"Préparer un dataset multivues",intro:"Exportez uniquement les images approuvées. Toutes les vues d'un même sujet restent dans le même ensemble. Sources intactes.",validation:"Validation (%)",seed:"Graine de répartition",synthetic:"Inclure les images synthétiques approuvées",preview:"Vérifier et prévisualiser",download:"Télécharger ZIP",initial:"Choisissez les options avant de télécharger.",empty:"Aucune image approuvée.",warning:"Archive générique : la prise en charge multivues n'est pas garantie pour tous les entraîneurs.",train:"Entraînement",valid:"Validation",subjects:"sujets",photos:"photos",real:"réelles",generated:"synthétiques",frames:"images vidéo",unknown:"inconnues",size:"Taille",ready:"Dataset prêt",confirm:"Télécharger sans modifier les originaux ?",wait:"Vérification de l'intégrité…",saving:"Création du ZIP…",saved:"Téléchargement prêt.",fail:"La préparation a échoué.",hint:"La répartition se fait par sujet; le pourcentage exact dépend du nombre de sujets.",needsPreview:"Vérifiez à nouveau après modification."},
de:{title:"Multiview-Datensatz vorbereiten",intro:"Nur freigegebene Bilder exportieren. Alle Ansichten eines Motivs bleiben zusammen. Originale bleiben unverändert.",validation:"Validierung (%)",seed:"Aufteilungs-Seed",synthetic:"Freigegebene synthetische Bilder einbeziehen",preview:"Prüfen",download:"ZIP herunterladen",initial:"Einstellungen vor dem Download prüfen.",empty:"Keine freigegebenen Bilder.",warning:"Generisches Multiview-Archiv; keine Garantie für Trainer-Kompatibilität.",train:"Training",valid:"Validierung",subjects:"Motive",photos:"Fotos",real:"echte",generated:"synthetische",frames:"Videoframes",unknown:"unbekannt",size:"Größe",ready:"Datensatz bereit",confirm:"ZIP laden, Originale unverändert?",wait:"Integrität wird geprüft…",saving:"ZIP wird erstellt…",saved:"Download bereit.",fail:"Vorbereitung fehlgeschlagen.",hint:"Aufteilung erfolgt nach Motiv, nicht nach Einzelbild.",needsPreview:"Nach Änderungen erneut prüfen."},
it:{title:"Prepara dataset multivista",intro:"Esporta solo immagini approvate. Tutte le viste dello stesso soggetto rimangono insieme. Originali invariati.",validation:"Validazione (%)",seed:"Seed",synthetic:"Includi immagini sintetiche approvate",preview:"Controlla",download:"Scarica ZIP",initial:"Scegli le opzioni prima di scaricare.",empty:"Nessuna immagine approvata.",warning:"Archivio generico: non garantisce supporto multivista in tutti gli allenatori.",train:"Training",valid:"Validazione",subjects:"soggetti",photos:"foto",real:"reali",generated:"sintetiche",frames:"fotogrammi",unknown:"sconosciute",size:"Dimensione",ready:"Dataset pronto",confirm:"Scaricare ZIP senza modificare gli originali?",wait:"Controllo integrità…",saving:"Creazione ZIP…",saved:"Scaricamento pronto.",fail:"Preparazione fallita.",hint:"Le viste dello stesso soggetto non si separano mai.",needsPreview:"Ricontrolla dopo le modifiche."},
ja:{title:"マルチビューデータセットの準備",intro:"承認済み画像のみを出力します。同じ被写体の画像は必ず同じ分割に入ります。元画像は変更しません。",validation:"検証 (%)",seed:"分割シード",synthetic:"承認済み合成画像を含める",preview:"事前確認",download:"ZIP を保存",initial:"設定を選んで確認してください。",empty:"対象となる画像がありません。",warning:"汎用アーカイブです。全トレーナーのマルチビュー対応は保証しません。",train:"学習",valid:"検証",subjects:"被写体",photos:"画像",real:"実写",generated:"合成",frames:"動画フレーム",unknown:"不明",size:"容量",ready:"準備完了",confirm:"元画像を変更せず ZIP を保存しますか？",wait:"画像の整合性を確認中…",saving:"ZIP 作成中…",saved:"ダウンロード準備完了。",fail:"準備できませんでした。",hint:"被写体単位で分割するため割合は近似値です。",needsPreview:"変更後は再確認してください。"},
ko:{title:"멀티뷰 데이터셋 준비",intro:"승인된 이미지만 내보냅니다. 같은 피사체의 모든 시점은 한 분할에 유지됩니다. 원본은 변경되지 않습니다.",validation:"검증 (%)",seed:"분할 시드",synthetic:"승인된 합성 이미지 포함",preview:"사전 검사",download:"ZIP 다운로드",initial:"설정 후 먼저 확인하세요.",empty:"승인된 이미지가 없습니다.",warning:"일반 멀티뷰 아카이브이며 모든 트레이너의 다중 시점 지원을 의미하지 않습니다.",train:"학습",valid:"검증",subjects:"피사체",photos:"사진",real:"실사",generated:"합성",frames:"영상 프레임",unknown:"알 수 없음",size:"크기",ready:"준비됨",confirm:"원본을 변경하지 않고 ZIP을 받을까요?",wait:"사진 무결성 확인 중…",saving:"ZIP 생성 중…",saved:"다운로드 준비됨.",fail:"준비할 수 없습니다.",hint:"같은 피사체는 항상 함께 분할됩니다.",needsPreview:"옵션 변경 후 다시 확인하세요."}
};
const language=()=>typeof I18N!=="undefined"&&tr[I18N.lang]?I18N.lang:"en";
const t=key=>tr[language()][key]||tr.en[key]||key;
const el=(tag,text,css)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(css)e.className=css;return e};
const labeled=(text,control)=>{const label=el("label");label.append(el("span",t(text)),control);return label};
function mount(target,getProject,api){
 const panel=el("section",undefined,"mv-export-panel");
 panel.setAttribute("aria-label",t("title"));
 panel.append(el("h2",t("title")),el("p",t("intro"),"muted"));
 const form=el("form",undefined,"mv-export-form");
 const percent=el("select"),seed=el("input"),synthetic=el("input");
 for(const value of [0,10,20,25,30,40,50])percent.add(new Option(String(value)+"%",value));
 percent.value="20";seed.type="number";seed.min="0";seed.max="2147483647";seed.step="1";seed.value="42";
 synthetic.type="checkbox";
 const toggle=el("label",undefined,"mv-export-toggle");toggle.append(synthetic,el("span",t("synthetic")));
 const preview=el("button",t("preview"),"primary");preview.type="submit";
 const download=el("button",t("download"));download.type="button";download.disabled=true;
 form.append(labeled("validation",percent),labeled("seed",seed),toggle,preview,download);
 const summary=el("p",t("initial"),"muted");summary.setAttribute("role","status");summary.setAttribute("aria-live","polite");
 const detail=el("div",undefined,"mv-export-summary");
 panel.append(form,summary,detail,el("p",t("hint"),"muted"),el("p",t("warning"),"muted"));
 target.append(panel);
 let verified=null,working=false;
 const options=()=>({validation_percent:Number(percent.value),seed:Number(seed.value),
                       include_synthetic:synthetic.checked});
 function reset(){
   verified=null;download.disabled=true;
   summary.textContent=t("needsPreview");detail.replaceChildren();
 }
 for(const input of [percent,seed,synthetic])input.addEventListener("change",reset);
 async function request(mode){
   const project=getProject();
   if(!project)throw Error("Select a project");
   const body={...options(),mode};
   if(mode==="download")body.confirm=true;
   const response=await fetch("/api/workspace/multiview/projects/"+encodeURIComponent(project)+"/export",{
      credentials:"same-origin",cache:"no-store",method:"POST",
      headers:{"Content-Type":"application/json"},body:JSON.stringify(body)
   });
   if(!response.ok){
      const msg=await response.json().catch(()=>({}));
      throw Error(msg.error||t("fail"));
   }
   return response;
 }
 async function runPreview(){
   if(working)return;
   reset();working=true;preview.disabled=true;summary.textContent=t("wait");
   try{
      const response=await request("preview"),value=await response.json();
      const info=value.summary;
      verified={project:getProject(),options:JSON.stringify(options())};
      summary.textContent=info.captures?t("ready"):t("empty");
      const table=el("div",undefined,"mv-export-counts");
      const lines=[
         [t("subjects"),info.subjects],
         [t("photos"),info.captures],
         [t("train"),info.splits.train.subjects+" "+t("subjects")+" / "+info.splits.train.captures+" "+t("photos")],
         [t("valid"),info.splits.validation.subjects+" "+t("subjects")+" / "+info.splits.validation.captures+" "+t("photos")],
         [t("real"),info.source_types.real],
         [t("generated"),info.source_types.synthetic],
         [t("frames"),info.source_types.frames],
         [t("unknown"),info.source_types.unknown],
         [t("size"),(info.total_bytes/1024/1024).toFixed(2)+" MiB"]
      ];
      for(const [key,value] of lines){const card=el("div",undefined,"mv-export-count");
        card.append(el("span",String(key)),el("strong",String(value)));table.append(card)}
      detail.replaceChildren(table);
      download.disabled=!value.ready;
   }catch(e){summary.textContent=e.message;verified=null}
   finally{working=false;preview.disabled=false}
 }
 form.addEventListener("submit",event=>{event.preventDefault();runPreview()});
 download.addEventListener("click",async()=>{
    if(working||!verified||verified.project!==getProject()||
       verified.options!==JSON.stringify(options())){reset();return}
    if(!window.confirm(t("confirm")))return;
    working=true;download.disabled=true;preview.disabled=true;summary.textContent=t("saving");
    try{
       const response=await request("download");
       const archive=await response.blob();
       const blobUrl=URL.createObjectURL(archive);
       const link=el("a");link.href=blobUrl;
       link.download="orkilab-multiview-"+getProject()+".zip";
       document.body.append(link);link.click();link.remove();
       setTimeout(()=>URL.revokeObjectURL(blobUrl),60000);
       summary.textContent=t("saved");
    }catch(e){summary.textContent=e.message||t("fail")}
    finally{working=false;preview.disabled=false;verified=null}
 });
 return {reset};
}
window.OrkiMultiviewExport={mount};
})();
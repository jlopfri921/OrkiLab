/* Multiview alpha.2: presentation-only coverage, review, image comparison.
 * Data are always requested from the project-scoped API. No synthetic angles.
 */
(function () {
 "use strict";
 const $=(tag,cls,text)=>{
   const el=document.createElement(tag);
   if(cls)el.className=cls;
   if(text!==undefined)el.textContent=text;
   return el;
 };
 const dictionary={
 es:{coverage:"Cobertura angular",loading:"Calculando cobertura…",missing:"Sin vistas",provisional:"Provisionales",approved:"Aprobadas",unknown:"Ángulo desconocido",sector:"Sector",photos:"fotos",provisionalTag:"Sin aprobar",approvedTag:"Aprobadas",missingTag:"Pendiente",rejected:"Rechazadas",hint:"Cobertura orientativa de azimut en sectores de 30°. No demuestra visibilidad completa ni reconstrucción 3D.",quality:"Control de calidad",small:"Resolución baja",blurry:"Posible desenfoque",duplicate:"Coincidencias exactas",notAnalyzed:"Sin análisis de nitidez (referencias anteriores)",warning:"Los avisos de nitidez son estimaciones, no rechazos automáticos.",compare:"Comparar fotografías",left:"Imagen izquierda",right:"Imagen derecha",zoom:"Ampliación",close:"Cerrar",review:"Revisión",approve:"Aprobar",reject:"Rechazar",restore:"Sin revisar",angle:"Azimut",noImages:"Añade fotografías para analizar sus perspectivas.",candidates:"Fotografías que revisar",none:"Sin avisos de calidad conocidos.",more:"El comparador muestra hasta 5000 referencias; el resumen utiliza todas.",saveFail:"No se ha podido guardar la revisión",all:"Todas las fotos"},
 en:{coverage:"Angle coverage",loading:"Calculating coverage…",missing:"Missing views",provisional:"Provisional",approved:"Approved",unknown:"Unknown angle",sector:"Sector",photos:"photos",provisionalTag:"Not approved",approvedTag:"Approved",missingTag:"Missing",rejected:"Rejected",hint:"Approximate 30° azimuth sectors only. Does not prove complete visibility or 3D reconstruction.",quality:"Quality checks",small:"Low resolution",blurry:"Possibly blurry",duplicate:"Exact matches",notAnalyzed:"Sharpness not analyzed (older references)",warning:"Blur indications are heuristics, never automatic rejections.",compare:"Compare photographs",left:"Left image",right:"Right image",zoom:"Zoom",close:"Close",review:"Review",approve:"Approve",reject:"Reject",restore:"Unreviewed",angle:"Azimuth",noImages:"Add photographs to analyze viewpoints.",candidates:"Photos needing review",none:"No known quality warnings.",more:"Comparison supports the first 5000 references; totals include all.",saveFail:"Review could not be saved",all:"All photos"},
 pt:{coverage:"Cobertura angular",loading:"A calcular cobertura…",missing:"Vistas em falta",provisional:"Provisórias",approved:"Aprovadas",unknown:"Ângulo desconhecido",sector:"Setor",photos:"fotos",provisionalTag:"Por aprovar",approvedTag:"Aprovadas",missingTag:"Em falta",rejected:"Rejeitadas",hint:"Setores aproximados de azimute de 30°. Não comprovam reconstrução 3D.",quality:"Qualidade",small:"Baixa resolução",blurry:"Possivelmente desfocada",duplicate:"Duplicados exatos",notAnalyzed:"Nitidez não analisada",warning:"A avaliação de nitidez é aproximada.",compare:"Comparar fotos",left:"Imagem esquerda",right:"Imagem direita",zoom:"Zoom",close:"Fechar",review:"Revisão",approve:"Aprovar",reject:"Rejeitar",restore:"Por rever",angle:"Azimute",noImages:"Adicione fotos para analisar perspetivas.",candidates:"Fotos a rever",none:"Sem avisos conhecidos.",more:"Comparação limitada a 5000 referências; contagens completas.",saveFail:"Não foi possível guardar",all:"Todas as fotos"},
 fr:{coverage:"Couverture angulaire",loading:"Calcul de couverture…",missing:"Vues manquantes",provisional:"Provisoires",approved:"Approuvées",unknown:"Angle inconnu",sector:"Secteur",photos:"photos",provisionalTag:"Non approuvées",approvedTag:"Approuvées",missingTag:"Manquant",rejected:"Rejetées",hint:"Secteurs azimutaux de 30° indicatifs, sans garantie de reconstruction 3D.",quality:"Contrôle qualité",small:"Basse résolution",blurry:"Flou possible",duplicate:"Doublons exacts",notAnalyzed:"Netteté non analysée",warning:"Le flou est estimé, pas automatiquement rejeté.",compare:"Comparer les photos",left:"Image gauche",right:"Image droite",zoom:"Zoom",close:"Fermer",review:"Révision",approve:"Approuver",reject:"Rejeter",restore:"À examiner",angle:"Azimut",noImages:"Ajoutez des photos pour analyser les vues.",candidates:"Photos à examiner",none:"Aucune alerte connue.",more:"Comparaison limitée à 5000 références; totaux complets.",saveFail:"Impossible d’enregistrer",all:"Toutes les photos"},
 de:{coverage:"Winkelabdeckung",loading:"Abdeckung wird berechnet…",missing:"Fehlende Ansichten",provisional:"Vorläufig",approved:"Freigegeben",unknown:"Winkel unbekannt",sector:"Sektor",photos:"Fotos",provisionalTag:"Nicht freigegeben",approvedTag:"Freigegeben",missingTag:"Fehlt",rejected:"Abgelehnt",hint:"Nur ungefähre Azimut-Sektoren von 30°. Kein Beleg für 3D-Rekonstruktion.",quality:"Qualitätsprüfung",small:"Niedrige Auflösung",blurry:"Möglicherweise unscharf",duplicate:"Exakte Duplikate",notAnalyzed:"Schärfe nicht geprüft",warning:"Unschärfewarnungen sind nur Schätzungen.",compare:"Fotos vergleichen",left:"Linkes Bild",right:"Rechtes Bild",zoom:"Zoom",close:"Schließen",review:"Prüfung",approve:"Freigeben",reject:"Ablehnen",restore:"Ungeprüft",angle:"Azimut",noImages:"Fügen Sie Fotos zur Winkelanalyse hinzu.",candidates:"Fotos zur Prüfung",none:"Keine bekannten Warnungen.",more:"Vergleich auf 5000 Referenzen begrenzt; Summen vollständig.",saveFail:"Prüfung konnte nicht gespeichert werden",all:"Alle Fotos"},
 it:{coverage:"Copertura angolare",loading:"Calcolo copertura…",missing:"Viste mancanti",provisional:"Provvisorie",approved:"Approvate",unknown:"Angolo sconosciuto",sector:"Settore",photos:"foto",provisionalTag:"Non approvate",approvedTag:"Approvate",missingTag:"Mancante",rejected:"Rifiutate",hint:"Settori azimutali indicativi di 30°, non prova di ricostruzione 3D.",quality:"Qualità",small:"Bassa risoluzione",blurry:"Possibile sfocatura",duplicate:"Duplicati esatti",notAnalyzed:"Nitidezza non analizzata",warning:"Le indicazioni di sfocatura sono stime.",compare:"Confronta foto",left:"Immagine sinistra",right:"Immagine destra",zoom:"Zoom",close:"Chiudi",review:"Revisione",approve:"Approva",reject:"Rifiuta",restore:"Da rivedere",angle:"Azimut",noImages:"Aggiungi foto per analizzare le viste.",candidates:"Foto da esaminare",none:"Nessun avviso noto.",more:"Confronto limitato a 5000 riferimenti; conteggi completi.",saveFail:"Impossibile salvare",all:"Tutte le foto"},
 ja:{coverage:"角度のカバー範囲",loading:"カバー範囲を計算中…",missing:"不足している視点",provisional:"仮登録",approved:"承認済み",unknown:"角度不明",sector:"区画",photos:"枚",provisionalTag:"未承認",approvedTag:"承認済み",missingTag:"不足",rejected:"却下済み",hint:"30度ごとの方位角の目安です。3D再構築を保証しません。",quality:"画質チェック",small:"低解像度",blurry:"ぼけの可能性",duplicate:"完全一致",notAnalyzed:"鮮明度未評価",warning:"ぼけ判定は推定であり自動却下しません。",compare:"写真を比較",left:"左の画像",right:"右の画像",zoom:"拡大",close:"閉じる",review:"確認",approve:"承認",reject:"却下",restore:"未確認",angle:"方位角",noImages:"視点を分析する写真を追加してください。",candidates:"確認が必要な写真",none:"既知の警告なし。",more:"比較は5000件まで、集計は全件対象。",saveFail:"保存できませんでした",all:"すべての写真"},
 ko:{coverage:"각도 범위",loading:"범위 계산 중…",missing:"누락된 시점",provisional:"임시",approved:"승인됨",unknown:"각도 알 수 없음",sector:"구역",photos:"사진",provisionalTag:"미승인",approvedTag:"승인됨",missingTag:"누락",rejected:"거부됨",hint:"30도 방위각 기준의 추정 범위이며 3D 재구성을 보장하지 않습니다.",quality:"품질 검사",small:"낮은 해상도",blurry:"흐릿할 가능성",duplicate:"정확한 중복",notAnalyzed:"선명도 미검사",warning:"흐림 평가는 추정이며 자동 거부하지 않습니다.",compare:"사진 비교",left:"왼쪽 이미지",right:"오른쪽 이미지",zoom:"확대",close:"닫기",review:"검토",approve:"승인",reject:"거부",restore:"미검토",angle:"방위각",noImages:"시점을 분석할 사진을 추가하세요.",candidates:"검토할 사진",none:"알려진 경고가 없습니다.",more:"비교는 5000개까지, 합계는 전체 대상입니다.",saveFail:"검토를 저장하지 못했습니다",all:"모든 사진"}
 };
 const lang=()=>typeof I18N!=="undefined"&&dictionary[I18N.lang]?I18N.lang:"en";
 const tr=key=>dictionary[lang()][key]||dictionary.en[key]||key;
 const captureUrl=(project,id)=>"/api/workspace/multiview/projects/"+encodeURIComponent(project)+"/captures/"+encodeURIComponent(id)+"/preview";
 function mount(target,getProject,subjectId,request,report) {
    let generation=0,reportData=null;
    const region=$("section","mv-coverage-panel");
    region.setAttribute("aria-label",tr("coverage"));
    const heading=$("h2",null,tr("coverage"));
    const summary=$("p","muted",tr("loading"));
    const layout=$("div","mv-coverage-layout");
    const wheel=$("div","mv-coverage-wheel");
    wheel.setAttribute("role","group");
    wheel.setAttribute("aria-label",tr("coverage"));
    const center=$("div","mv-wheel-center");
    const centerScore=$("strong",null,"—");
    center.append(centerScore,$("small",null,tr("coverage")));
    wheel.append(center);
    const aside=$("div","mv-coverage-aside");
    const unknown=$("p","muted");
    const missing=$("p","muted");
    const sectorDetail=$("p","muted");
    const hint=$("p","muted",tr("hint"));
    aside.append(unknown,missing,sectorDetail,hint);
    layout.append(wheel,aside);
    const qualityTitle=$("h2",null,tr("quality"));
    const quality=$("p","muted");
    const warnings=$("div","mv-quality-warning");
    const qualityNote=$("p","muted",tr("warning"));
    const compareTitle=$("h2",null,tr("compare"));
    const compareRow=$("div","row mv-comparison-controls");
    const pairA=$("select"),pairB=$("select");
    for (const [sel,title] of [[pairA,tr("left")],[pairB,tr("right")]]) {
       const label=$("label");label.append($("span",null,title),sel);compareRow.append(label);
    }
    const compareButton=$("button","primary",tr("compare"));compareButton.type="button";
    compareRow.append(compareButton);
    const dialog=$("dialog","mv-compare-dialog");
    dialog.setAttribute("aria-label",tr("compare"));
    const top=$("div","mv-compare-top");
    const dialogTitle=$("h2",null,tr("compare"));
    const close=$("button",null,tr("close"));close.type="button";
    top.append(dialogTitle,close);
    const zoomLabel=$("label","mv-compare-zoom");
    const range=$("input");range.type="range";range.min="100";range.max="250";range.step="25";range.value="100";
    const zoomText=$("output",null,"100%");
    zoomLabel.append($("span",null,tr("zoom")),range,zoomText);
    const images=$("div","mv-compare-images");
    const photoA=$("img"),photoB=$("img");
    photoA.alt=tr("left");photoB.alt=tr("right");
    images.append(photoA,photoB);
    dialog.append(top,zoomLabel,images);
    region.append(heading,summary,layout,qualityTitle,quality,warnings,qualityNote,
                  compareTitle,compareRow,dialog);
    target.append(region);
    close.addEventListener("click",()=>dialog.close());
    dialog.addEventListener("close",()=>{photoA.removeAttribute("src");photoB.removeAttribute("src")});
    range.addEventListener("input",()=>{
       const size=Number(range.value);
       zoomText.textContent=size+"%";
       photoA.style.transform=photoB.style.transform="scale("+(size/100)+")";
    });
    compareButton.addEventListener("click",()=>{
       if(!reportData||!pairA.value||!pairB.value)return;
       const project=getProject();
       const a=reportData.captures.find(x=>x.id===pairA.value);
       const b=reportData.captures.find(x=>x.id===pairB.value);
       if(!a||!b)return;
       photoA.src=captureUrl(project,a.id);
       photoB.src=captureUrl(project,b.id);
       photoA.alt=a.name;photoB.alt=b.name;
       range.value="100";range.dispatchEvent(new Event("input"));
       dialog.showModal();
    });
    async function setReview(capture,status) {
       try {
         const project=getProject();
         await request("/api/workspace/multiview/projects/"+encodeURIComponent(project)+
             "/captures/"+encodeURIComponent(capture.id),{
           method:"PATCH",headers:{"Content-Type":"application/json"},
           body:JSON.stringify({review:status})
         });
         await refresh();
         document.dispatchEvent(new CustomEvent("orkilab:multiview-review-updated",{
           detail:{project,subjectId}
         }));
       } catch (error) {report(tr("saveFail")+": "+error.message)}
    }
    function draw(data) {
       reportData=data;
       summary.textContent=tr("approved")+": "+data.approved_coverage_percent+"% · "+
         tr("provisional")+": "+data.coverage_percent+"% · "+data.total+" "+tr("photos");
       centerScore.textContent=data.coverage_percent+"%";
       for(const item of wheel.querySelectorAll(".mv-sector-button"))item.remove();
       const gradients=data.sectors.map(b=>b.approved?"#0f766e":b.count?"#2b78a5":"#584352");
       wheel.style.background="conic-gradient(from -15deg,"+
         gradients.map((c,i)=>c+" "+i*30+"deg "+(i+1)*30+"deg").join(",")+")";
       for(const sector of data.sectors){
          const angle=sector.center_deg*Math.PI/180;
          const btn=$("button","mv-sector-button",String(sector.center_deg)+"°");
          btn.type="button";
          btn.style.left=(50+40*Math.sin(angle))+"%";
          btn.style.top=(50-40*Math.cos(angle))+"%";
          const state=sector.approved?tr("approvedTag"):
               sector.count?tr("provisionalTag"):tr("missingTag");
          btn.setAttribute("aria-label",tr("sector")+" "+sector.center_deg+"°: "+
               state+", "+sector.count+" "+tr("photos"));
          btn.title=btn.getAttribute("aria-label");
          btn.addEventListener("click",()=>{
             for(const element of wheel.querySelectorAll(".mv-sector-button"))
                element.removeAttribute("aria-pressed");
             btn.setAttribute("aria-pressed","true");
             sectorDetail.textContent=btn.getAttribute("aria-label");
             const associated=data.captures.filter(c=>c.sector_center_deg===sector.center_deg&&c.review!=="rejected");
             if(associated.length) {
                const first=associated[0];
                pairA.value=first.id;
             }
          });
          wheel.append(btn);
       }
       unknown.textContent=tr("unknown")+": "+data.unknown_angles;
       missing.textContent=tr("missing")+": "+(data.missing_sectors.length ?
           data.missing_sectors.map(a=>a+"°").join(" · "):"0");
       sectorDetail.textContent=tr("hint");
       const q=data.quality;
       quality.textContent=[
           tr("small")+": "+q.low_resolution,
           tr("blurry")+": "+q.possibly_blurry,
           tr("duplicate")+": "+q.exact_duplicate_captures,
           tr("notAnalyzed")+": "+q.sharpness_unavailable,
           tr("rejected")+": "+data.reviews.rejected
       ].join(" · ");
       warnings.replaceChildren();
       const candidates=data.captures.filter(c=>c.low_resolution||c.possibly_blurry||c.exact_duplicate);
       if(!candidates.length)warnings.append($("p","muted",tr("none")));
       else {
         warnings.append($("strong",null,tr("candidates")));
         const list=$("div","mv-quality-candidates");
         for(const c of candidates.slice(0,40)){
             const item=$("div","mv-quality-item");
             const reasons=[];
             if(c.low_resolution)reasons.push(tr("small"));
             if(c.possibly_blurry)reasons.push(tr("blurry"));
             if(c.exact_duplicate)reasons.push(tr("duplicate"));
             const title=$("div",null,c.name+" · "+reasons.join(", "));
             const actions=$("div","mv-review-actions");
             for(const [status,key] of [["approved","approve"],["rejected","reject"],["unreviewed","restore"]]){
                const btn=$("button",null,tr(key));btn.type="button";
                if(c.review===status){btn.disabled=true;btn.setAttribute("aria-current","true")}
                btn.addEventListener("click",()=>setReview(c,status));
                actions.append(btn);
             }
             item.append(title,actions);list.append(item);
         }
         warnings.append(list);
       }
       pairA.replaceChildren();pairB.replaceChildren();
       const options=data.captures;
       for(const c of options){
           pairA.add(new Option(c.name+" · "+(c.azimuth_deg===null?tr("unknown"):c.azimuth_deg+"°"),c.id));
           pairB.add(new Option(c.name+" · "+(c.azimuth_deg===null?tr("unknown"):c.azimuth_deg+"°"),c.id));
       }
       pairA.disabled=pairB.disabled=compareButton.disabled=options.length<2;
       if(options.length>=2)pairB.selectedIndex=1;
       if(data.limited)warnings.append($("p","muted",tr("more")));
    }
    async function refresh() {
       const ticket=++generation,project=getProject();
       if(!project)return;
       try {
          const value=await request("/api/workspace/multiview/projects/"+
                  encodeURIComponent(project)+"/subjects/"+
                  encodeURIComponent(subjectId)+"/coverage");
          if(ticket!==generation||project!==getProject()||!target.isConnected)return;
          draw(value);
       } catch (error) {
          if(ticket===generation)summary.textContent=error.message;
       }
    }
    return {refresh};
 }
 window.OrkiMultiviewCoverage={mount};
})();

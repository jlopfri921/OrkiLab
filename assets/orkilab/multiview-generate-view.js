/* Multiview requested-view generator. Reuses OrkiLab's validated ComfyUI job API. */
(function(){
"use strict";
const words={
 es:{send:"Enviar fotos seleccionadas a ComfyUI/input",mappingMode:"Asignación de fotos",auto:"Automática (propuesta, revisable)",semi:"Semiautomática (elegir cada nodo)",uploadedHeading:"Copias enviadas al input de ComfyUI",confirmMapping:"Confirmar la asignación antes de generar",notUploaded:"Ninguna foto enviada todavía",uploadedStatus:"Se enviaron {count} fotografías a ComfyUI/input. Revisa el destino de cada una.",chooseNode:"Selecciona un nodo LoadImage para cada fotografía.",unknown:"Desconocida",requestedLabel:"Vista solicitada (sintética, NO medida): ",max4:"Selecciona un máximo de cuatro fotografías de referencia.",title:"Generar vista faltante",intro:"Selecciona fotografías reales, asigna cada una a una entrada de imagen del workflow y solicita una vista. El workflow debe aceptar referencias: un modelo de texto a imagen no garantiza conservar el sujeto.",photos:"Fotografías de referencia (1–4)",workflow:"Workflow ComfyUI compatible",refresh:"Actualizar referencias y workflows",direction:"Vista solicitada",height:"Altura de cámara",distance:"Distancia aparente",extra:"Indicaciones adicionales (opcional)",stage:"Preparar fotos y workflow",mapping:"Asignación de imágenes a nodos LoadImage",prompt:"Campo de texto editable",run:"Generar nueva vista",cancel:"Cancelar generación",pending:"Selecciona fotos reales y un workflow compatible antes de continuar.",noRefs:"Vincula primero fotografías reales al sujeto.",noWorkflow:"Importa primero un workflow de imagen con nodos LoadImage conectados desde Zona ComfyUI.",badNodes:"El workflow necesita al menos una entrada LoadImage editable por cada foto elegida; selecciona menos fotos u otro workflow.",badPrompt:"Elige una entrada de texto editable; el workflow no tiene campos adecuados.",ready:"Las referencias se han copiado a ComfyUI/input. Configura las asignaciones y confirma para generar.",running:"Generando en ComfyUI…",finished:"Generación terminada. Revisa la imagen antes de incorporarla.",register:"Incorporar como sintética pendiente de revisión",saved:"Imagen sintética vinculada con su vista solicitada; los grados siguen desconocidos.",note:"Los modelos pueden inventar partes ocultas. Las copias subidas a ComfyUI/input no se eliminan automáticamente; tus originales siguen intactos.",confirmStage:"¿Copiar estas fotos a la carpeta input del ComfyUI configurado? Aún no se generará nada.",confirmRun:"¿Ejecutar este workflow con las fotos y la vista indicadas?",confirmImport:"¿Registrar esta imagen sintética en el sujeto sin aprobarla?",front:"Frontal",front_right:"Frontal derecha",right:"Derecha",back_right:"Trasera derecha",back:"Trasera",back_left:"Trasera izquierda",left:"Izquierda",front_left:"Frontal izquierda",top:"Superior",bottom:"Inferior",above:"Desde arriba",level:"A nivel",below:"Desde abajo",close:"Cerca",medium:"Media",far:"Lejos",none:"No modificar",stop:"Trabajo cancelado",mismatch:"Cambió el proyecto; la operación no se ha continuado."},
 en:{send:"Send selected photos to ComfyUI/input",mappingMode:"Photo mapping",auto:"Automatic (suggested, editable)",semi:"Semi-automatic (choose each node)",uploadedHeading:"Copies sent to ComfyUI input",confirmMapping:"Confirm mapping before generation",notUploaded:"No photos transferred yet",uploadedStatus:"Uploaded {count} photos to ComfyUI/input. Review every mapping.",chooseNode:"Select a LoadImage node for each photo.",unknown:"Unknown",requestedLabel:"Requested viewpoint (synthetic, NOT measured): ",max4:"Select up to four reference photographs.",title:"Generate missing viewpoint",intro:"Select real photographs, map each to an image input in a reference-capable workflow, and request a view. Text-to-image models cannot guarantee subject fidelity.",photos:"Reference photos (1–4)",workflow:"Compatible ComfyUI workflow",refresh:"Refresh references and workflows",direction:"Requested view",height:"Camera height",distance:"Apparent distance",extra:"Extra instructions (optional)",stage:"Stage photos and prepare workflow",mapping:"Map images to LoadImage nodes",prompt:"Editable text input",run:"Generate new view",cancel:"Cancel generation",pending:"Select real photos and a compatible workflow to continue.",noRefs:"Link real photos to this subject first.",noWorkflow:"Import an image workflow with connected LoadImage nodes in ComfyUI Zone.",badNodes:"Workflow needs an editable LoadImage input for each selected photo; select fewer photos or another workflow.",badPrompt:"Choose an editable prompt input; no compatible field found.",ready:"Reference copies are now in ComfyUI/input. Map them and confirm to generate.",running:"Generating with ComfyUI…",finished:"Generation completed. Review before importing.",register:"Register as synthetic and unreviewed",saved:"Synthetic image linked with its requested view; measured degrees remain unknown.",note:"Models can hallucinate hidden details. Copies staged in ComfyUI/input are not automatically removed; your originals remain intact.",confirmStage:"Copy these photos into the configured ComfyUI input folder? No generation yet.",confirmRun:"Execute the workflow with these references and requested view?",confirmImport:"Import this result as an unreviewed synthetic image?",front:"Front",front_right:"Front right",right:"Right",back_right:"Back right",back:"Back",back_left:"Back left",left:"Left",front_left:"Front left",top:"Top",bottom:"Bottom",above:"Above",level:"Level",below:"Below",close:"Close",medium:"Medium",far:"Far",none:"Do not change",stop:"Job cancelled",mismatch:"Project changed; operation stopped."},
 pt:{send:"Enviar fotos selecionadas para ComfyUI/input",mappingMode:"Associação das fotografias",auto:"Automática (sugerida, editável)",semi:"Semiautomática (escolher cada nó)",uploadedHeading:"Cópias enviadas para ComfyUI/input",confirmMapping:"Confirmar associação antes de gerar",notUploaded:"Nenhuma foto enviada ainda",uploadedStatus:"Foram enviadas {count} fotos para ComfyUI/input. Confirme as associações.",chooseNode:"Escolha um nó LoadImage para cada fotografia.",unknown:"Desconhecida",requestedLabel:"Vista solicitada (sintética, NÃO medida): ",max4:"Selecione no máximo quatro fotografias de referência.",title:"Gerar vista em falta",intro:"Selecione fotografias reais, associe-as a entradas de imagem de um workflow compatível com referências e peça uma nova vista. Modelos só de texto não garantem a fidelidade do sujeito.",photos:"Fotos de referência (1–4)",workflow:"Workflow ComfyUI compatível",refresh:"Atualizar referências e workflows",direction:"Vista pretendida",height:"Altura da câmara",distance:"Distância aparente",extra:"Instruções adicionais (opcional)",stage:"Preparar fotos e workflow",mapping:"Associar imagens aos nós LoadImage",prompt:"Campo de texto editável",run:"Gerar nova vista",cancel:"Cancelar geração",pending:"Selecione fotos reais e um workflow compatível para continuar.",noRefs:"Primeiro associe fotos reais a este sujeito.",noWorkflow:"Importe um workflow de imagem com nós LoadImage ligados na Zona ComfyUI.",badNodes:"É necessária uma entrada LoadImage editável por foto selecionada; escolha menos fotos ou outro workflow.",badPrompt:"Escolha um campo de prompt editável; não foi encontrado nenhum compatível.",ready:"As cópias foram colocadas em ComfyUI/input. Confirme as associações antes de gerar.",running:"A gerar no ComfyUI…",finished:"Geração concluída. Reveja antes de importar.",register:"Registar como sintética e não revista",saved:"Imagem sintética associada à vista solicitada; os graus medidos continuam desconhecidos.",note:"Os modelos podem inventar detalhes ocultos. As cópias em ComfyUI/input não são eliminadas automaticamente; os originais mantêm-se intactos.",confirmStage:"Copiar estas fotos para a pasta input do ComfyUI configurado? Ainda não será gerada nenhuma imagem.",confirmRun:"Executar este workflow com as referências e a vista solicitada?",confirmImport:"Importar este resultado como imagem sintética não revista?",front:"Frontal",front_right:"Frontal direita",right:"Direita",back_right:"Traseira direita",back:"Traseira",back_left:"Traseira esquerda",left:"Esquerda",front_left:"Frontal esquerda",top:"Superior",bottom:"Inferior",above:"De cima",level:"Ao nível",below:"De baixo",close:"Perto",medium:"Média",far:"Longe",none:"Não modificar",stop:"Trabalho cancelado",mismatch:"O projeto mudou; a operação foi interrompida."},
 fr:{send:"Envoyer les photos sélectionnées vers ComfyUI/input",mappingMode:"Association des photos",auto:"Automatique (proposée, modifiable)",semi:"Semi-automatique (choisir chaque nœud)",uploadedHeading:"Copies transférées vers ComfyUI/input",confirmMapping:"Confirmer les associations avant génération",notUploaded:"Aucune photo transférée",uploadedStatus:"{count} photos envoyées vers ComfyUI/input. Vérifiez les associations.",chooseNode:"Choisissez un nœud LoadImage pour chaque photo.",unknown:"Inconnue",requestedLabel:"Vue demandée (synthétique, NON mesurée) : ",max4:"Sélectionnez au maximum quatre photos de référence.",title:"Générer une vue manquante",intro:"Choisissez des photos réelles, associez-les aux entrées d'image d'un workflow prenant en charge les références et demandez une vue. Un modèle texte-image ne garantit pas la fidélité au sujet.",photos:"Photos de référence (1–4)",workflow:"Workflow ComfyUI compatible",refresh:"Actualiser les références et workflows",direction:"Vue demandée",height:"Hauteur de caméra",distance:"Distance apparente",extra:"Instructions supplémentaires (facultatif)",stage:"Préparer les photos et le workflow",mapping:"Associer les images aux nœuds LoadImage",prompt:"Champ de texte modifiable",run:"Générer une nouvelle vue",cancel:"Annuler la génération",pending:"Sélectionnez des photos réelles et un workflow compatible pour continuer.",noRefs:"Associez d'abord des photos réelles à ce sujet.",noWorkflow:"Importez un workflow d'image avec des nœuds LoadImage connectés depuis la Zone ComfyUI.",badNodes:"Le workflow exige une entrée LoadImage modifiable par photo choisie ; choisissez moins de photos ou un autre workflow.",badPrompt:"Choisissez un champ de prompt modifiable ; aucun champ compatible trouvé.",ready:"Les copies sont dans ComfyUI/input. Vérifiez les associations avant de générer.",running:"Génération dans ComfyUI…",finished:"Génération terminée. Vérifiez avant d'importer.",register:"Enregistrer comme synthétique et non vérifiée",saved:"Image synthétique associée à la vue demandée ; aucun angle mesuré ajouté.",note:"Les modèles peuvent inventer des détails cachés. Les copies de ComfyUI/input ne sont pas supprimées automatiquement ; vos originaux restent intacts.",confirmStage:"Copier ces photos vers le dossier input de ComfyUI ? Aucune génération pour l'instant.",confirmRun:"Exécuter ce workflow avec ces références et cette vue ?",confirmImport:"Importer ce résultat comme image synthétique non vérifiée ?",front:"Face",front_right:"Avant droite",right:"Droite",back_right:"Arrière droite",back:"Arrière",back_left:"Arrière gauche",left:"Gauche",front_left:"Avant gauche",top:"Dessus",bottom:"Dessous",above:"D'en haut",level:"À hauteur",below:"D'en bas",close:"Proche",medium:"Moyenne",far:"Loin",none:"Ne pas modifier",stop:"Tâche annulée",mismatch:"Le projet a changé ; opération interrompue."},
 de:{send:"Ausgewählte Fotos nach ComfyUI/input senden",mappingMode:"Fotozuordnung",auto:"Automatisch (Vorschlag, bearbeitbar)",semi:"Halbautomatisch (Knoten auswählen)",uploadedHeading:"Kopien in ComfyUI/input",confirmMapping:"Zuordnung vor Erzeugung bestätigen",notUploaded:"Noch keine Fotos übertragen",uploadedStatus:"{count} Fotos nach ComfyUI/input übertragen. Prüfen Sie die Zuordnung.",chooseNode:"Wählen Sie für jedes Foto einen LoadImage-Knoten.",unknown:"Unbekannt",requestedLabel:"Gewünschte Ansicht (synthetisch, NICHT gemessen): ",max4:"Wählen Sie höchstens vier Referenzfotos.",title:"Fehlende Ansicht erzeugen",intro:"Wählen Sie echte Referenzfotos aus und ordnen Sie diese den Bildeingängen eines geeigneten Workflows zu. Reine Text-zu-Bild-Modelle garantieren keine Motivtreue.",photos:"Referenzfotos (1–4)",workflow:"Kompatibler ComfyUI-Workflow",refresh:"Referenzen und Workflows aktualisieren",direction:"Gewünschte Ansicht",height:"Kamerahöhe",distance:"Scheinbare Entfernung",extra:"Zusätzliche Anweisungen (optional)",stage:"Fotos und Workflow vorbereiten",mapping:"Bilder LoadImage-Knoten zuordnen",prompt:"Bearbeitbares Textfeld",run:"Neue Ansicht erzeugen",cancel:"Erzeugung abbrechen",pending:"Wählen Sie echte Fotos und einen kompatiblen Workflow aus.",noRefs:"Verknüpfen Sie zuerst echte Fotos mit diesem Motiv.",noWorkflow:"Importieren Sie einen Bild-Workflow mit verbundenen LoadImage-Knoten aus der ComfyUI-Zone.",badNodes:"Pro Foto wird ein bearbeitbarer LoadImage-Eingang benötigt; weniger Fotos oder anderen Workflow wählen.",badPrompt:"Wählen Sie einen bearbeitbaren Prompt-Eingang; kein kompatibles Feld gefunden.",ready:"Kopien liegen in ComfyUI/input. Prüfen Sie die Zuordnung vor dem Start.",running:"Erzeugung in ComfyUI läuft…",finished:"Erzeugung abgeschlossen. Vor dem Import prüfen.",register:"Als synthetisch und ungeprüft registrieren",saved:"Synthetisches Bild mit gewünschter Ansicht verknüpft; gemessene Winkel bleiben unbekannt.",note:"Modelle können verdeckte Details erfinden. Kopien in ComfyUI/input werden nicht automatisch gelöscht; Originale bleiben unverändert.",confirmStage:"Diese Fotos nach ComfyUI/input kopieren? Noch keine Erzeugung.",confirmRun:"Diesen Workflow mit den Referenzen und der gewünschten Ansicht ausführen?",confirmImport:"Dieses Ergebnis als ungeprüftes synthetisches Bild importieren?",front:"Vorne",front_right:"Vorne rechts",right:"Rechts",back_right:"Hinten rechts",back:"Hinten",back_left:"Hinten links",left:"Links",front_left:"Vorne links",top:"Oben",bottom:"Unten",above:"Von oben",level:"Auf gleicher Höhe",below:"Von unten",close:"Nah",medium:"Mittel",far:"Fern",none:"Nicht ändern",stop:"Auftrag abgebrochen",mismatch:"Projekt gewechselt; Vorgang gestoppt."},
 it:{send:"Invia le foto selezionate a ComfyUI/input",mappingMode:"Assegnazione delle foto",auto:"Automatica (suggerita, modificabile)",semi:"Semiautomatica (scegli ogni nodo)",uploadedHeading:"Copie inviate a ComfyUI/input",confirmMapping:"Conferma le assegnazioni prima di generare",notUploaded:"Nessuna foto inviata",uploadedStatus:"{count} foto inviate a ComfyUI/input. Verifica ogni assegnazione.",chooseNode:"Seleziona un nodo LoadImage per ogni foto.",unknown:"Sconosciuta",requestedLabel:"Vista richiesta (sintetica, NON misurata): ",max4:"Seleziona al massimo quattro foto di riferimento.",title:"Genera vista mancante",intro:"Seleziona foto reali, assegnale agli ingressi immagine di un workflow compatibile con riferimenti e richiedi una vista. I modelli testo-immagine non garantiscono la fedeltà al soggetto.",photos:"Foto di riferimento (1–4)",workflow:"Workflow ComfyUI compatibile",refresh:"Aggiorna riferimenti e workflow",direction:"Vista richiesta",height:"Altezza camera",distance:"Distanza apparente",extra:"Istruzioni aggiuntive (facoltative)",stage:"Prepara foto e workflow",mapping:"Assegna immagini ai nodi LoadImage",prompt:"Campo di testo modificabile",run:"Genera nuova vista",cancel:"Annulla generazione",pending:"Seleziona foto reali e un workflow compatibile per continuare.",noRefs:"Prima collega foto reali al soggetto.",noWorkflow:"Importa un workflow immagini con nodi LoadImage collegati nella Zona ComfyUI.",badNodes:"Serve un ingresso LoadImage modificabile per ciascuna foto; scegli meno foto o un altro workflow.",badPrompt:"Scegli un campo prompt modificabile; nessuno compatibile trovato.",ready:"Le copie sono in ComfyUI/input. Controlla le associazioni prima di generare.",running:"Generazione in ComfyUI…",finished:"Generazione completata. Controlla prima di importare.",register:"Registra come sintetica e non revisionata",saved:"Immagine sintetica collegata alla vista richiesta; i gradi misurati restano sconosciuti.",note:"I modelli possono inventare dettagli nascosti. Le copie in ComfyUI/input non vengono rimosse automaticamente; gli originali restano intatti.",confirmStage:"Copiare queste foto nella cartella input di ComfyUI? Nessuna generazione ancora.",confirmRun:"Eseguire questo workflow con questi riferimenti e questa vista?",confirmImport:"Importare questo risultato come immagine sintetica non revisionata?",front:"Frontale",front_right:"Anteriore destra",right:"Destra",back_right:"Posteriore destra",back:"Posteriore",back_left:"Posteriore sinistra",left:"Sinistra",front_left:"Anteriore sinistra",top:"Superiore",bottom:"Inferiore",above:"Dall'alto",level:"All'altezza",below:"Dal basso",close:"Vicino",medium:"Media",far:"Lontano",none:"Non modificare",stop:"Lavoro annullato",mismatch:"Il progetto è cambiato; operazione interrotta."},
 ja:{send:"選択した写真をComfyUI/inputに送信",mappingMode:"写真の割り当て",auto:"自動（提案・編集可能）",semi:"半自動（ノードを手動選択）",uploadedHeading:"ComfyUI/inputへコピー済み",confirmMapping:"生成前に割り当てを確認",notUploaded:"写真はまだ送信されていません",uploadedStatus:"{count}枚の写真をComfyUI/inputに送信しました。割り当てを確認してください。",chooseNode:"写真ごとにLoadImageノードを選択してください。",unknown:"不明",requestedLabel:"要求した視点（合成・測定値ではありません）：",max4:"参照写真は最大4枚まで選択できます。",title:"不足視点を生成",intro:"実写の参照写真を選び、参照画像に対応するワークフローの画像入力に割り当てて視点を指定します。テキスト画像生成だけでは被写体の同一性を保証できません。",photos:"参照写真 (1～4枚)",workflow:"対応するComfyUIワークフロー",refresh:"参照写真とワークフローを更新",direction:"生成したい視点",height:"カメラの高さ",distance:"見かけの距離",extra:"追加指示（任意）",stage:"写真とワークフローを準備",mapping:"LoadImageノードへ画像を割り当て",prompt:"編集可能なテキスト入力",run:"新しい視点を生成",cancel:"生成をキャンセル",pending:"実写写真と対応するワークフローを選んでください。",noRefs:"先に実写写真を被写体に関連付けてください。",noWorkflow:"ComfyUIゾーンで接続済みのLoadImageノードを持つ画像ワークフローを読み込んでください。",badNodes:"各写真に編集可能なLoadImage入力が必要です。写真を減らすか別のワークフローを選んでください。",badPrompt:"編集可能なプロンプト入力が見つかりません。",ready:"写真のコピーをComfyUI/inputに保存しました。割り当てを確認して生成してください。",running:"ComfyUIで生成中…",finished:"生成が完了しました。取り込む前に確認してください。",register:"合成画像・未レビューとして登録",saved:"指定した視点と合成画像を関連付けました。測定角度は不明のままです。",note:"モデルが見えない部分を創作する場合があります。ComfyUI/inputのコピーは自動削除されず、元のファイルは変更されません。",confirmStage:"これらの写真をComfyUIのinputフォルダーにコピーしますか？まだ生成しません。",confirmRun:"参照写真と指定視点でワークフローを実行しますか？",confirmImport:"この結果を未レビューの合成画像として取り込みますか？",front:"正面",front_right:"右前",right:"右側",back_right:"右後",back:"背面",back_left:"左後",left:"左側",front_left:"左前",top:"上面",bottom:"下面",above:"上から",level:"同じ高さ",below:"下から",close:"近い",medium:"中程度",far:"遠い",none:"変更しない",stop:"ジョブをキャンセルしました",mismatch:"プロジェクトが変更されたため処理を中断しました。"},
 ko:{send:"선택한 사진을 ComfyUI/input으로 전송",mappingMode:"사진 연결 방식",auto:"자동(추천·수정 가능)",semi:"반자동(노드 직접 선택)",uploadedHeading:"ComfyUI/input에 사본 전송됨",confirmMapping:"생성 전 연결 확인",notUploaded:"아직 전송된 사진이 없습니다",uploadedStatus:"{count}장의 사진을 ComfyUI/input으로 전송했습니다. 연결을 확인하세요.",chooseNode:"사진마다 LoadImage 노드를 선택하세요.",unknown:"알 수 없음",requestedLabel:"요청 시점(합성·측정값 아님): ",max4:"참조 사진은 최대 4장까지 선택할 수 있습니다.",title:"누락된 시점 생성",intro:"실제 참조 사진을 선택하고 참조 이미지를 지원하는 워크플로의 이미지 입력에 연결한 뒤 시점을 지정하세요. 텍스트 이미지 생성 모델은 피사체의 동일성을 보장하지 않습니다.",photos:"참조 사진(1~4장)",workflow:"호환 ComfyUI 워크플로",refresh:"참조 및 워크플로 새로고침",direction:"요청 시점",height:"카메라 높이",distance:"겉보기 거리",extra:"추가 지시(선택)",stage:"사진 및 워크플로 준비",mapping:"LoadImage 노드에 이미지 연결",prompt:"수정 가능한 텍스트 입력",run:"새 시점 생성",cancel:"생성 취소",pending:"실제 사진과 호환 워크플로를 선택하세요.",noRefs:"먼저 피사체에 실제 사진을 연결하세요.",noWorkflow:"ComfyUI 영역에서 연결된 LoadImage 노드가 있는 이미지 워크플로를 가져오세요.",badNodes:"선택한 사진마다 편집 가능한 LoadImage 입력이 필요합니다. 사진 수를 줄이거나 다른 워크플로를 선택하세요.",badPrompt:"수정 가능한 프롬프트 입력이 없습니다.",ready:"사진 사본을 ComfyUI/input에 저장했습니다. 연결을 확인하고 생성하세요.",running:"ComfyUI에서 생성 중…",finished:"생성이 끝났습니다. 가져오기 전에 확인하세요.",register:"합성·미검토 이미지로 등록",saved:"합성 이미지를 요청 시점에 연결했습니다. 측정 각도는 알 수 없는 상태로 유지됩니다.",note:"모델은 보이지 않는 부분을 만들어 낼 수 있습니다. ComfyUI/input 사본은 자동 삭제되지 않으며 원본은 그대로 유지됩니다.",confirmStage:"이 사진을 ComfyUI의 input 폴더에 복사할까요? 아직 생성하지 않습니다.",confirmRun:"이 참조 사진과 요청 시점으로 워크플로를 실행할까요?",confirmImport:"이 결과를 미검토 합성 이미지로 가져올까요?",front:"정면",front_right:"오른쪽 앞",right:"오른쪽",back_right:"오른쪽 뒤",back:"뒷면",back_left:"왼쪽 뒤",left:"왼쪽",front_left:"왼쪽 앞",top:"위쪽",bottom:"아래쪽",above:"위에서",level:"같은 높이",below:"아래에서",close:"가까움",medium:"중간",far:"멀리",none:"변경하지 않음",stop:"작업 취소됨",mismatch:"프로젝트가 변경되어 작업을 중단했습니다."}
};
const directions=["front","front_right","right","back_right","back","back_left","left","front_left","top","bottom"];
const elevations=["level","above","below"],distances=["medium","close","far"];
function t(k){const locale=typeof I18N!=="undefined"?I18N.lang:"en";return (words[locale]||words.en)[k]||words.en[k]||k}
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
 const stage=elt("button",t("send"));stage.type="button";
 const mapLabel=elt("label",t("mappingMode")),mapMode=elt("select");
 mapMode.add(new Option(t("auto"),"auto"));mapMode.add(new Option(t("semi"),"semi"));
 mapLabel.append(mapMode);
 const controls=elt("div");controls.className="mv-request-controls";
 controls.append(flowLabel,directionLabel,heightLabel,distanceLabel,extraLabel,mapLabel,stage);
 const message=elt("p",t("pending"));message.setAttribute("role","status");
 const transfer=elt("section"),transferTitle=elt("h3",t("uploadedHeading"));
 transferTitle.hidden=true;
 const transferred=elt("ul");transferred.setAttribute("aria-live","polite");
 transfer.append(transferTitle,transferred);
 const mapping=elt("div");mapping.hidden=true;
 const mappingTitle=elt("h3",t("mapping"));mapping.append(mappingTitle);
 const fieldsWrap=elt("div");mapping.append(fieldsWrap);
 const promptWrap=elt("label",t("prompt")),promptField=elt("select");
 promptWrap.append(promptField);mapping.append(promptWrap);
 const edit=elt("textarea");edit.rows=4;edit.maxLength=3500;mapping.append(edit);
 const run=elt("button",t("run"));run.type="button";const cancel=elt("button",t("cancel"));cancel.type="button";cancel.disabled=true;
 mapping.append(run,cancel);
 const outputs=elt("div");
 panel.append(refresh,elt("h3",t("photos")),refs,controls,message,transfer,mapping,outputs,elt("p",t("note")));host.append(panel);
 let candidates=[],installed=[],chosen=[],upload=[],prepared=null,active="",timer=null,disposed=false,stagedRequest=null;
 const ok=()=>!disposed&&host.isConnected&&getProject()===originalProject;
 const status=x=>message.textContent=x;
 function stop(){if(timer)clearTimeout(timer);timer=null;cancel.disabled=true;}
 function dispose(){disposed=true;stop();}
 function resetPrepared(){prepared=null;upload=[];chosen=[];stagedRequest=null;mapping.hidden=true;transferTitle.hidden=true;transferred.replaceChildren();fieldsWrap.replaceChildren();outputs.replaceChildren();stop();}
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
     box.onchange=()=>{if(checked().length>4){box.checked=false;status(t("max4"))}resetPrepared()};
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
   transferTitle.hidden=false;transferred.replaceChildren();
   for(const item of upload){
     const original=candidates.find(x=>x.id===item.capture_id);
     transferred.append(elt("li",(original?.name||item.capture_id)+" → ComfyUI/input/"+item.comfy_name));
   }
   status(t("uploadedStatus").replace("{count}",String(upload.length)));
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
    if(first&&mapMode.value==="auto")chooser.value=first.value;
    label.append(chooser);fieldsWrap.append(label);assigned.push(chooser);
   }
   const texts=editablePromptFields(prepared);
   promptField.replaceChildren(new Option(t("none"),""));
   for(const f of texts)promptField.add(new Option(f.class_type+" #"+f.node+" · "+f.name,f.node+"|"+f.name));
   const preferred=texts.find(f=>/CLIPTextEncode|TextEncode|Prompt/i.test(f.class_type))||texts[0];
   if(preferred)promptField.value=preferred.node+"|"+preferred.name;
   const selected=preferred?.value||"";
   edit.value=selected+"\n"+makePrompt(stagedRequest);
   mapping.hidden=false;status(t("ready")+" "+t("confirmMapping"));
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
  if(fieldKeys.some(x=>!x)||new Set(fieldKeys).size!==fieldKeys.length){status(t("chooseNode"));return}
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
 mapMode.onchange=resetPrepared;flowSelect.onchange=resetPrepared;for(const select of [direction,height,distance])select.onchange=resetPrepared;
 extra.oninput=resetPrepared;refresh.onclick=refreshAll;
 refreshAll();
 return {dispose};
}
window.OrkiMultiviewGenerateViews={mount,translate:t};
})();

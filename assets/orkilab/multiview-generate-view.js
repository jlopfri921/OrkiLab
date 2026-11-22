/* Multiview requested-view generator. Reuses OrkiLab's validated ComfyUI job API. */
(function(){
"use strict";
const words={
 es:{inputTitle:"Carpeta input de ComfyUI",inputPath:"Ruta completa de la carpeta input",browse:"Examinar…",direct:"Copiar directamente a la carpeta",viaApi:"Subir a través de la API",copyPhotos:"Copiar fotos seleccionadas",prepareCopied:"Preparar workflow",chooseInput:"Selecciona la carpeta input o utiliza la subida por API.",choosePhotos:"Selecciona entre una y cuatro fotografías reales.",pickerHint:"El explorador se abre en el ordenador que ejecuta OrkiLab.",pickerCancelled:"No se ha elegido ninguna carpeta.",copyDone:"Fotografías copiadas. Ahora puedes preparar un workflow compatible.",chooseWorkflow:"Elige un workflow compatible para continuar.",invalidInput:"Selecciona una carpeta existente cuyo nombre sea input.",confirmCopy:"¿Copiar {count} fotos al input sin modificar los originales?",compatibleOnly:"Solo workflows compatibles (recomendado)",allWorkflows:"Mostrar todos los workflows",noneCompatible:"No hay workflows con entradas LoadImage y campo de texto reconocidos. Puedes mostrar todos para revisión.",compatibleCount:"Compatibilidad preliminar: {count} entradas de imagen. Se validará al preparar.",send:"Enviar fotos seleccionadas a ComfyUI/input",mappingMode:"Asignación de fotos",auto:"Automática (propuesta, revisable)",semi:"Semiautomática (elegir cada nodo)",uploadedHeading:"Copias enviadas al input de ComfyUI",confirmMapping:"Confirmar la asignación antes de generar",notUploaded:"Ninguna foto enviada todavía",uploadedStatus:"Se enviaron {count} fotografías a ComfyUI/input. Revisa el destino de cada una.",chooseNode:"Selecciona un nodo LoadImage para cada fotografía.",unknown:"Desconocida",requestedLabel:"Vista solicitada (sintética, NO medida): ",max4:"Selecciona un máximo de cuatro fotografías de referencia.",title:"Generar vista faltante",intro:"Selecciona fotografías reales, asigna cada una a una entrada de imagen del workflow y solicita una vista. El workflow debe aceptar referencias: un modelo de texto a imagen no garantiza conservar el sujeto.",photos:"Fotografías de referencia (1–4)",workflow:"Workflow ComfyUI compatible",refresh:"Actualizar referencias y workflows",direction:"Vista solicitada",height:"Altura de cámara",distance:"Distancia aparente",extra:"Indicaciones adicionales (opcional)",stage:"Preparar fotos y workflow",mapping:"Asignación de imágenes a nodos LoadImage",prompt:"Campo de texto editable",run:"Generar nueva vista",cancel:"Cancelar generación",pending:"Selecciona fotos reales y un workflow compatible antes de continuar.",noRefs:"Vincula primero fotografías reales al sujeto.",noWorkflow:"Importa primero un workflow de imagen con nodos LoadImage conectados desde Zona ComfyUI.",badNodes:"El workflow necesita al menos una entrada LoadImage editable por cada foto elegida; selecciona menos fotos u otro workflow.",badPrompt:"Elige una entrada de texto editable; el workflow no tiene campos adecuados.",ready:"Las referencias se han copiado a ComfyUI/input. Configura las asignaciones y confirma para generar.",running:"Generando en ComfyUI…",finished:"Generación terminada. Revisa la imagen antes de incorporarla.",register:"Incorporar como sintética pendiente de revisión",saved:"Imagen sintética vinculada con su vista solicitada; los grados siguen desconocidos.",note:"Los modelos pueden inventar partes ocultas. Las copias subidas a ComfyUI/input no se eliminan automáticamente; tus originales siguen intactos.",confirmStage:"¿Copiar estas fotos a la carpeta input del ComfyUI configurado? Aún no se generará nada.",confirmRun:"¿Ejecutar este workflow con las fotos y la vista indicadas?",confirmImport:"¿Registrar esta imagen sintética en el sujeto sin aprobarla?",front:"Frontal",front_right:"Frontal derecha",right:"Derecha",back_right:"Trasera derecha",back:"Trasera",back_left:"Trasera izquierda",left:"Izquierda",front_left:"Frontal izquierda",top:"Superior",bottom:"Inferior",above:"Desde arriba",level:"A nivel",below:"Desde abajo",close:"Cerca",medium:"Media",far:"Lejos",none:"No modificar",stop:"Trabajo cancelado",mismatch:"Cambió el proyecto; la operación no se ha continuado."},
 en:{inputTitle:"ComfyUI input folder",inputPath:"Full input folder path",browse:"Browse…",direct:"Copy directly to folder",viaApi:"Upload via API",copyPhotos:"Copy selected photos",prepareCopied:"Prepare workflow",chooseInput:"Choose an input folder or use API upload.",choosePhotos:"Select one to four real photos.",pickerHint:"The picker opens on the computer running OrkiLab.",pickerCancelled:"No folder selected.",copyDone:"Photos copied. You can now prepare a compatible workflow.",chooseWorkflow:"Choose a compatible workflow to continue.",invalidInput:"Choose an existing folder named input.",confirmCopy:"Copy {count} photos to input without changing originals?",compatibleOnly:"Only compatible workflows (recommended)",allWorkflows:"Show all workflows",noneCompatible:"No workflows with recognized LoadImage and prompt inputs. Show all to review.",compatibleCount:"Preliminary match: {count} image inputs. Validated during preparation.",send:"Send selected photos to ComfyUI/input",mappingMode:"Photo mapping",auto:"Automatic (suggested, editable)",semi:"Semi-automatic (choose each node)",uploadedHeading:"Copies sent to ComfyUI input",confirmMapping:"Confirm mapping before generation",notUploaded:"No photos transferred yet",uploadedStatus:"Uploaded {count} photos to ComfyUI/input. Review every mapping.",chooseNode:"Select a LoadImage node for each photo.",unknown:"Unknown",requestedLabel:"Requested viewpoint (synthetic, NOT measured): ",max4:"Select up to four reference photographs.",title:"Generate missing viewpoint",intro:"Select real photographs, map each to an image input in a reference-capable workflow, and request a view. Text-to-image models cannot guarantee subject fidelity.",photos:"Reference photos (1–4)",workflow:"Compatible ComfyUI workflow",refresh:"Refresh references and workflows",direction:"Requested view",height:"Camera height",distance:"Apparent distance",extra:"Extra instructions (optional)",stage:"Stage photos and prepare workflow",mapping:"Map images to LoadImage nodes",prompt:"Editable text input",run:"Generate new view",cancel:"Cancel generation",pending:"Select real photos and a compatible workflow to continue.",noRefs:"Link real photos to this subject first.",noWorkflow:"Import an image workflow with connected LoadImage nodes in ComfyUI Zone.",badNodes:"Workflow needs an editable LoadImage input for each selected photo; select fewer photos or another workflow.",badPrompt:"Choose an editable prompt input; no compatible field found.",ready:"Reference copies are now in ComfyUI/input. Map them and confirm to generate.",running:"Generating with ComfyUI…",finished:"Generation completed. Review before importing.",register:"Register as synthetic and unreviewed",saved:"Synthetic image linked with its requested view; measured degrees remain unknown.",note:"Models can hallucinate hidden details. Copies staged in ComfyUI/input are not automatically removed; your originals remain intact.",confirmStage:"Copy these photos into the configured ComfyUI input folder? No generation yet.",confirmRun:"Execute the workflow with these references and requested view?",confirmImport:"Import this result as an unreviewed synthetic image?",front:"Front",front_right:"Front right",right:"Right",back_right:"Back right",back:"Back",back_left:"Back left",left:"Left",front_left:"Front left",top:"Top",bottom:"Bottom",above:"Above",level:"Level",below:"Below",close:"Close",medium:"Medium",far:"Far",none:"Do not change",stop:"Job cancelled",mismatch:"Project changed; operation stopped."},
 pt:{inputTitle:"Pasta input do ComfyUI",inputPath:"Caminho completo da pasta input",browse:"Procurar…",direct:"Copiar diretamente para a pasta",viaApi:"Enviar por API",copyPhotos:"Copiar fotos selecionadas",prepareCopied:"Preparar workflow",chooseInput:"Escolha a pasta input ou envio pela API.",choosePhotos:"Selecione de uma a quatro fotografias reais.",pickerHint:"O explorador abre no computador do OrkiLab.",pickerCancelled:"Nenhuma pasta selecionada.",copyDone:"Fotos copiadas. Agora prepare um workflow compatível.",chooseWorkflow:"Escolha um workflow compatível.",invalidInput:"Selecione uma pasta existente chamada input.",confirmCopy:"Copiar {count} fotos para input sem modificar os originais?",compatibleOnly:"Apenas workflows compatíveis (recomendado)",allWorkflows:"Mostrar todos os workflows",noneCompatible:"Nenhum workflow reconhecido com LoadImage e texto. Pode mostrar todos.",compatibleCount:"Compatibilidade preliminar: {count} entradas de imagem.",send:"Enviar fotos selecionadas para ComfyUI/input",mappingMode:"Associação das fotografias",auto:"Automática (sugerida, editável)",semi:"Semiautomática (escolher cada nó)",uploadedHeading:"Cópias enviadas para ComfyUI/input",confirmMapping:"Confirmar associação antes de gerar",notUploaded:"Nenhuma foto enviada ainda",uploadedStatus:"Foram enviadas {count} fotos para ComfyUI/input. Confirme as associações.",chooseNode:"Escolha um nó LoadImage para cada fotografia.",unknown:"Desconhecida",requestedLabel:"Vista solicitada (sintética, NÃO medida): ",max4:"Selecione no máximo quatro fotografias de referência.",title:"Gerar vista em falta",intro:"Selecione fotografias reais, associe-as a entradas de imagem de um workflow compatível com referências e peça uma nova vista. Modelos só de texto não garantem a fidelidade do sujeito.",photos:"Fotos de referência (1–4)",workflow:"Workflow ComfyUI compatível",refresh:"Atualizar referências e workflows",direction:"Vista pretendida",height:"Altura da câmara",distance:"Distância aparente",extra:"Instruções adicionais (opcional)",stage:"Preparar fotos e workflow",mapping:"Associar imagens aos nós LoadImage",prompt:"Campo de texto editável",run:"Gerar nova vista",cancel:"Cancelar geração",pending:"Selecione fotos reais e um workflow compatível para continuar.",noRefs:"Primeiro associe fotos reais a este sujeito.",noWorkflow:"Importe um workflow de imagem com nós LoadImage ligados na Zona ComfyUI.",badNodes:"É necessária uma entrada LoadImage editável por foto selecionada; escolha menos fotos ou outro workflow.",badPrompt:"Escolha um campo de prompt editável; não foi encontrado nenhum compatível.",ready:"As cópias foram colocadas em ComfyUI/input. Confirme as associações antes de gerar.",running:"A gerar no ComfyUI…",finished:"Geração concluída. Reveja antes de importar.",register:"Registar como sintética e não revista",saved:"Imagem sintética associada à vista solicitada; os graus medidos continuam desconhecidos.",note:"Os modelos podem inventar detalhes ocultos. As cópias em ComfyUI/input não são eliminadas automaticamente; os originais mantêm-se intactos.",confirmStage:"Copiar estas fotos para a pasta input do ComfyUI configurado? Ainda não será gerada nenhuma imagem.",confirmRun:"Executar este workflow com as referências e a vista solicitada?",confirmImport:"Importar este resultado como imagem sintética não revista?",front:"Frontal",front_right:"Frontal direita",right:"Direita",back_right:"Traseira direita",back:"Traseira",back_left:"Traseira esquerda",left:"Esquerda",front_left:"Frontal esquerda",top:"Superior",bottom:"Inferior",above:"De cima",level:"Ao nível",below:"De baixo",close:"Perto",medium:"Média",far:"Longe",none:"Não modificar",stop:"Trabalho cancelado",mismatch:"O projeto mudou; a operação foi interrompida."},
 fr:{inputTitle:"Dossier input de ComfyUI",inputPath:"Chemin complet du dossier input",browse:"Parcourir…",direct:"Copier directement dans le dossier",viaApi:"Envoyer par API",copyPhotos:"Copier les photos sélectionnées",prepareCopied:"Préparer le workflow",chooseInput:"Choisissez le dossier input ou l'envoi par API.",choosePhotos:"Sélectionnez une à quatre photos réelles.",pickerHint:"Le sélecteur s'ouvre sur l'ordinateur OrkiLab.",pickerCancelled:"Aucun dossier choisi.",copyDone:"Photos copiées. Préparez ensuite un workflow compatible.",chooseWorkflow:"Choisissez un workflow compatible.",invalidInput:"Choisissez un dossier existant nommé input.",confirmCopy:"Copier {count} photos sans modifier les originaux ?",compatibleOnly:"Workflows compatibles uniquement (conseillé)",allWorkflows:"Afficher tous les workflows",noneCompatible:"Aucun workflow LoadImage avec texte reconnu. Affichez tous les workflows.",compatibleCount:"Compatibilité préliminaire : {count} entrées image.",send:"Envoyer les photos sélectionnées vers ComfyUI/input",mappingMode:"Association des photos",auto:"Automatique (proposée, modifiable)",semi:"Semi-automatique (choisir chaque nœud)",uploadedHeading:"Copies transférées vers ComfyUI/input",confirmMapping:"Confirmer les associations avant génération",notUploaded:"Aucune photo transférée",uploadedStatus:"{count} photos envoyées vers ComfyUI/input. Vérifiez les associations.",chooseNode:"Choisissez un nœud LoadImage pour chaque photo.",unknown:"Inconnue",requestedLabel:"Vue demandée (synthétique, NON mesurée) : ",max4:"Sélectionnez au maximum quatre photos de référence.",title:"Générer une vue manquante",intro:"Choisissez des photos réelles, associez-les aux entrées d'image d'un workflow prenant en charge les références et demandez une vue. Un modèle texte-image ne garantit pas la fidélité au sujet.",photos:"Photos de référence (1–4)",workflow:"Workflow ComfyUI compatible",refresh:"Actualiser les références et workflows",direction:"Vue demandée",height:"Hauteur de caméra",distance:"Distance apparente",extra:"Instructions supplémentaires (facultatif)",stage:"Préparer les photos et le workflow",mapping:"Associer les images aux nœuds LoadImage",prompt:"Champ de texte modifiable",run:"Générer une nouvelle vue",cancel:"Annuler la génération",pending:"Sélectionnez des photos réelles et un workflow compatible pour continuer.",noRefs:"Associez d'abord des photos réelles à ce sujet.",noWorkflow:"Importez un workflow d'image avec des nœuds LoadImage connectés depuis la Zone ComfyUI.",badNodes:"Le workflow exige une entrée LoadImage modifiable par photo choisie ; choisissez moins de photos ou un autre workflow.",badPrompt:"Choisissez un champ de prompt modifiable ; aucun champ compatible trouvé.",ready:"Les copies sont dans ComfyUI/input. Vérifiez les associations avant de générer.",running:"Génération dans ComfyUI…",finished:"Génération terminée. Vérifiez avant d'importer.",register:"Enregistrer comme synthétique et non vérifiée",saved:"Image synthétique associée à la vue demandée ; aucun angle mesuré ajouté.",note:"Les modèles peuvent inventer des détails cachés. Les copies de ComfyUI/input ne sont pas supprimées automatiquement ; vos originaux restent intacts.",confirmStage:"Copier ces photos vers le dossier input de ComfyUI ? Aucune génération pour l'instant.",confirmRun:"Exécuter ce workflow avec ces références et cette vue ?",confirmImport:"Importer ce résultat comme image synthétique non vérifiée ?",front:"Face",front_right:"Avant droite",right:"Droite",back_right:"Arrière droite",back:"Arrière",back_left:"Arrière gauche",left:"Gauche",front_left:"Avant gauche",top:"Dessus",bottom:"Dessous",above:"D'en haut",level:"À hauteur",below:"D'en bas",close:"Proche",medium:"Moyenne",far:"Loin",none:"Ne pas modifier",stop:"Tâche annulée",mismatch:"Le projet a changé ; opération interrompue."},
 de:{inputTitle:"ComfyUI-input-Ordner",inputPath:"Vollständiger Pfad zum input-Ordner",browse:"Durchsuchen…",direct:"Direkt in den Ordner kopieren",viaApi:"Per API hochladen",copyPhotos:"Gewählte Fotos kopieren",prepareCopied:"Workflow vorbereiten",chooseInput:"Wählen Sie den input-Ordner oder API-Upload.",choosePhotos:"Wählen Sie 1–4 echte Fotos aus.",pickerHint:"Die Ordnerauswahl öffnet sich auf dem OrkiLab-PC.",pickerCancelled:"Kein Ordner gewählt.",copyDone:"Fotos kopiert. Wählen Sie nun einen kompatiblen Workflow.",chooseWorkflow:"Wählen Sie einen kompatiblen Workflow.",invalidInput:"Wählen Sie einen vorhandenen Ordner namens input.",confirmCopy:"{count} Fotos kopieren, ohne Originale zu ändern?",compatibleOnly:"Nur kompatible Workflows (empfohlen)",allWorkflows:"Alle Workflows anzeigen",noneCompatible:"Keine passenden LoadImage- und Texteingänge erkannt. Alle anzeigen.",compatibleCount:"Vorläufig passend: {count} Bildeingänge.",send:"Ausgewählte Fotos nach ComfyUI/input senden",mappingMode:"Fotozuordnung",auto:"Automatisch (Vorschlag, bearbeitbar)",semi:"Halbautomatisch (Knoten auswählen)",uploadedHeading:"Kopien in ComfyUI/input",confirmMapping:"Zuordnung vor Erzeugung bestätigen",notUploaded:"Noch keine Fotos übertragen",uploadedStatus:"{count} Fotos nach ComfyUI/input übertragen. Prüfen Sie die Zuordnung.",chooseNode:"Wählen Sie für jedes Foto einen LoadImage-Knoten.",unknown:"Unbekannt",requestedLabel:"Gewünschte Ansicht (synthetisch, NICHT gemessen): ",max4:"Wählen Sie höchstens vier Referenzfotos.",title:"Fehlende Ansicht erzeugen",intro:"Wählen Sie echte Referenzfotos aus und ordnen Sie diese den Bildeingängen eines geeigneten Workflows zu. Reine Text-zu-Bild-Modelle garantieren keine Motivtreue.",photos:"Referenzfotos (1–4)",workflow:"Kompatibler ComfyUI-Workflow",refresh:"Referenzen und Workflows aktualisieren",direction:"Gewünschte Ansicht",height:"Kamerahöhe",distance:"Scheinbare Entfernung",extra:"Zusätzliche Anweisungen (optional)",stage:"Fotos und Workflow vorbereiten",mapping:"Bilder LoadImage-Knoten zuordnen",prompt:"Bearbeitbares Textfeld",run:"Neue Ansicht erzeugen",cancel:"Erzeugung abbrechen",pending:"Wählen Sie echte Fotos und einen kompatiblen Workflow aus.",noRefs:"Verknüpfen Sie zuerst echte Fotos mit diesem Motiv.",noWorkflow:"Importieren Sie einen Bild-Workflow mit verbundenen LoadImage-Knoten aus der ComfyUI-Zone.",badNodes:"Pro Foto wird ein bearbeitbarer LoadImage-Eingang benötigt; weniger Fotos oder anderen Workflow wählen.",badPrompt:"Wählen Sie einen bearbeitbaren Prompt-Eingang; kein kompatibles Feld gefunden.",ready:"Kopien liegen in ComfyUI/input. Prüfen Sie die Zuordnung vor dem Start.",running:"Erzeugung in ComfyUI läuft…",finished:"Erzeugung abgeschlossen. Vor dem Import prüfen.",register:"Als synthetisch und ungeprüft registrieren",saved:"Synthetisches Bild mit gewünschter Ansicht verknüpft; gemessene Winkel bleiben unbekannt.",note:"Modelle können verdeckte Details erfinden. Kopien in ComfyUI/input werden nicht automatisch gelöscht; Originale bleiben unverändert.",confirmStage:"Diese Fotos nach ComfyUI/input kopieren? Noch keine Erzeugung.",confirmRun:"Diesen Workflow mit den Referenzen und der gewünschten Ansicht ausführen?",confirmImport:"Dieses Ergebnis als ungeprüftes synthetisches Bild importieren?",front:"Vorne",front_right:"Vorne rechts",right:"Rechts",back_right:"Hinten rechts",back:"Hinten",back_left:"Hinten links",left:"Links",front_left:"Vorne links",top:"Oben",bottom:"Unten",above:"Von oben",level:"Auf gleicher Höhe",below:"Von unten",close:"Nah",medium:"Mittel",far:"Fern",none:"Nicht ändern",stop:"Auftrag abgebrochen",mismatch:"Projekt gewechselt; Vorgang gestoppt."},
 it:{inputTitle:"Cartella input di ComfyUI",inputPath:"Percorso completo della cartella input",browse:"Sfoglia…",direct:"Copia direttamente nella cartella",viaApi:"Carica tramite API",copyPhotos:"Copia foto selezionate",prepareCopied:"Prepara workflow",chooseInput:"Scegli la cartella input oppure usa l'API.",choosePhotos:"Seleziona da una a quattro foto reali.",pickerHint:"La finestra si apre sul computer OrkiLab.",pickerCancelled:"Nessuna cartella scelta.",copyDone:"Foto copiate. Ora prepara un workflow compatibile.",chooseWorkflow:"Scegli un workflow compatibile.",invalidInput:"Scegli una cartella esistente chiamata input.",confirmCopy:"Copiare {count} foto senza modificare gli originali?",compatibleOnly:"Solo workflow compatibili (consigliato)",allWorkflows:"Mostra tutti i workflow",noneCompatible:"Nessun workflow con LoadImage e testo riconosciuto. Mostra tutti.",compatibleCount:"Compatibilità preliminare: {count} ingressi immagine.",send:"Invia le foto selezionate a ComfyUI/input",mappingMode:"Assegnazione delle foto",auto:"Automatica (suggerita, modificabile)",semi:"Semiautomatica (scegli ogni nodo)",uploadedHeading:"Copie inviate a ComfyUI/input",confirmMapping:"Conferma le assegnazioni prima di generare",notUploaded:"Nessuna foto inviata",uploadedStatus:"{count} foto inviate a ComfyUI/input. Verifica ogni assegnazione.",chooseNode:"Seleziona un nodo LoadImage per ogni foto.",unknown:"Sconosciuta",requestedLabel:"Vista richiesta (sintetica, NON misurata): ",max4:"Seleziona al massimo quattro foto di riferimento.",title:"Genera vista mancante",intro:"Seleziona foto reali, assegnale agli ingressi immagine di un workflow compatibile con riferimenti e richiedi una vista. I modelli testo-immagine non garantiscono la fedeltà al soggetto.",photos:"Foto di riferimento (1–4)",workflow:"Workflow ComfyUI compatibile",refresh:"Aggiorna riferimenti e workflow",direction:"Vista richiesta",height:"Altezza camera",distance:"Distanza apparente",extra:"Istruzioni aggiuntive (facoltative)",stage:"Prepara foto e workflow",mapping:"Assegna immagini ai nodi LoadImage",prompt:"Campo di testo modificabile",run:"Genera nuova vista",cancel:"Annulla generazione",pending:"Seleziona foto reali e un workflow compatibile per continuare.",noRefs:"Prima collega foto reali al soggetto.",noWorkflow:"Importa un workflow immagini con nodi LoadImage collegati nella Zona ComfyUI.",badNodes:"Serve un ingresso LoadImage modificabile per ciascuna foto; scegli meno foto o un altro workflow.",badPrompt:"Scegli un campo prompt modificabile; nessuno compatibile trovato.",ready:"Le copie sono in ComfyUI/input. Controlla le associazioni prima di generare.",running:"Generazione in ComfyUI…",finished:"Generazione completata. Controlla prima di importare.",register:"Registra come sintetica e non revisionata",saved:"Immagine sintetica collegata alla vista richiesta; i gradi misurati restano sconosciuti.",note:"I modelli possono inventare dettagli nascosti. Le copie in ComfyUI/input non vengono rimosse automaticamente; gli originali restano intatti.",confirmStage:"Copiare queste foto nella cartella input di ComfyUI? Nessuna generazione ancora.",confirmRun:"Eseguire questo workflow con questi riferimenti e questa vista?",confirmImport:"Importare questo risultato come immagine sintetica non revisionata?",front:"Frontale",front_right:"Anteriore destra",right:"Destra",back_right:"Posteriore destra",back:"Posteriore",back_left:"Posteriore sinistra",left:"Sinistra",front_left:"Anteriore sinistra",top:"Superiore",bottom:"Inferiore",above:"Dall'alto",level:"All'altezza",below:"Dal basso",close:"Vicino",medium:"Media",far:"Lontano",none:"Non modificare",stop:"Lavoro annullato",mismatch:"Il progetto è cambiato; operazione interrotta."},
 ja:{inputTitle:"ComfyUIのinputフォルダー",inputPath:"inputフォルダーのフルパス",browse:"参照…",direct:"選択したフォルダーへ直接コピー",viaApi:"APIでアップロード",copyPhotos:"選択写真をコピー",prepareCopied:"ワークフローを準備",chooseInput:"inputフォルダーを選択するかAPIを使用してください。",choosePhotos:"実写写真を1〜4枚選択してください。",pickerHint:"フォルダー選択画面はOrkiLabのPCに表示されます。",pickerCancelled:"フォルダー未選択。",copyDone:"写真をコピーしました。次にワークフローを準備できます。",chooseWorkflow:"対応ワークフローを選択してください。",invalidInput:"名前がinputの既存フォルダーを選択してください。",confirmCopy:"元写真を変更せずに{count}枚をコピーしますか？",compatibleOnly:"対応ワークフローのみ（推奨）",allWorkflows:"すべてのワークフローを表示",noneCompatible:"LoadImageとテキスト入力を持つワークフローが見つかりません。すべて表示できます。",compatibleCount:"暫定的に対応：画像入力{count}個。",send:"選択した写真をComfyUI/inputに送信",mappingMode:"写真の割り当て",auto:"自動（提案・編集可能）",semi:"半自動（ノードを手動選択）",uploadedHeading:"ComfyUI/inputへコピー済み",confirmMapping:"生成前に割り当てを確認",notUploaded:"写真はまだ送信されていません",uploadedStatus:"{count}枚の写真をComfyUI/inputに送信しました。割り当てを確認してください。",chooseNode:"写真ごとにLoadImageノードを選択してください。",unknown:"不明",requestedLabel:"要求した視点（合成・測定値ではありません）：",max4:"参照写真は最大4枚まで選択できます。",title:"不足視点を生成",intro:"実写の参照写真を選び、参照画像に対応するワークフローの画像入力に割り当てて視点を指定します。テキスト画像生成だけでは被写体の同一性を保証できません。",photos:"参照写真 (1～4枚)",workflow:"対応するComfyUIワークフロー",refresh:"参照写真とワークフローを更新",direction:"生成したい視点",height:"カメラの高さ",distance:"見かけの距離",extra:"追加指示（任意）",stage:"写真とワークフローを準備",mapping:"LoadImageノードへ画像を割り当て",prompt:"編集可能なテキスト入力",run:"新しい視点を生成",cancel:"生成をキャンセル",pending:"実写写真と対応するワークフローを選んでください。",noRefs:"先に実写写真を被写体に関連付けてください。",noWorkflow:"ComfyUIゾーンで接続済みのLoadImageノードを持つ画像ワークフローを読み込んでください。",badNodes:"各写真に編集可能なLoadImage入力が必要です。写真を減らすか別のワークフローを選んでください。",badPrompt:"編集可能なプロンプト入力が見つかりません。",ready:"写真のコピーをComfyUI/inputに保存しました。割り当てを確認して生成してください。",running:"ComfyUIで生成中…",finished:"生成が完了しました。取り込む前に確認してください。",register:"合成画像・未レビューとして登録",saved:"指定した視点と合成画像を関連付けました。測定角度は不明のままです。",note:"モデルが見えない部分を創作する場合があります。ComfyUI/inputのコピーは自動削除されず、元のファイルは変更されません。",confirmStage:"これらの写真をComfyUIのinputフォルダーにコピーしますか？まだ生成しません。",confirmRun:"参照写真と指定視点でワークフローを実行しますか？",confirmImport:"この結果を未レビューの合成画像として取り込みますか？",front:"正面",front_right:"右前",right:"右側",back_right:"右後",back:"背面",back_left:"左後",left:"左側",front_left:"左前",top:"上面",bottom:"下面",above:"上から",level:"同じ高さ",below:"下から",close:"近い",medium:"中程度",far:"遠い",none:"変更しない",stop:"ジョブをキャンセルしました",mismatch:"プロジェクトが変更されたため処理を中断しました。"},
 ko:{inputTitle:"ComfyUI input 폴더",inputPath:"input 폴더 전체 경로",browse:"찾아보기…",direct:"폴더에 직접 복사",viaApi:"API로 업로드",copyPhotos:"선택 사진 복사",prepareCopied:"워크플로 준비",chooseInput:"input 폴더를 선택하거나 API 업로드를 이용하세요.",choosePhotos:"실제 사진 1~4장을 선택하세요.",pickerHint:"폴더 선택창은 OrkiLab PC에서 열립니다.",pickerCancelled:"폴더가 선택되지 않았습니다.",copyDone:"사진을 복사했습니다. 이제 워크플로를 준비하세요.",chooseWorkflow:"호환 워크플로를 선택하세요.",invalidInput:"이름이 input인 기존 폴더를 선택하세요.",confirmCopy:"원본 변경 없이 사진 {count}장을 복사할까요?",compatibleOnly:"호환 워크플로만 표시(권장)",allWorkflows:"모든 워크플로 표시",noneCompatible:"LoadImage와 텍스트 입력을 갖춘 워크플로가 없습니다. 모두 표시할 수 있습니다.",compatibleCount:"예상 호환: 이미지 입력 {count}개.",send:"선택한 사진을 ComfyUI/input으로 전송",mappingMode:"사진 연결 방식",auto:"자동(추천·수정 가능)",semi:"반자동(노드 직접 선택)",uploadedHeading:"ComfyUI/input에 사본 전송됨",confirmMapping:"생성 전 연결 확인",notUploaded:"아직 전송된 사진이 없습니다",uploadedStatus:"{count}장의 사진을 ComfyUI/input으로 전송했습니다. 연결을 확인하세요.",chooseNode:"사진마다 LoadImage 노드를 선택하세요.",unknown:"알 수 없음",requestedLabel:"요청 시점(합성·측정값 아님): ",max4:"참조 사진은 최대 4장까지 선택할 수 있습니다.",title:"누락된 시점 생성",intro:"실제 참조 사진을 선택하고 참조 이미지를 지원하는 워크플로의 이미지 입력에 연결한 뒤 시점을 지정하세요. 텍스트 이미지 생성 모델은 피사체의 동일성을 보장하지 않습니다.",photos:"참조 사진(1~4장)",workflow:"호환 ComfyUI 워크플로",refresh:"참조 및 워크플로 새로고침",direction:"요청 시점",height:"카메라 높이",distance:"겉보기 거리",extra:"추가 지시(선택)",stage:"사진 및 워크플로 준비",mapping:"LoadImage 노드에 이미지 연결",prompt:"수정 가능한 텍스트 입력",run:"새 시점 생성",cancel:"생성 취소",pending:"실제 사진과 호환 워크플로를 선택하세요.",noRefs:"먼저 피사체에 실제 사진을 연결하세요.",noWorkflow:"ComfyUI 영역에서 연결된 LoadImage 노드가 있는 이미지 워크플로를 가져오세요.",badNodes:"선택한 사진마다 편집 가능한 LoadImage 입력이 필요합니다. 사진 수를 줄이거나 다른 워크플로를 선택하세요.",badPrompt:"수정 가능한 프롬프트 입력이 없습니다.",ready:"사진 사본을 ComfyUI/input에 저장했습니다. 연결을 확인하고 생성하세요.",running:"ComfyUI에서 생성 중…",finished:"생성이 끝났습니다. 가져오기 전에 확인하세요.",register:"합성·미검토 이미지로 등록",saved:"합성 이미지를 요청 시점에 연결했습니다. 측정 각도는 알 수 없는 상태로 유지됩니다.",note:"모델은 보이지 않는 부분을 만들어 낼 수 있습니다. ComfyUI/input 사본은 자동 삭제되지 않으며 원본은 그대로 유지됩니다.",confirmStage:"이 사진을 ComfyUI의 input 폴더에 복사할까요? 아직 생성하지 않습니다.",confirmRun:"이 참조 사진과 요청 시점으로 워크플로를 실행할까요?",confirmImport:"이 결과를 미검토 합성 이미지로 가져올까요?",front:"정면",front_right:"오른쪽 앞",right:"오른쪽",back_right:"오른쪽 뒤",back:"뒷면",back_left:"왼쪽 뒤",left:"왼쪽",front_left:"왼쪽 앞",top:"위쪽",bottom:"아래쪽",above:"위에서",level:"같은 높이",below:"아래에서",close:"가까움",medium:"중간",far:"멀리",none:"변경하지 않음",stop:"작업 취소됨",mismatch:"프로젝트가 변경되어 작업을 중단했습니다."}
};
const directions=["front","front_right","right","back_right","back","back_left","left","front_left","top","bottom"];
const elevations=["level","above","below"],distances=["medium","close","far"];
function t(k){const locale=typeof I18N!=="undefined"?I18N.lang:"en";return (words[locale]||words.en)[k]||words.en[k]||k}
function elt(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e}
function choose(label,options){const wrap=elt("label");wrap.append(elt("span",label));const select=elt("select");for(const key of options)select.add(new Option(t(key),key));wrap.append(select);return [wrap,select]}
function u(project,suffix){return "/api/workspace/multiview/projects/"+encodeURIComponent(project)+suffix}
function post(api,url,data){return api(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)})}
const officialLabels={
 es:{title:"Biblioteca oficial de workflows OrkiLab",empty:"No se han encontrado workflows adecuados para las fotografías seleccionadas. Puedes descargar o importar plantillas oficiales aquí.",included:"Plantillas incluidas (nodos básicos)",official:"Workflow oficial de OrkiLab",checkpoint:"Checkpoint instalado en ComfyUI",import:"Importar a OrkiLab",zip:"Descargar paquete ZIP",github:"Ver workflows en GitHub",advanced:"Plantillas avanzadas de ComfyUI",externalHint:"Guías oficiales para Qwen y FLUX: requieren revisar nodos y modelos antes de utilizarlas.",copyFirst:"Selecciona una fotografía y cópiala primero a ComfyUI/input.",onePhoto:"Las plantillas básicas admiten una sola fotografía. Selecciona y copia solo una.",pickCheckpoint:"Selecciona un checkpoint instalado; puedes importar modelos en ComfyUI antes de continuar.",done:"Importación completada. El workflow está disponible en la lista.",already:"Workflow ya importado. Seleccionado para preparar.",unavailable:"No se pudo leer la biblioteca oficial.",noModels:"ComfyUI no ha devuelto checkpoints compatibles. El ZIP puede descargarse sin conexión.",confirm:"¿Importar la plantilla y vincularla a la fotografía copiada?",starter:"Nodos básicos · 1 foto · requiere checkpoint",upstream:"Plantilla externa · comprobar dependencias"},
 en:{title:"Official OrkiLab workflow library",empty:"No suitable workflow for the selected photos. Download or import official starter templates here.",included:"Included templates (core nodes)",official:"OrkiLab official workflow",checkpoint:"Checkpoint installed in ComfyUI",import:"Import into OrkiLab",zip:"Download workflow ZIP",github:"View workflows on GitHub",advanced:"Advanced ComfyUI templates",externalHint:"Upstream Qwen and FLUX examples require model and node review before use.",copyFirst:"Select and copy one photo into ComfyUI/input first.",onePhoto:"Core templates support one photo. Select and copy just one.",pickCheckpoint:"Choose an installed checkpoint, or add a model to ComfyUI first.",done:"Import complete. The workflow is now in the selector.",already:"Workflow already imported. Selected for preparation.",unavailable:"Could not read official workflow library.",noModels:"ComfyUI returned no compatible checkpoints. ZIP download works offline.",confirm:"Import this template and bind it to the copied photo?",starter:"Core nodes · 1 photo · checkpoint required",upstream:"Upstream template · verify dependencies"},
 pt:{title:"Biblioteca oficial de workflows OrkiLab",empty:"Não há workflows adequados. Descarregue ou importe aqui modelos oficiais.",included:"Modelos incluídos (nós básicos)",official:"Workflow oficial OrkiLab",checkpoint:"Checkpoint instalado no ComfyUI",import:"Importar para OrkiLab",zip:"Descarregar pacote ZIP",github:"Ver workflows no GitHub",advanced:"Modelos avançados ComfyUI",externalHint:"Exemplos Qwen e FLUX requerem verificação de modelos e nós.",copyFirst:"Selecione e copie primeiro uma foto para ComfyUI/input.",onePhoto:"Os modelos básicos aceitam uma foto. Copie apenas uma.",pickCheckpoint:"Escolha um checkpoint instalado no ComfyUI.",done:"Importação concluída. Workflow disponível.",already:"Workflow já importado e selecionado.",unavailable:"Não foi possível ler a biblioteca oficial.",noModels:"O ComfyUI não devolveu checkpoints. O ZIP pode ser descarregado.",confirm:"Importar este modelo e associá-lo à foto copiada?",starter:"Nós básicos · 1 foto · checkpoint necessário",upstream:"Modelo externo · verificar dependências"},
 fr:{title:"Bibliothèque officielle de workflows OrkiLab",empty:"Aucun workflow adapté. Téléchargez ou importez les modèles officiels ici.",included:"Modèles inclus (nœuds de base)",official:"Workflow officiel OrkiLab",checkpoint:"Checkpoint installé dans ComfyUI",import:"Importer dans OrkiLab",zip:"Télécharger le ZIP",github:"Voir les workflows sur GitHub",advanced:"Modèles avancés ComfyUI",externalHint:"Les exemples Qwen et FLUX nécessitent une vérification des modèles et nœuds.",copyFirst:"Choisissez et copiez d'abord une photo dans ComfyUI/input.",onePhoto:"Les modèles de base acceptent une seule photo.",pickCheckpoint:"Choisissez un checkpoint installé dans ComfyUI.",done:"Importation terminée. Workflow disponible.",already:"Workflow déjà importé et sélectionné.",unavailable:"Bibliothèque officielle indisponible.",noModels:"ComfyUI n'a renvoyé aucun checkpoint. Le ZIP reste téléchargeable.",confirm:"Importer ce modèle avec la photo copiée ?",starter:"Nœuds de base · 1 photo · checkpoint requis",upstream:"Modèle externe · vérifier les dépendances"},
 de:{title:"Offizielle OrkiLab-Workflow-Bibliothek",empty:"Kein geeigneter Workflow gefunden. Laden oder importieren Sie hier offizielle Vorlagen.",included:"Enthaltene Vorlagen (Kernknoten)",official:"Offizieller OrkiLab-Workflow",checkpoint:"Checkpoint in ComfyUI installiert",import:"In OrkiLab importieren",zip:"ZIP-Paket herunterladen",github:"Workflows auf GitHub ansehen",advanced:"Erweiterte ComfyUI-Vorlagen",externalHint:"Qwen- und FLUX-Beispiele erfordern Modell- und Knotenprüfung.",copyFirst:"Wählen und kopieren Sie zuerst ein Foto nach ComfyUI/input.",onePhoto:"Basisvorlagen unterstützen nur ein Foto.",pickCheckpoint:"Wählen Sie einen installierten ComfyUI-Checkpoint.",done:"Import abgeschlossen. Workflow ist auswählbar.",already:"Workflow bereits importiert und ausgewählt.",unavailable:"Offizielle Bibliothek nicht verfügbar.",noModels:"Keine ComfyUI-Checkpoints gefunden. ZIP-Download ist möglich.",confirm:"Vorlage mit dem kopierten Foto importieren?",starter:"Kernknoten · 1 Foto · Checkpoint erforderlich",upstream:"Externe Vorlage · Abhängigkeiten prüfen"},
 it:{title:"Libreria ufficiale dei workflow OrkiLab",empty:"Nessun workflow adatto. Scarica o importa qui i modelli ufficiali.",included:"Modelli inclusi (nodi base)",official:"Workflow ufficiale OrkiLab",checkpoint:"Checkpoint installato in ComfyUI",import:"Importa in OrkiLab",zip:"Scarica pacchetto ZIP",github:"Vedi workflow su GitHub",advanced:"Modelli avanzati ComfyUI",externalHint:"Gli esempi Qwen e FLUX richiedono la verifica dei modelli e dei nodi.",copyFirst:"Prima seleziona e copia una foto in ComfyUI/input.",onePhoto:"I modelli base supportano una sola foto.",pickCheckpoint:"Seleziona un checkpoint installato in ComfyUI.",done:"Importazione completata. Workflow disponibile.",already:"Workflow già importato e selezionato.",unavailable:"Impossibile leggere la libreria ufficiale.",noModels:"ComfyUI non ha restituito checkpoint. Puoi scaricare il ZIP.",confirm:"Importare il modello e collegarlo alla foto copiata?",starter:"Nodi base · 1 foto · checkpoint richiesto",upstream:"Modello esterno · verificare dipendenze"},
 ja:{title:"OrkiLab公式ワークフローライブラリ",empty:"対応するワークフローがありません。公式テンプレートをダウンロードまたは取り込めます。",included:"収録テンプレート（基本ノード）",official:"OrkiLab公式ワークフロー",checkpoint:"ComfyUIにインストール済みのチェックポイント",import:"OrkiLabに取り込む",zip:"ZIPをダウンロード",github:"GitHubで確認",advanced:"ComfyUIの高度なテンプレート",externalHint:"Qwen・FLUXの公式例はモデルとノードの確認が必要です。",copyFirst:"先に写真を1枚選んでComfyUI/inputにコピーしてください。",onePhoto:"基本テンプレートは写真1枚のみ対応します。",pickCheckpoint:"インストール済みチェックポイントを選択してください。",done:"取り込み完了。ワークフローを選択できます。",already:"すでに取り込み済みです。準備用に選択しました。",unavailable:"公式ライブラリを読み込めません。",noModels:"ComfyUIからチェックポイントを取得できません。ZIPはダウンロードできます。",confirm:"コピーした写真を使うテンプレートを取り込みますか？",starter:"基本ノード · 写真1枚 · チェックポイント必須",upstream:"外部テンプレート · 依存関係を確認"},
 ko:{title:"OrkiLab 공식 워크플로 라이브러리",empty:"호환 워크플로가 없습니다. 여기서 공식 템플릿을 내려받거나 가져오세요.",included:"포함된 템플릿(기본 노드)",official:"OrkiLab 공식 워크플로",checkpoint:"ComfyUI에 설치된 체크포인트",import:"OrkiLab으로 가져오기",zip:"ZIP 다운로드",github:"GitHub에서 워크플로 보기",advanced:"ComfyUI 고급 템플릿",externalHint:"Qwen·FLUX 공식 예제는 모델 및 노드 확인이 필요합니다.",copyFirst:"먼저 사진 1장을 ComfyUI/input에 복사하세요.",onePhoto:"기본 템플릿은 사진 1장만 지원합니다.",pickCheckpoint:"설치된 체크포인트를 선택하세요.",done:"가져오기 완료. 워크플로를 사용할 수 있습니다.",already:"이미 가져온 워크플로를 선택했습니다.",unavailable:"공식 라이브러리를 읽을 수 없습니다.",noModels:"ComfyUI에 체크포인트가 없습니다. ZIP은 다운로드할 수 있습니다.",confirm:"복사한 사진에 템플릿을 연결해 가져올까요?",starter:"기본 노드 · 사진 1장 · 체크포인트 필요",upstream:"외부 템플릿 · 의존성을 확인"}
};
function officialText(key){const locale=typeof I18N!=="undefined"?I18N.lang:"en";return (officialLabels[locale]||officialLabels.en)[key]||officialLabels.en[key]||key;}
function mount(host,getProject,subjectId,api,onImport){
 const originalProject=getProject(),panel=elt("section");panel.className="mv-requested-generation no-i18n";
 panel.append(elt("h2",t("title")),elt("p",t("intro")));
 const refresh=elt("button",t("refresh"));refresh.type="button";
 const refs=elt("div");const flowSelect=elt("select");
 const flowLabel=elt("label",t("workflow"));flowLabel.append(flowSelect);
 const filterLabel=elt("label"),filterToggle=elt("input");filterToggle.type="checkbox";filterToggle.checked=true;
 filterLabel.append(filterToggle,elt("span",t("compatibleOnly")));
 const flowInfo=elt("p");flowInfo.className="muted";
 const [directionLabel,direction]=choose(t("direction"),directions);
 const [heightLabel,height]=choose(t("height"),elevations);
 const [distanceLabel,distance]=choose(t("distance"),distances);
 const extra=elt("textarea");extra.maxLength=500;extra.rows=2;
 const extraLabel=elt("label",t("extra"));extraLabel.append(extra);
 const folderTitle=elt("h3",t("inputTitle"));
 const modeLabel=elt("label",t("inputTitle")),transferMode=elt("select");
 transferMode.add(new Option(t("direct"),"folder"));transferMode.add(new Option(t("viaApi"),"api"));modeLabel.append(transferMode);
 const pathLabel=elt("label",t("inputPath")),inputPath=elt("input");inputPath.type="text";inputPath.autocomplete="off";
 inputPath.placeholder="C:\\\\ComfyUI\\\\input";pathLabel.append(inputPath);
 const browse=elt("button",t("browse"));browse.type="button";
 const folderDetails=elt("div");folderDetails.append(pathLabel,browse,elt("p",t("pickerHint")));
 const folderSection=elt("section");folderSection.append(folderTitle,modeLabel,folderDetails);
 const stage=elt("button",t("copyPhotos"));stage.type="button";
 const prepareCopy=elt("button",t("prepareCopied"));prepareCopy.type="button";prepareCopy.disabled=true;
 const mapLabel=elt("label",t("mappingMode")),mapMode=elt("select");
 mapMode.add(new Option(t("auto"),"auto"));mapMode.add(new Option(t("semi"),"semi"));
 mapLabel.append(mapMode);
 const controls=elt("div");controls.className="mv-request-controls";
 controls.append(directionLabel,heightLabel,distanceLabel,extraLabel,mapLabel);
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
 const officialPanel=elt("details");officialPanel.className="mv-official-library";
 const officialTitle=elt("summary",officialText("title"));
 const officialHint=elt("p",officialText("empty"));
 const officialLinks=elt("div");officialLinks.className="mv-official-links";
 const zipLink=elt("a",officialText("zip"));zipLink.href="/api/workspace/multiview/official-workflows/download";
 zipLink.setAttribute("download","OrkiLab-Multiview-Workflows-0.5.0-rc1.zip");
 const githubLink=elt("a",officialText("github"));
 githubLink.href="https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/tree/main/workflows/multiview";
 githubLink.target="_blank";githubLink.rel="noopener noreferrer";
 officialLinks.append(zipLink,githubLink);
 const officialItems=elt("div");officialItems.className="mv-official-templates";
 const officialSelect=elt("select");
 const checkpoints=elt("select");const checkpointLabel=elt("label",officialText("checkpoint"));
 checkpointLabel.append(checkpoints);
 const installOfficial=elt("button",officialText("import"));installOfficial.type="button";
 const officialStatus=elt("p");officialStatus.setAttribute("role","status");
 const upstreamLinks=elt("div");
 officialPanel.append(officialTitle,officialHint,officialLinks,
    elt("h3",officialText("included")),officialSelect,checkpointLabel,
    installOfficial,officialStatus,elt("h3",officialText("advanced")),
    elt("p",officialText("externalHint")),upstreamLinks);
 panel.append(refresh,elt("h3",t("photos")),refs,folderSection,stage,transfer,flowLabel,
   filterLabel,flowInfo,officialPanel,controls,prepareCopy,message,mapping,outputs,elt("p",t("note")));host.append(panel);
 let candidates=[],installed=[],chosen=[],upload=[],prepared=null,active="",timer=null,disposed=false,stagedRequest=null;
 const ok=()=>!disposed&&host.isConnected&&getProject()===originalProject;
 const status=x=>message.textContent=x;
 transferMode.onchange=()=>{folderDetails.hidden=transferMode.value!=="folder";resetPrepared()};
 inputPath.oninput=resetPrepared;
 browse.onclick=async()=>{
  browse.disabled=true;
  try{
   const result=await post(api,"/api/workspace/multiview/comfyui-input/browse",{confirm:true});
   if(!ok())return;
   if(result.cancelled){status(t("pickerCancelled"));return}
   inputPath.value=result.path;resetPrepared();
  }catch(e){status(e.message)}finally{browse.disabled=false}
 };
 api("/api/workspace/multiview/comfyui-input").then(result=>{
  if(ok()&&result?.path)inputPath.value=result.path;
 }).catch(()=>{});
 function stop(){if(timer)clearTimeout(timer);timer=null;cancel.disabled=true;}
 function dispose(){disposed=true;stop();}
 function resetPrepared(){prepared=null;upload=[];chosen=[];stagedRequest=null;prepareCopy.disabled=true;mapping.hidden=true;transferTitle.hidden=true;transferred.replaceChildren();fieldsWrap.replaceChildren();outputs.replaceChildren();stop();}
 function checked(){return [...refs.querySelectorAll("input:checked")].map(x=>x.value)}
 function selectOne(){return [direction.value,height.value,distance.value]}
 function filterWorkflows(){
  const current=flowSelect.value;
  const count=checked().length||1;
  const matches=installed.filter(f=>f.category==="image"&&
   f.multiview_reference?.likely_compatible&&f.multiview_reference.image_inputs>=count);
  const shown=filterToggle.checked?matches:installed;
  flowSelect.replaceChildren(new Option(t("workflow"),""));
  for(const item of shown){
   const number=item.multiview_reference?.image_inputs||0;
   flowSelect.add(new Option(item.name+(number?" · "+t("compatibleCount").replace("{count}",number):""),item.id));
  }
  if([...flowSelect.options].some(option=>option.value===current))flowSelect.value=current;
  flowInfo.textContent=filterToggle.checked&&matches.length===0?t("noneCompatible"):
   (filterToggle.checked?"":t("allWorkflows"));
  if(filterToggle.checked&&matches.length===0)officialPanel.open=true;
 }
 filterToggle.onchange=()=>{prepared=null;mapping.hidden=true;filterWorkflows()};
 let officialReady=false;
 async function loadOfficial(){
  try{
   const [data,modelData]=await Promise.all([
    api("/api/workspace/multiview/official-workflows"),
    api("/api/workspace/multiview/official-workflows/checkpoints").catch(()=>({checkpoints:[]}))
   ]);
   if(!ok())return;
   officialSelect.replaceChildren();
   for(const entry of data.official||[]){
    officialSelect.add(new Option(entry.name+" · "+officialText("starter"),entry.id));
   }
   checkpoints.replaceChildren(new Option(officialText("checkpoint"),""));
   for(const filename of modelData.checkpoints||[])checkpoints.add(new Option(filename,filename));
   upstreamLinks.replaceChildren();
   for(const entry of data.upstream||[]){
    const link=elt("a",entry.name+" · "+officialText("upstream"));
    link.href=entry.url;link.target="_blank";link.rel="noopener noreferrer";
    upstreamLinks.append(link);
   }
   officialReady=true;
   if(!(modelData.checkpoints||[]).length)officialStatus.textContent=officialText("noModels");
  }catch(e){officialStatus.textContent=officialText("unavailable")}
 }
 installOfficial.onclick=async()=>{
  if(!officialReady){officialStatus.textContent=officialText("unavailable");return}
  if(upload.length!==1){officialStatus.textContent=upload.length?officialText("onePhoto"):officialText("copyFirst");return}
  if(!checkpoints.value){officialStatus.textContent=officialText("pickCheckpoint");return}
  if(!window.confirm(officialText("confirm")))return;
  installOfficial.disabled=true;
  try{
   const result=await post(api,"/api/workspace/multiview/official-workflows/install",{
    confirm:true,template_id:officialSelect.value,checkpoint:checkpoints.value,
    image_name:upload[0].comfy_name
   });
   if(!ok())return;
   const workflows=await api("/api/workspace/workflows");
   installed=(workflows.workflows||[]).filter(f=>f.category==="image");
   filterWorkflows();
   if(![...flowSelect.options].some(x=>x.value===result.id)){
    filterToggle.checked=false;filterWorkflows();
   }
   flowSelect.value=result.id;
   officialStatus.textContent=officialText(result.installed?"done":"already");
   prepared=null;mapping.hidden=true;
  }catch(e){officialStatus.textContent=e.message}finally{installOfficial.disabled=false}
 };
 loadOfficial();
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
     box.onchange=()=>{if(checked().length>4){box.checked=false;status(t("max4"))}resetPrepared();filterWorkflows()};
   }
   if(!candidates.length)refs.append(elt("p",t("noRefs")));
   installed=(workflows.workflows||[]).filter(x=>x.category==="image");
   filterWorkflows();
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
  const ids=checked();
  if(!ok()||ids.length<1||ids.length>4){status(t("choosePhotos"));return}
  const mode=transferMode.value,folder=inputPath.value.trim();
  if(mode==="folder"&&!folder){status(t("chooseInput"));return}
  if(!window.confirm(t("confirmCopy").replace("{count}",ids.length)))return;
  stage.disabled=true;resetPrepared();
  try{
   const body={confirm:true,capture_ids:ids,transfer_mode:mode};
   if(mode==="folder")body.input_folder=folder;
   const result=await post(api,u(originalProject,"/subjects/"+subjectId+"/reference-upload"),body);
   if(!ok())throw Error(t("mismatch"));
   upload=result.references;chosen=[...ids];
   transferTitle.hidden=false;transferred.replaceChildren();
   for(const item of upload){
    const original=candidates.find(x=>x.id===item.capture_id);
    transferred.append(elt("li",(original?.name||item.capture_id)+" → ComfyUI/input/"+item.comfy_name));
   }
   prepareCopy.disabled=false;status(t("copyDone"));
  }catch(e){status(e.message);resetPrepared()}finally{stage.disabled=false}
 };
 prepareCopy.onclick=async()=>{
  const flow=flowSelect.value;
  if(!ok()||!upload.length){status(t("choosePhotos"));return}
  if(!flow){status(t("chooseWorkflow"));return}
  prepareCopy.disabled=true;mapping.hidden=true;
  try{
   const p=await post(api,"/api/workspace/generation/prepare",{workflow_id:flow});
   if(!ok())throw Error(t("mismatch"));
   const inputs=connectedImageInputs(p);
   if(inputs.length<upload.length||!upload.every(x=>inputs.some(f=>matches(f,x.comfy_name))))throw Error(t("badNodes"));
   const texts=editablePromptFields(p);
   if(!texts.length)throw Error(t("badPrompt"));
   stagedRequest={direction:direction.value,height:height.value,distance:distance.value,extra:extra.value};
   prepared={token:p.token,workflowId:flow,fields:p.fields||[]};
   fieldsWrap.replaceChildren();assigned=[];
   for(const item of upload){
    const original=candidates.find(x=>x.id===item.capture_id);
    const label=elt("label",(original?.name||"Photo")+" → LoadImage");
    const selector=elt("select");selector.add(new Option(t("none"),""));
    for(const field of inputs.filter(f=>matches(f,item.comfy_name)))
     selector.add(new Option(field.class_type+" #"+field.node+" · "+field.name,field.node+"|"+field.name));
    if(mapMode.value==="auto"){
     const candidate=[...selector.options].find(x=>x.value&&!assigned.some(y=>y.value===x.value));
     if(candidate)selector.value=candidate.value;
    }
    label.append(selector);fieldsWrap.append(label);assigned.push(selector);
   }
   promptField.replaceChildren(new Option(t("none"),""));
   for(const field of texts)promptField.add(new Option(field.class_type+" #"+field.node+" · "+field.name,field.node+"|"+field.name));
   const preferred=texts.find(f=>/CLIPTextEncode|TextEncode|Prompt/i.test(f.class_type))||texts[0];
   promptField.value=preferred.node+"|"+preferred.name;
   edit.value=(preferred.value||"")+"\n"+makePrompt(stagedRequest);
   mapping.hidden=false;status(t("ready")+" "+t("confirmMapping"));
  }catch(e){status(e.message);mapping.hidden=true}finally{prepareCopy.disabled=false}
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
 mapMode.onchange=()=>{prepared=null;mapping.hidden=true;fieldsWrap.replaceChildren()};flowSelect.onchange=()=>{prepared=null;mapping.hidden=true;fieldsWrap.replaceChildren()};for(const select of [direction,height,distance])select.onchange=()=>{prepared=null;mapping.hidden=true};
 extra.oninput=()=>{prepared=null;mapping.hidden=true};refresh.onclick=refreshAll;
 refreshAll();
 return {dispose};
}
window.OrkiMultiviewGenerateViews={mount,translate:t};
})();

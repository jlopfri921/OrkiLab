/* OrkiLab general guide: six additional languages with accessible, text-only DOM.
 * The Spanish and English sections remain in the HTML for no-JS fallback. */
(function(){
"use strict";
const dictionary={
pt:{
hero:["ORKILAB / AJUDA 0.5.0 RC.1","Guia do OrkiLab","Conheça a estrutura da aplicação, os projetos, os dados, o treino e as ferramentas opcionais de IA. Consultar este guia não executa workflows nem descarrega modelos."],
nav:["Primeiros passos","Módulos","Multivista","Modos","Perguntas frequentes"],
flow:["1. Primeiros passos","Em Projetos, crie um projeto e escolha a categoria e o motor.","No Dataset Studio, associe imagens, reveja a qualidade e prepare as descrições.","Em Treinadores, abra um motor compatível e configure o treino. Criar um projeto não inicia o treino automaticamente.","Na Fila de trabalhos, acompanhe o progresso e controle as tarefas.","Em Os meus LoRA treinados, consulte os resultados guardados.","Abrir projetos"],
modules:["2. Estrutura e funções","Painel principal: acesso rápido e estado da instalação.","Projetos: organização do motor, dados e atividade.","Treinadores: treino por família de modelos.","Dataset Studio: referências sem alterar originais, revisão, comparação e legendas.","Estúdio multivista: vistas do sujeito, cobertura e exportação.","Gestor GPU: recursos, memória e diagnóstico.","Fila: execução e controlo das tarefas.","Definições: GPU, rede, modo independente ou ComfyUI.","Zona ComfyUI: ligação, modelos, workflows e geração quando ativada."],
multiview:["3. Multivista: de fotos a novas vistas","Escolha um projeto de imagem.","Crie um sujeito, o objeto ou figura presente nas fotografias.","Na recuperação de fotografias, associe as imagens do Dataset Studio ao sujeito.","Se não conhecer os ângulos, deixe-os em branco. A IA local de Ollama sugere orientações, não graus medidos.","Reveja a comparação e a cobertura. Os setores sem azimute conhecido permanecem desconhecidos.","Em Gerar vista em falta, escolha 1–4 fotos reais e um workflow ComfyUI com entradas LoadImage; associe-as e gere uma imagem sintética.","Reveja o resultado antes de o registar como sintético e não aprovado. Exporte o ZIP quando estiver pronto.","A IA pode inventar detalhes não visíveis. Não substitui a fotogrametria nem medições geométricas.","Abrir Multivista"],
modes:["4. Modos de funcionamento","Só OrkiLab (independente): treinadores, Dataset Studio, GPU, projetos e fila continuam disponíveis. As ferramentas exclusivas do ComfyUI ficam ocultas.","Com ComfyUI: ative a ligação e os workflows. Híbrido: combine os treinadores OrkiLab com a geração ComfyUI. Pode mudar de modo nas Definições sem eliminar dados.","Ollama é opcional e independente do ComfyUI. Não é instalado automaticamente e requer um modelo local de visão para analisar fotos."],
faq:["Perguntas frequentes","Porque não aparece o meu projeto no Multivista?","O projeto deve estar ativo e pertencer à categoria Imagem; os projetos arquivados não aparecem.","O que significa Dataset 8 fotos / Multivista 0?","As fotos estão no Dataset Studio, mas ainda precisa de criar um sujeito e associá-las. Não são duplicadas.","A IA consegue medir o ângulo exato?","Não. A direção visual é estimada, não um azimute medido. Deixe vazios os graus desconhecidos.","Porque não é gerada uma vista nova?","Verifique o modo e a ligação do ComfyUI, um workflow validado e as entradas de imagem ligadas.","As fotos originais são apagadas ao remover referências?","Não. As referências preservam os originais. Faça uma cópia de settings/orkilab antes de alterações importantes.","E se a GPU ficar sem memória?","Consulte o Gestor GPU e os controlos de memória. Não interrompa tarefas de outras pessoas nem termine processos desconhecidos."]
},
fr:{
hero:["ORKILAB / AIDE 0.5.0 RC.1","Guide d'OrkiLab","Découvrez la structure de l'application, les projets, les données, l'entraînement et les outils d'IA facultatifs. Lire ce guide ne lance aucun workflow et ne télécharge aucun modèle."],
nav:["Premiers pas","Modules","Multivue","Modes","Questions fréquentes"],
flow:["1. Premiers pas","Dans Projets, créez un projet et choisissez sa catégorie et son moteur.","Dans Dataset Studio, associez des images, vérifiez leur qualité et préparez les descriptions.","Dans Entraîneurs, ouvrez un moteur compatible et configurez l'entraînement. Un projet ne lance aucun entraînement automatiquement.","Dans la File de tâches, suivez l'avancement et gérez les travaux.","Dans Mes LoRA entraînés, consultez les résultats enregistrés.","Ouvrir les projets"],
modules:["2. Structure et fonctions","Tableau de bord : accès rapide et état de l'installation.","Projets : organisation du moteur, des données et des activités.","Entraîneurs : outils d'entraînement par famille de modèles.","Dataset Studio : références non destructives, contrôle, comparaison et descriptions.","Studio multivue : vues d'un sujet, couverture et exportation.","Gestionnaire GPU : ressources, mémoire et diagnostics.","File : exécution et suivi des tâches.","Paramètres : GPU, réseau, mode autonome ou ComfyUI.","Zone ComfyUI : connexion, modèles, workflows et génération si activée."],
multiview:["3. Multivue : des photos aux nouvelles vues","Choisissez un projet d'images.","Créez un sujet : l'objet ou la figure représentée sur les photos.","Dans la récupération des photos, associez celles du Dataset Studio au sujet.","Si les angles sont inconnus, laissez-les vides. L'IA locale d'Ollama suggère des directions, pas des degrés mesurés.","Examinez la comparaison et la couverture. Les secteurs sans azimut restent inconnus.","Dans Générer une vue manquante, sélectionnez 1 à 4 photos réelles et un workflow ComfyUI avec des entrées LoadImage, puis générez une image synthétique.","Vérifiez le résultat avant de l'intégrer comme synthétique et non approuvé. Exportez le ZIP si nécessaire.","L'IA peut inventer les détails cachés. Elle ne remplace pas la photogrammétrie ni une mesure géométrique.","Ouvrir Multivue"],
modes:["4. Modes de fonctionnement","OrkiLab seul (autonome) : les entraîneurs, Dataset Studio, le GPU, les projets et la file restent disponibles. Les outils ComfyUI sont masqués.","Avec ComfyUI : activez la connexion et les workflows. Hybride : combinez l'entraînement OrkiLab avec la génération ComfyUI. Changez de mode dans les Paramètres sans effacer les données.","Ollama est facultatif et indépendant de ComfyUI. Il n'est jamais installé automatiquement et exige un modèle local de vision pour analyser les photos."],
faq:["Questions fréquentes","Pourquoi mon projet n'apparaît-il pas dans Multivue ?","Il doit être actif et de catégorie Image ; les projets archivés ne sont pas affichés.","Que signifie Dataset 8 photos / Multivue 0 ?","Les photos sont dans Dataset Studio, mais vous devez créer un sujet et les associer. Elles ne sont pas dupliquées.","L'IA peut-elle mesurer l'angle exact ?","Non. Une direction visuelle est une estimation, pas un azimut mesuré. Laissez les degrés inconnus vides.","Pourquoi la nouvelle vue ne se génère-t-elle pas ?","Vérifiez la connexion à ComfyUI, le workflow validé et les entrées d'image connectées.","Les originaux sont-ils supprimés en retirant les références ?","Non. Les références préservent les originaux. Sauvegardez settings/orkilab avant toute modification importante.","Que faire si la mémoire GPU est saturée ?","Consultez le Gestionnaire GPU et les contrôles mémoire. N'interrompez pas les tâches d'autres utilisateurs ni des processus inconnus."]
},
de:{
hero:["ORKILAB / HILFE 0.5.0 RC.1","OrkiLab-Handbuch","Hier finden Sie den Aufbau der Anwendung, Projekte, Daten, Training und optionale KI-Werkzeuge. Beim Lesen werden weder Workflows gestartet noch Modelle heruntergeladen."],
nav:["Erste Schritte","Module","Mehransichten","Modi","Häufige Fragen"],
flow:["1. Erste Schritte","Erstellen Sie unter Projekte ein Projekt und wählen Sie Kategorie und Engine.","Verknüpfen Sie Bilder in Dataset Studio, prüfen Sie die Qualität und erstellen Sie Beschreibungen.","Öffnen Sie unter Trainer eine kompatible Engine und richten Sie das Training ein. Ein Projekt startet kein Training automatisch.","Überwachen und steuern Sie Aufträge in der Warteschlange.","Unter Meine trainierten LoRAs sehen Sie die gespeicherten Ergebnisse.","Projekte öffnen"],
modules:["2. Aufbau und Funktionen","Dashboard: Schnellzugriff und Installationsstatus.","Projekte: Engine, Daten und Aktivitäten organisieren.","Trainer: Trainingswerkzeuge nach Modellfamilie.","Dataset Studio: nichtdestruktive Bildreferenzen, Prüfung, Vergleich und Beschriftungen.","Mehransichten-Studio: Ansichten, Abdeckung und Export.","GPU-Manager: Ressourcen, Speicher und Diagnose.","Warteschlange: Ausführung und Auftragssteuerung.","Einstellungen: GPU, Netzwerk und Betriebsmodus.","ComfyUI-Zone: Verbindung, Modelle, Workflows und Erzeugung nach Aktivierung."],
multiview:["3. Mehransichten: aus Fotos weitere Ansichten erzeugen","Wählen Sie ein Bildprojekt.","Erstellen Sie ein Motiv für das fotografierte Objekt.","Verknüpfen Sie im Fotowiederherstellungsbereich die Dataset-Studio-Fotos mit dem Motiv.","Lassen Sie unbekannte Winkel leer. Lokales Ollama kann Richtungen schätzen, aber keine gemessenen Winkel liefern.","Prüfen Sie Vergleich und Abdeckung. Sektoren ohne bekannten Azimut bleiben unbekannt.","Für eine fehlende Ansicht wählen Sie 1–4 echte Fotos und einen ComfyUI-Workflow mit LoadImage-Eingängen, weisen die Bilder zu und erzeugen ein synthetisches Bild.","Prüfen Sie das Ergebnis und importieren Sie es als synthetisch und ungeprüft. Exportieren Sie bei Bedarf eine ZIP-Datei.","KI kann verdeckte Details erfinden. Sie ersetzt keine Fotogrammetrie oder geometrische Messung.","Mehransichten öffnen"],
modes:["4. Betriebsmodi","Nur OrkiLab (eigenständig): Trainer, Dataset Studio, GPU, Projekte und Warteschlange bleiben verfügbar. ComfyUI-Werkzeuge werden ausgeblendet.","Mit ComfyUI: aktivieren Sie Verbindung und Workflows. Hybrid: kombinieren Sie OrkiLab-Training mit ComfyUI-Erzeugung. Ändern Sie den Modus in den Einstellungen ohne Datenverlust.","Ollama ist optional und von ComfyUI unabhängig. Es wird nicht automatisch installiert; für Fotoanalysen ist ein lokales Visionmodell nötig."],
faq:["Häufige Fragen","Warum fehlt mein Projekt im Mehransichten-Studio?","Das Projekt muss aktiv und von der Kategorie Bild sein. Archivierte Projekte werden nicht angezeigt.","Was bedeutet Dataset 8 Fotos / Mehransichten 0?","Die Fotos sind in Dataset Studio vorhanden, müssen aber mit einem neuen Motiv verknüpft werden. Sie werden nicht dupliziert.","Kann die KI den exakten Winkel messen?","Nein. Eine Blickrichtung ist nur geschätzt und kein gemessener Azimut. Lassen Sie unbekannte Winkel leer.","Warum wird keine neue Ansicht erzeugt?","Prüfen Sie ComfyUI-Verbindung, validierten Workflow und verbundene Bildeingänge.","Werden Originalbilder beim Entfernen von Referenzen gelöscht?","Nein. Referenzaktionen erhalten die Originale. Sichern Sie settings/orkilab vor größeren Änderungen.","Was tun, wenn der GPU-Speicher voll ist?","Prüfen Sie den GPU-Manager und Speichersteuerungen. Unterbrechen Sie keine fremden Aufgaben oder unbekannten Prozesse."]
},
it:{
hero:["ORKILAB / AIUTO 0.5.0 RC.1","Guida a OrkiLab","Esplora la struttura dell'applicazione, i progetti, i dati, l'addestramento e gli strumenti IA opzionali. Leggere questa guida non avvia workflow né scarica modelli."],
nav:["Primi passi","Moduli","Multivista","Modalità","Domande frequenti"],
flow:["1. Primi passi","In Progetti crea un progetto e scegli categoria e motore.","In Dataset Studio collega le immagini, controlla la qualità e prepara le descrizioni.","In Trainer apri un motore compatibile e configura l'addestramento. La creazione di un progetto non avvia alcun lavoro.","Nella Coda di lavoro monitora lo stato e gestisci le attività.","In I miei LoRA addestrati consulta i risultati salvati.","Apri progetti"],
modules:["2. Struttura e funzioni","Pannello: accesso rapido e stato dell'installazione.","Progetti: organizzazione di motori, dati e attività.","Trainer: strumenti di addestramento per famiglia di modelli.","Dataset Studio: riferimenti senza modificare gli originali, revisione, confronto e didascalie.","Studio multivista: punti di vista, copertura ed esportazione.","Gestore GPU: risorse, memoria e diagnostica.","Coda: esecuzione e controllo dei lavori.","Impostazioni: GPU, rete e modalità operativa.","Zona ComfyUI: connessione, modelli, workflow e generazione, se attivata."],
multiview:["3. Multivista: dalle foto a nuove viste","Seleziona un progetto di immagini.","Crea un soggetto per l'oggetto o la figura fotografata.","Nel recupero foto collega al soggetto le immagini di Dataset Studio.","Se non conosci gli angoli lasciali vuoti. Ollama locale suggerisce orientamenti, non gradi misurati.","Controlla confronto e copertura. I settori senza azimut restano sconosciuti.","Per Generare vista mancante scegli 1–4 foto reali e un workflow ComfyUI con ingressi LoadImage, assegnale e genera un'immagine sintetica.","Controlla il risultato prima di importarlo come sintetico e non approvato. Esporta il file ZIP quando necessario.","L'IA può inventare dettagli nascosti. Non sostituisce la fotogrammetria né le misurazioni geometriche.","Apri Multivista"],
modes:["4. Modalità operative","Solo OrkiLab (autonomo): trainer, Dataset Studio, GPU, progetti e coda restano disponibili. Gli strumenti ComfyUI vengono nascosti.","Con ComfyUI: abilita connessione e workflow. Ibrido: combina i trainer OrkiLab con la generazione ComfyUI. Cambia modalità nelle Impostazioni senza cancellare dati.","Ollama è opzionale e indipendente da ComfyUI. Non si installa automaticamente e richiede un modello visivo locale per analizzare le foto."],
faq:["Domande frequenti","Perché il progetto non compare in Multivista?","Deve essere attivo e di categoria Immagine; i progetti archiviati sono nascosti.","Cosa significa Dataset 8 foto / Multivista 0?","Le foto sono nel Dataset Studio, ma devi creare un soggetto e collegarle. Non vengono duplicate.","L'IA può misurare l'angolo esatto?","No, una direzione visuale è una stima, non un azimut misurato. Lascia vuoti gli angoli sconosciuti.","Perché non genera una nuova vista?","Controlla la connessione ComfyUI, un workflow validato e gli ingressi immagine collegati.","Gli originali vengono cancellati rimuovendo riferimenti?","No. Le azioni sui riferimenti preservano gli originali. Esegui un backup di settings/orkilab prima di modifiche importanti.","Cosa fare quando la memoria GPU è piena?","Usa Gestore GPU e i controlli memoria. Non interrompere lavori di altri utenti o processi sconosciuti."]
},
ja:{
hero:["ORKILAB / ヘルプ 0.5.0 RC.1","OrkiLab 利用ガイド","アプリの構成、プロジェクト、データ、学習、任意のAIツールについて説明します。このガイドを読むだけでワークフローが実行されたりモデルがダウンロードされたりすることはありません。"],
nav:["はじめに","モジュール","マルチビュー","モード","よくある質問"],
flow:["1. はじめに","プロジェクトで新しいプロジェクトを作成し、カテゴリとエンジンを選択します。","Dataset Studioで画像を参照登録し、品質を確認して説明文を準備します。","トレーナーで対応エンジンを開いて学習を設定します。プロジェクト作成だけでは学習は始まりません。","ジョブキューで進捗を確認し、作業を管理します。","学習済みLoRA一覧で結果を確認します。","プロジェクトを開く"],
modules:["2. 構成と機能","ダッシュボード：状態確認とショートカット。","プロジェクト：エンジン、データ、作業の整理。","トレーナー：モデルファミリーごとの学習ツール。","Dataset Studio：元画像を変更しない参照登録、レビュー、比較、説明文。","マルチビュースタジオ：視点、カバー率、エクスポート。","GPU管理：リソース、メモリ、診断。","ジョブキュー：実行とジョブ管理。","設定：GPU、ネットワーク、動作モード。","ComfyUIゾーン：有効時の接続、モデル、ワークフロー、生成機能。"],
multiview:["3. マルチビュー：写真から新しい視点へ","画像プロジェクトを選択します。","写真に写る物体や人物の被写体を作成します。","写真の復元画面でDataset Studioの画像を被写体に関連付けます。","不明な角度は空欄のままにします。ローカルOllamaは方向を推定できますが測定角度ではありません。","比較とカバー率を確認します。方位角が不明な範囲は未確認のままです。","不足視点の生成では、1～4枚の実写写真とLoadImage入力を持つComfyUIワークフローを選び、割り当てて合成画像を生成します。","結果を確認して合成・未承認として取り込み、必要に応じてZIPをエクスポートします。","AIは見えない部分を創作することがあります。写真測量や幾何学的測定の代わりにはなりません。","マルチビューを開く"],
modes:["4. 動作モード","OrkiLab単独モード：トレーナー、Dataset Studio、GPU、プロジェクト、ジョブキューを利用できます。ComfyUI専用機能は非表示になります。","ComfyUIモード：接続とワークフローを有効にします。ハイブリッド：OrkiLab学習とComfyUI生成を組み合わせます。設定でデータを削除せずに切り替えられます。","Ollamaは任意でComfyUIとは独立しています。自動インストールされず、写真分析にはローカル画像認識モデルが必要です。"],
faq:["よくある質問","プロジェクトがマルチビューに表示されないのはなぜですか？","画像カテゴリの有効なプロジェクトである必要があります。アーカイブ済みは表示されません。","Dataset 8枚 / マルチビュー0枚とは？","画像はDataset Studioにありますが、被写体を作成して関連付ける必要があります。複製はしません。","AIで正確な角度を測れますか？","いいえ。視覚的な方向は推定であり、測定方位角ではありません。不明な角度は空欄にします。","新しい視点が生成されないのはなぜですか？","ComfyUI接続、検証済みワークフロー、接続された画像入力を確認してください。","参照を削除すると元写真も削除されますか？","いいえ。元ファイルは保持されます。大きな変更の前にsettings/orkilabをバックアップしてください。","GPUメモリが足りないときは？","GPU管理とメモリ制御を確認してください。他の作業や不明なプロセスを停止しないでください。"]
},
ko:{
hero:["ORKILAB / 도움말 0.5.0 RC.1","OrkiLab 사용 가이드","앱 구조, 프로젝트, 데이터, 학습 및 선택적 AI 도구를 설명합니다. 이 가이드를 읽는 것만으로 워크플로가 실행되거나 모델이 다운로드되지 않습니다."],
nav:["시작하기","모듈","멀티뷰","모드","자주 묻는 질문"],
flow:["1. 시작하기","프로젝트에서 프로젝트를 만들고 범주와 엔진을 선택합니다.","Dataset Studio에서 이미지를 참조로 등록하고 품질을 검토하며 설명을 준비합니다.","트레이너에서 호환 엔진을 열고 학습을 설정합니다. 프로젝트를 만든다고 학습이 자동 시작되지는 않습니다.","작업 대기열에서 진행 상황을 확인하고 작업을 관리합니다.","학습된 LoRA 목록에서 저장된 결과를 확인합니다.","프로젝트 열기"],
modules:["2. 구성 및 기능","대시보드: 빠른 접근 및 설치 상태 확인.","프로젝트: 엔진, 데이터 및 활동 정리.","트레이너: 모델 계열별 학습 도구.","Dataset Studio: 원본을 변경하지 않는 이미지 참조, 검토, 비교 및 설명.","멀티뷰 스튜디오: 피사체 시점, 범위 및 내보내기.","GPU 관리자: 리소스, 메모리 및 진단.","작업 대기열: 실행 및 작업 관리.","설정: GPU, 네트워크 및 작동 모드.","ComfyUI 영역: 활성화 시 연결, 모델, 워크플로 및 생성."],
multiview:["3. 멀티뷰: 사진에서 새로운 시점으로","이미지 프로젝트를 선택합니다.","사진에 담긴 물체나 인물의 피사체를 만듭니다.","사진 복구에서 Dataset Studio 사진을 피사체에 연결합니다.","알 수 없는 각도는 비워 두세요. 로컬 Ollama가 방향을 추정할 수 있지만 측정 각도는 아닙니다.","비교와 커버리지를 확인합니다. 방위각이 알려지지 않은 구역은 계속 미확인 상태입니다.","누락된 시점 생성에서 실제 사진 1~4장과 LoadImage 입력이 있는 ComfyUI 워크플로를 선택해 연결한 뒤 합성 이미지를 생성합니다.","결과를 검토하고 합성·미승인으로 등록한 후 필요하면 ZIP을 내보냅니다.","AI는 보이지 않는 부분을 만들어낼 수 있습니다. 사진측량이나 기하학적 측정을 대신하지 않습니다.","멀티뷰 열기"],
modes:["4. 작동 모드","OrkiLab 단독 모드: 트레이너, Dataset Studio, GPU, 프로젝트 및 작업 대기열을 사용할 수 있습니다. ComfyUI 전용 도구는 숨겨집니다.","ComfyUI 모드: 연결과 워크플로를 활성화합니다. 하이브리드 모드: OrkiLab 학습과 ComfyUI 생성을 함께 사용합니다. 설정에서 데이터를 삭제하지 않고 전환할 수 있습니다.","Ollama는 선택 사항이며 ComfyUI와 별도입니다. 자동으로 설치되지 않고 사진 분석에는 로컬 비전 모델이 필요합니다."],
faq:["자주 묻는 질문","프로젝트가 멀티뷰에 보이지 않는 이유는?","활성 상태의 이미지 범주 프로젝트여야 합니다. 보관된 프로젝트는 보이지 않습니다.","Dataset 8장 / 멀티뷰 0장은 무엇인가요?","사진은 Dataset Studio에 있지만 피사체를 만들고 연결해야 합니다. 파일을 복제하지 않습니다.","AI가 정확한 각도를 측정할 수 있나요?","아니요. 시각적 방향은 추정값일 뿐 측정 방위각이 아닙니다. 모르는 각도는 비워 두세요.","새 시점이 생성되지 않는 이유는?","ComfyUI 연결, 검증된 워크플로 및 연결된 이미지 입력을 확인하세요.","참조를 제거하면 원본 사진도 삭제되나요?","아니요. 원본 파일은 보존됩니다. 중요한 변경 전에 settings/orkilab를 백업하세요.","GPU 메모리가 부족하면 어떻게 하나요?","GPU 관리자와 메모리 제어를 확인하세요. 다른 작업이나 알 수 없는 프로세스를 종료하지 마세요."]
}
};
const make=(tag,cls,value)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(value!==undefined)n.textContent=value;return n};
const addLink=(parent,href,text)=>{const n=make("a",null,text);n.href=href;parent.append(n)};
function renderAll(){
 const grid=document.querySelector(".orki-guide-body .grid");
 const main=document.querySelector(".orki-guide-body");
 if(!grid||!main)return;
 for(const [locale,d] of Object.entries(dictionary)){
  const hero=make("section","hero");hero.dataset.lang=locale;hero.hidden=true;
  hero.append(make("span","tag",d.hero[0]),make("h1",null,d.hero[1]),make("p",null,d.hero[2]));
  main.insertBefore(hero,main.querySelector(".sections"));
  const flow=make("article","panel");flow.dataset.lang=locale;flow.dataset.guideSection="flow";flow.hidden=true;
  flow.append(make("h2",null,d.flow[0]));const ol=make("ol");
  for(const line of d.flow.slice(1,6))ol.append(make("li",null,line));
  flow.append(ol);addLink(flow,"/workspace#projects",d.flow[6]);grid.append(flow);
  const modules=make("article","panel");modules.dataset.lang=locale;modules.dataset.guideSection="sections";modules.hidden=true;
  modules.append(make("h2",null,d.modules[0]));const ul=make("ul");
  for(const line of d.modules.slice(1))ul.append(make("li",null,line));
  modules.append(ul);grid.append(modules);
  const multi=make("article","panel");multi.dataset.lang=locale;multi.dataset.guideSection="multiview";multi.hidden=true;
  multi.append(make("h2",null,d.multiview[0]));const steps=make("ol");
  for(const line of d.multiview.slice(1,8))steps.append(make("li",null,line));
  multi.append(steps,make("p",null,d.multiview[8]));
  addLink(multi,"/workspace/multiview",d.multiview[9]);grid.append(multi);
  const modes=make("article","panel");modes.dataset.lang=locale;modes.dataset.guideSection="modes";modes.hidden=true;
  modes.append(make("h2",null,d.modes[0]));
  for(const line of d.modes.slice(1))modes.append(make("p",null,line));
  grid.append(modes);
  const faq=make("section","panel qa");faq.dataset.lang=locale;faq.dataset.guideSection="faq";faq.hidden=true;
  faq.append(make("h2",null,d.faq[0]));
  for(let i=1;i<d.faq.length;i+=2){const details=make("details");details.append(make("summary",null,d.faq[i]),make("p",null,d.faq[i+1]));faq.append(details)}
  main.append(faq);
 }
}
function updateGuide(){
 const current=typeof I18N!=="undefined"?I18N.lang:"es";
 const lang=["es","en",...Object.keys(dictionary)].includes(current)?current:"en";
 const anchors=["flow","sections","multiview","modes","faq"];
 for(const id of anchors){
  const old=document.getElementById(id);
  if(old&&!old.dataset.guideSection)old.dataset.guideSection=id;
 }
 for(const section of document.querySelectorAll(".orki-guide-body [data-lang]")){
  section.hidden=section.dataset.lang!==lang;
  if(section.dataset.guideSection)section.id=section.hidden?"":section.dataset.guideSection;
 }
 const nav=["Primeros pasos","Módulos","Multiview","Modos","Preguntas frecuentes"];
 const en=["Getting started","Modules","Multiview","Modes","FAQ"];
 document.querySelectorAll(".orki-guide-body .sections a").forEach((node,i)=>{
  node.textContent=lang==="es"?nav[i]:lang==="en"?en[i]:dictionary[lang].nav[i];
 });
 document.documentElement.lang=lang;
}
function init(){renderAll();updateGuide()}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
document.addEventListener("orkilab:language-changed",updateGuide);
})();

/* Shared, non-destructive OrkiLab navigation chrome for standalone Workspace tools.
   Never rewrites queue controls, image controls or their listeners. */
(function () {
    "use strict";
    // Every menu transition must begin at the top, not at the previous
    // section's scroll offset (including browser back/forward restoration).
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
    const goTop=()=>window.scrollTo(0,0);
    window.addEventListener("pageshow",goTop);
    document.addEventListener("click",event=>{
        if(event.defaultPrevented||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
        const link=event.target.closest?.(
            "#home-navigation a,#comfy-navigation a,.queue-sidebar a,.studio-navigation a"
        );
        if(link)goTop();
    });
    // Same item order as #home-navigation in GUI/workspace.html.
    const routes = [
        ["overview", "/workspace#overview", 1],
        ["projects", "/workspace#projects", 2],
        ["engines", "/workspace#engines", 3],
        ["gpu", "/workspace#gpu-manager", 5],
        ["settings", "/workspace?dialog=settings", null],
        ["shutdown", "/workspace?dialog=shutdown", null],
        ["queue", "/queue", 6],
        ["comfy", "/workspace/comfyui", 7],
        ["datasets", "/workspace/datasets", 4],
        ["multiview", "/workspace/multiview", null]
    ];
    const names = {
        en: ["Workspace", "Dashboard", "Projects", "Training engines", "Dataset Studio", "GPU Manager", "Job queue", "ComfyUI Zone", "Local AI workspace", "Open-source · Local-first", "Support OrkiLab"],
        es: ["Espacio de trabajo", "Panel general", "Proyectos", "Entrenadores", "Dataset Studio", "Gestor GPU", "Cola de trabajo", "Zona ComfyUI", "Entorno de IA local", "Código abierto · Primero local", "Apoya OrkiLab"],
        pt: ["Área de trabalho", "Painel geral", "Projetos", "Treinadores", "Dataset Studio", "Gestor GPU", "Fila de trabalhos", "Zona ComfyUI", "Área de IA local", "Código aberto · Local", "Apoiar OrkiLab"],
        fr: ["Espace de travail", "Tableau de bord", "Projets", "Entraîneurs", "Dataset Studio", "Gestion GPU", "File de travaux", "Zone ComfyUI", "Espace IA local", "Code ouvert · Local", "Soutenir OrkiLab"],
        de: ["Arbeitsbereich", "Übersicht", "Projekte", "Trainer", "Dataset Studio", "GPU-Manager", "Auftragswarteschlange", "ComfyUI-Bereich", "Lokaler KI-Arbeitsbereich", "Open Source · Lokal", "OrkiLab unterstützen"],
        it: ["Spazio di lavoro", "Dashboard", "Progetti", "Trainer", "Dataset Studio", "Gestione GPU", "Coda lavori", "Zona ComfyUI", "Spazio IA locale", "Open source · Locale", "Sostieni OrkiLab"],
        ja: ["ワークスペース", "ダッシュボード", "プロジェクト", "トレーナー", "Dataset Studio", "GPU管理", "ジョブキュー", "ComfyUIゾーン", "ローカルAI", "オープンソース・ローカル", "OrkiLabを支援"],
        ko: ["작업 공간", "대시보드", "프로젝트", "트레이너", "Dataset Studio", "GPU 관리자", "작업 대기열", "ComfyUI 영역", "로컬 AI", "오픈 소스 · 로컬 우선", "OrkiLab 후원"]
    };
    const multiviewLabel = {
        en:"Multiview Studio", es:"Estudio multivista", pt:"Estúdio multivista",
        fr:"Studio multivues", de:"Multiview-Studio", it:"Studio multivista",
        ja:"マルチビュースタジオ", ko:"멀티뷰 스튜디오"
    };
    const multiviewIntro = {
        en:"Organize real and synthetic reference photographs of a subject by viewpoint, angle and distance. Sources stay untouched.",
        es:"Organiza fotografías reales o sintéticas de un sujeto según vista, ángulo y distancia, sin modificar las imágenes originales.",
        pt:"Organize fotografias reais e sintéticas por vista, ângulo e distância, sem alterar os originais.",
        fr:"Classez des photographies réelles ou synthétiques par vue, angle et distance, sans modifier les originaux.",
        de:"Reale und synthetische Referenzbilder nach Blickwinkel und Abstand ordnen, ohne die Originale zu verändern.",
        it:"Organizza fotografie reali o sintetiche per vista, angolo e distanza senza modificare gli originali.",
        ja:"元画像を変更せず、被写体の写真を視点・角度・距離ごとに整理します。",
        ko:"원본을 수정하지 않고 실제·합성 사진을 시점, 각도, 거리별로 정리합니다."
    };
    function element(tag, cls, value) {
        const node = document.createElement(tag);
        if (cls) node.className = cls;
        if (value !== undefined) node.textContent = value;
        return node;
    }
    function link(to, label, cls) {
        const a = element("a", cls, label);
        a.href = to;
        return a;
    }
    function unifiedFooter(content, t) {
        let footer = content.querySelector(".orki-app-footer");
        if (!footer) {
            footer = element("footer", "orki-shell-footer orki-app-footer");
            content.append(footer);
        }
        footer.replaceChildren();
        const notice = element("span", null, "OrkiLab · " + t[9] + " · ");
        const home = link("/workspace", t[0]);
        const github = link("https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio", "GitHub", "orki-footer-github");
        github.target = "_blank";
        github.rel = "noopener noreferrer";
        footer.append(notice, home, document.createTextNode(" · "), github);
    }
    function placeVersionBelowMenu(nav, indicator) {
        if (!nav || !indicator) return;
        indicator.classList.add("orki-nav-version", "no-i18n");
        indicator.setAttribute("aria-label", "OrkiLab version");
        nav.append(indicator);
    }
    function renderWorkspaceChrome() {
        const body = document.body, home = document.querySelector("#home-navigation");
        const content = document.querySelector("#workspace-body");
        const header = document.querySelector("body > header");
        if (!home || !content || !header) return;
        body.classList.add("orki-app-frame", "orki-queue-theme");
        header.classList.add("orki-app-header", "orki-shell-header");
        home.classList.add("orki-app-nav");
        document.querySelector("#comfy-navigation")?.classList.add("orki-app-nav");
        document.querySelector("#workspace-context")?.classList.add("orki-app-context");
        const locale = typeof I18N !== "undefined" && names[I18N.lang] ? I18N.lang : "en";
        unifiedFooter(content, names[locale]);
        placeVersionBelowMenu(location.pathname.replace(/\/$/, "") === "/workspace/comfyui" ? document.querySelector("#comfy-navigation") : home, document.querySelector("#version"));
        // ComfyUI is a focused zone: ONLY its own navigation plus the
        // existing first "Back to Workspace" link in #comfy-navigation.
        // Never clone Home navigation into this area.
        const comfy = document.querySelector("#comfy-navigation");
        comfy?.querySelectorAll(".orki-global-nav").forEach(node => node.remove());
    }
    function render() {
        if (document.querySelector("#home-navigation")) {
            renderWorkspaceChrome();
            return;
        }
        const page = location.pathname === "/queue" ? "queue" : location.pathname === "/workspace/multiview" ? "multiview" : "datasets";
        const nav = document.querySelector(page === "queue" ? ".queue-sidebar" : ".studio-navigation");
        const content = document.querySelector(page === "queue" ? ".queue-shell .wrap" : ".studio-content");
        const layout = document.querySelector(page === "queue" ? ".queue-shell" : ".studio-layout");
        if (!nav || !content || !layout) return;
        const locale = typeof I18N !== "undefined" && names[I18N.lang] ? I18N.lang : "en";
        const t = names[locale];
        document.body.classList.add("orki-standalone-shell", "orki-app-frame", "orki-queue-theme");
        nav.classList.add("orki-app-nav");
        // Match Workspace's actual header: logo, language selector, version and Ko-fi.
        let head = document.querySelector(".orki-shell-header");
        if (!head) {
            head = element("header", "orki-shell-header");
            head.setAttribute("role", "banner");
            const brand = link("/workspace", "", "orki-shell-brand");
            const logo = element("img");
            logo.src = "/assets/orkilab/orkilab-logo-dark.svg";
            logo.alt = "OrkiLab";
            brand.append(logo);
            const tools = element("div", "orki-shell-side row");
            const languageLabel = element("label", "orki-shell-language");
            const languageText = element("span", null, "Language");
            languageText.id = "orki-shell-language-label";
            const selector = element("select", "no-i18n");
            selector.id = "orki-shell-language";
            selector.setAttribute("aria-labelledby", "orki-shell-language-label");
            languageLabel.append(languageText, selector);
            const version = element("span", "muted no-i18n", "OrkiLab");
            version.id = "orki-shell-version";
            const support = link("https://ko-fi.com/jorgelf", "♡ Ko-fi · Support OrkiLab", "orki-header-kofi no-i18n");
            support.title = "Voluntary support for the open-source OrkiLab project";
            support.target = "_blank";
            support.rel = "noopener noreferrer";
            tools.append(languageLabel, version, support);
            head.append(brand, tools);
            document.body.insertBefore(head, layout);
            if (typeof I18N !== "undefined" && Array.isArray(I18N.languages)) {
                for (const [code, label] of I18N.languages) selector.add(new Option(label, code));
                selector.value = I18N.lang;
            }
            selector.addEventListener("change", async () => {
                const previous = typeof I18N !== "undefined" ? I18N.lang : "en";
                selector.disabled = true;
                try {
                    const result = await fetch("/api/i18n", {
                        method: "POST", credentials: "same-origin",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({language: selector.value})
                    });
                    if (!result.ok) throw new Error("Could not change language");
                    location.reload();
                } catch (error) {
                    selector.value = previous;
                    selector.disabled = false;
                    const message = document.querySelector(".orki-shell-context-description");
                    if (message) { message.textContent = error.message; message.hidden = false; }
                }
            });
            fetch("/api/workspace/overview", {credentials:"same-origin"}).then(r => r.ok ? r.json() : null).then(info => {
                if (info && info.version) version.textContent = info.version;
            }).catch(() => {});
        }
        head.classList.add("orki-app-header");
        // Pre-rendered canonical header is interactive even if the Workspace
        // fetch fails; the later canonical clone will rebind its own controls.
        const readySelector=head.querySelector("#workspace-language");
        if(readySelector&&typeof I18N!=="undefined"&&!readySelector.options.length){
            for(const [code,label] of I18N.languages)readySelector.add(new Option(label,code));
            readySelector.value=I18N.lang;
            readySelector.addEventListener("change",async()=>{
                const previous=I18N.lang;readySelector.disabled=true;
                try{
                    const response=await fetch("/api/i18n",{method:"POST",credentials:"same-origin",
                        headers:{"Content-Type":"application/json"},
                        body:JSON.stringify({language:readySelector.value})});
                    if(!response.ok)throw Error("Language change failed");
                    location.reload();
                }catch(error){
                    readySelector.value=previous;
                    readySelector.disabled=false;
                }
            });
            fetch("/api/workspace/overview",{credentials:"same-origin"})
                .then(response=>response.ok?response.json():null)
                .then(data=>{const version=head.querySelector("#version");
                    if(version&&data?.version)version.textContent=data.version})
                .catch(()=>{});
        }
        const languageText = head.querySelector("#orki-shell-language-label");
        if (languageText) languageText.textContent = typeof I18N !== "undefined" ? I18N.translate("Language") : "Language";
        const selector = head.querySelector("#orki-shell-language");
        if (selector && typeof I18N !== "undefined") selector.value = I18N.lang;
        // Use the same contextual title-and-help pattern as #workspace-context.
        let context = content.querySelector(".orki-shell-workspace-context");
        if (!context) {
            context = element("section", "workspace-context orki-shell-workspace-context orki-app-context");
            const row = element("div", "row");
            const title = element("strong", "no-i18n");
            title.id = "orki-shell-context-title";
            const toggle = element("button");
            toggle.type = "button";
            toggle.id = "orki-shell-context-toggle";
            toggle.setAttribute("aria-expanded", "false");
            toggle.setAttribute("aria-controls", "orki-shell-context-description");
            const toggleLabel = element("span");
            toggleLabel.id = "orki-shell-context-toggle-label";
            const info = element("span", null, "ⓘ");
            info.setAttribute("aria-hidden", "true");
            toggle.append(toggleLabel, document.createTextNode(" "), info);
            row.append(title, toggle);
            const description = element("p", "muted no-i18n");
            description.id = "orki-shell-context-description";
            description.hidden = true;
            context.append(row, description);
            content.prepend(context);
            toggle.addEventListener("click", () => {
                const opened = description.hidden;
                description.hidden = !opened;
                toggle.setAttribute("aria-expanded", String(opened));
            });
        }
        const help = {
            en: ["What can I do here?", "Job queue", "See active, waiting and completed training jobs. Pause the queue, reorder pending tasks, monitor progress and review previous results.", "Dataset Studio", "Import images by reference, review datasets, analyze duplicates or blur, compare images and organize selections without deleting originals."],
            es: ["¿Qué puedo hacer aquí?", "Cola de trabajo", "Consulta trabajos en curso, pendientes y terminados. Pausa la cola, cambia el orden de las tareas, supervisa el progreso y revisa el historial.", "Dataset Studio", "Importa imágenes sin copiarlas, revisa datasets, analiza duplicados o desenfoque y compara imágenes sin borrar los archivos originales."],
            pt: ["O que posso fazer aqui?", "Fila de trabalhos", "Veja trabalhos ativos, pendentes e concluídos. Pause a fila, altere a ordem e consulte o progresso e o histórico.", "Dataset Studio", "Importe imagens por referência, reveja datasets e compare imagens sem apagar os originais."],
            fr: ["Que puis-je faire ici ?", "File de travaux", "Consultez les tâches actives, en attente et terminées. Mettez la file en pause et suivez la progression.", "Dataset Studio", "Importez et examinez vos images, détectez les doublons et comparez-les sans supprimer les originaux."],
            de: ["Was kann ich hier tun?", "Auftragswarteschlange", "Laufende, wartende und abgeschlossene Aufgaben ansehen, anhalten, sortieren und den Fortschritt prüfen.", "Dataset Studio", "Bilder importieren, Duplikate prüfen und vergleichen, ohne Originale zu löschen."],
            it: ["Cosa posso fare qui?", "Coda di lavoro", "Controlla i lavori attivi, in attesa e completati. Metti in pausa la coda e verifica l'avanzamento.", "Dataset Studio", "Importa, controlla e confronta le immagini senza eliminare gli originali."],
            ja: ["ここでは何ができますか？", "ジョブキュー", "進行中・待機中・完了したジョブの表示、順序変更、一時停止、進捗確認ができます。", "Dataset Studio", "元画像を削除せずに画像の取り込み、品質チェック、比較ができます。"],
            ko: ["여기서 무엇을 할 수 있나요?", "작업 대기열", "진행 중, 대기 중, 완료된 작업을 확인하고 일시정지, 순서 변경, 진행 상황을 확인하세요.", "Dataset Studio", "원본을 삭제하지 않고 이미지를 가져오고 품질을 확인하고 비교할 수 있습니다."]
        };
        const words = help[locale] || help.en;
        context.classList.add("orki-app-context");
        context.querySelector("#orki-shell-context-title").textContent = page === "queue" ? words[1] : page === "multiview" ? multiviewLabel[locale] : words[3];
        context.querySelector("#orki-shell-context-toggle-label").textContent = words[0];
        context.querySelector("#orki-shell-context-description").textContent = page === "queue" ? words[2] : page === "multiview" ? multiviewIntro[locale] : words[4];
        // Canonical source of truth: read the real Workspace chrome instead of
        // reconstructing a similar-looking but divergent header and menu.
        syncCanonicalWorkspaceChrome(page, nav, content);
        nav.setAttribute("aria-label", t[0]);
        // Complete fallback menu appears immediately, before /workspace is fetched.
        nav.replaceChildren();
        routes.forEach(([id, to, nameIndex]) => {
            const label = id === "multiview" ? multiviewLabel[locale] : id === "settings" ? (locale === "es" ? "Ajustes" : "Settings") :
                id === "shutdown" ? (locale === "es" ? "Pausar todo y salir" : "Pause all and exit") :
                t[nameIndex];
            const node = id === "settings" || id === "shutdown" ?
                element("button", "", label) : link(to, label, id === "comfy" || id === "datasets" ? "zone-entry" : "");
            if (node.tagName === "BUTTON") {
                node.type = "button";
                node.addEventListener("click", () => location.assign(to));
            }
            if (id === page) node.setAttribute("aria-current", "page");
            nav.append(node);
        });
        placeVersionBelowMenu(nav, document.querySelector("#version") || document.querySelector("#orki-shell-version"));
        unifiedFooter(content, t);
    }
    async function syncCanonicalWorkspaceChrome(page, nav, content) {
        try {
            const response = await fetch("/workspace", {credentials:"same-origin", cache:"no-store"});
            if (!response.ok) throw new Error("Workspace unavailable");
            const html = await response.text();
            const source = new DOMParser().parseFromString(html, "text/html");
            const canonicalHeader = source.querySelector("body > header");
            const canonicalNav = source.querySelector("#home-navigation");
            const canonicalContext = source.querySelector("#workspace-context");
            if (!canonicalHeader || !canonicalNav || !canonicalContext)
                throw new Error("Workspace chrome missing");
            // Clone exact markup, IDs and element order from Workspace.
            const liveHeader = document.querySelector(".orki-shell-header");
            if (liveHeader) {
                const header = canonicalHeader.cloneNode(true);
                header.classList.add("orki-shell-header", "orki-app-header");
                liveHeader.replaceWith(header);
                if (typeof I18N !== "undefined") I18N.apply(header);
                const selector = header.querySelector("#workspace-language");
                if (selector && typeof I18N !== "undefined") {
                    for (const [code, name] of I18N.languages) selector.add(new Option(name, code));
                    selector.value = I18N.lang;
                    selector.addEventListener("change", async () => {
                        const old = I18N.lang;
                        selector.disabled = true;
                        try {
                            const saved = await fetch("/api/i18n", {
                                method:"POST", credentials:"same-origin",
                                headers:{"Content-Type":"application/json"},
                                body:JSON.stringify({language:selector.value})
                            });
                            if (!saved.ok) throw new Error("Language change failed");
                            location.reload();
                        } catch (err) {
                            selector.value = old;
                            selector.disabled = false;
                            const alert = content.querySelector("#context-description");
                            if (alert) { alert.textContent = err.message; alert.hidden = false; }
                        }
                    });
                }
                fetch("/api/workspace/overview", {credentials:"same-origin"})
                    .then(r => r.ok ? r.json() : null)
                    .then(data => { if (data && data.version) {
                        const version = document.getElementById("version");
                        if (version) version.textContent = data.version;
                    } }).catch(() => {});
            }
            const canonical = canonicalNav.cloneNode(true);
            canonical.removeAttribute("id");
            canonical.className = (page === "queue" ? "queue-sidebar" : "studio-navigation") + " orki-app-nav";
            // Hash navigation must resolve to Workspace, not this standalone page.
            for (const a of canonical.querySelectorAll("a[href^='#']"))
                a.href = "/workspace" + a.getAttribute("href");
            const current = canonical.querySelector(page === "queue" ?
                'a[href="/queue"]' : page === "multiview" ?
                'a[href="/workspace/multiview"]' : 'a[href="/workspace/datasets"]');
            if (current) current.setAttribute("aria-current", "page");
            for (const button of canonical.querySelectorAll("button")) {
                const mode = button.id === "settings-open" ? "settings" :
                             button.id === "shutdown-open" ? "shutdown" : null;
                if (mode) {
                    button.addEventListener("click", () => {
                        location.href = "/workspace?dialog=" + mode;
                    });
                }
            }
            const versionInHeader = document.querySelector(".orki-shell-header #version");
            if (versionInHeader) {
                const prior = document.querySelector(".orki-nav-version");
                if (prior && prior !== versionInHeader) prior.remove();
                placeVersionBelowMenu(canonical, versionInHeader);
            }
            nav.replaceWith(canonical);
            if (typeof I18N !== "undefined") I18N.apply(canonical);
            const oldContext = content.querySelector(".orki-shell-workspace-context");
            if (oldContext) {
                const titleText = oldContext.querySelector("#orki-shell-context-title")?.textContent || "";
                const descriptionText = oldContext.querySelector("#orki-shell-context-description")?.textContent || "";
                const labelText = oldContext.querySelector("#orki-shell-context-toggle-label")?.textContent || "";
                const context = canonicalContext.cloneNode(true);
                const title = context.querySelector("#context-title");
                const description = context.querySelector("#context-description");
                const toggle = context.querySelector("#context-toggle");
                if (title) title.textContent = titleText;
                if (description) { description.textContent = descriptionText; description.hidden = true; }
                if (toggle) {
                    const span = toggle.querySelector("span");
                    if (span) span.textContent = labelText;
                    toggle.setAttribute("aria-expanded", "false");
                    toggle.addEventListener("click", () => {
                        if (!description) return;
                        const opened = description.hidden;
                        description.hidden = !opened;
                        toggle.setAttribute("aria-expanded", String(opened));
                    });
                }
                context.classList.add("orki-shell-workspace-context", "orki-app-context");
                oldContext.replaceWith(context);
            }
        } catch (error) {
            // Keep the existing shell usable if the standalone page was loaded
            // before Workspace became available; never break queue operations.
        }
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
    else render();
    document.addEventListener("orkilab:language-changed", render);
})();

"""Regression guard for ComfyUI Bridge postMessage serialization safety."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "integrations" / "orkilab_bridge" / "js" / "bridge.js"
GENERATION = ROOT / "scripts" / "generation_studio.py"
WORKSPACE = ROOT / "GUI" / "workspace.html"


class BridgeCloneSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge = BRIDGE.read_text(encoding="utf-8")
        cls.generation = GENERATION.read_text(encoding="utf-8")
        cls.workspace = WORKSPACE.read_text(encoding="utf-8")

    def test_graph_to_prompt_is_serialized_before_message(self):
        self.assertIn("const converted = await app.graphToPrompt();", self.bridge)
        self.assertIn("JSON.stringify(converted.output", self.bridge)
        self.assertIn("prompt = JSON.parse(serialized)", self.bridge)
        self.assertIn('opener.postMessage({type:"orkilab.result",token,prompt}, origin)', self.bridge)
        self.assertNotIn('prompt:converted.output', self.bridge)

    def test_non_json_errors_are_reported_safely(self):
        self.assertIn("Unsupported non-JSON value in converted prompt", self.bridge)
        self.assertIn("Cannot serialize ComfyUI prompt:", self.bridge)
        self.assertIn("Bridge failed at ", self.bridge)
        self.assertIn("console.error", self.bridge)
        self.assertIn('event.origin !== origin', self.bridge)
        self.assertIn('event.data?.token !== token', self.bridge)

    def test_stage_aware_diagnostics(self):
        for stage in ("loadGraphData (ComfyUI frontend)", "graphToPrompt (ComfyUI frontend)", "serialize converted prompt", "postMessage API prompt"):
            self.assertIn(stage, self.bridge)
        self.assertIn("Bridge failed sending workflow to ComfyUI:", self.workspace)
        self.assertIn("JSON.parse(JSON.stringify(w.graph))", self.workspace)

    def test_bridge_reports_progress_with_existing_origin_and_token(self):
        self.assertIn('opener.postMessage({type:"orkilab.progress",token,step},origin)', self.bridge)
        for step in ("received", "loading", "converting", "serializing", "returning"):
            self.assertIn('progress("' + step + '")', self.bridge)
        self.assertIn('e.origin!==target.origin||e.data?.token!==token', self.workspace)
        self.assertIn('e.data.type==="orkilab.progress"&&sent', self.workspace)
        self.assertIn('const allowed=["received","loading","converting","serializing","returning"]', self.workspace)

    def test_preparation_can_be_cancelled_without_submitting_generation(self):
        for snippet in (
            'id="bridge-cancel"',
            'const controller=new AbortController()',
            'bridgeAbort.abort()',
            'if(bridgeReject)bridgeReject(',
            'signal:controller.signal',
            'if(!popup.closed)popup.close()',
            'if(controller.signal.aborted)throw Error(',
            'showBridgeStep("validating")',
            'showBridgeStep("done")',
        ):
            self.assertIn(snippet, self.workspace)
        self.assertIn('id="bridge-progress-fill"', self.workspace)
        self.assertIn('id="bridge-progress-label"', self.workspace)
        self.assertIn('t("Step {current} of {total}"', self.workspace)

    def test_execution_progress_is_tied_to_submitted_prompt(self):
        for snippet in (
            'client_id = str(uuid.uuid4())',
            'return ident, client_id',
            'result = dict(id=token, prompt_id=ident, client_id=client_id)',
            'return jsonify(result), 201',
            'details.prompt_id!==runningGeneration.prompt_id',
            'executionSocket=new WebSocket(wsUrl.href)',
            'message.type==="executing"',
            'message.type==="progress"',
            'id="execution-progress"',
            'id="generation-cancel"',
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, self.generation + self.workspace)

    def test_cancel_targets_only_current_generation(self):
        for snippet in (
            '@app.post("/api/workspace/generation/<token>/cancel")',
            '"delete": [ident]',
            '{"prompt_id": ident}',
            'if len(running) != 1 or pending:',
            '"cancelling"',
            '"cancelled"',
            'Cannot safely interrupt while other ComfyUI jobs are present',
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, self.generation)
        self.assertNotIn('"clear": True', self.generation)
        self.assertIn('state NOT IN (\'completed\',\'error\',\'cancelled\')',
            (ROOT / "scripts" / "generation_history.py").read_text(encoding="utf-8"))

    def test_install_action_overwrites_bridge_code(self):
        self.assertIn('shutil.copyfile(source / rel, dst)', self.generation)
        self.assertIn('"js/bridge.js"', self.generation)


if __name__ == "__main__":
    unittest.main()

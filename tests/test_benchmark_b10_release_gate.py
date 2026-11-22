"""B10.5 release candidate gates must never be silently approved."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_b10_release_gate import summarize_b10_release_readiness


def report():
    return {
        "b9_closure": {"status":"not_fully_verified","checks":[{"code":"a","status":"pending"}]},
        "b10_comparison_preflight": {"gates":[{"code":"a","status":"pending"}],
                                     "comparison_execution_authorized":False},
        "b10_results":{"pairs":[{"status":"insufficient_measurements"}],
                       "ranking_eligible":False,"speedup_claim_allowed":False,
                       "best_variant":None},
    }


class B10ReleaseGateTests(unittest.TestCase):
    def test_valid_diagnostics_are_never_release_authorization(self):
        example=report()
        original=copy.deepcopy(example)
        result=summarize_b10_release_readiness(example)
        self.assertEqual(result["status"],"not_ready")
        self.assertEqual(result["diagnostic_status"],"diagnostics_present_unverified")
        for field in ("release_authorized","candidate_tag_authorized",
                      "merge_authorized","ranking_eligible","full_inference_verified",
                      "generation_submitted","database_modified"):
            self.assertFalse(result[field])
        self.assertIsNone(result["best_variant"])
        self.assertEqual(example,original)

    def test_manual_windows_linux_and_gpu_are_not_auto_verified(self):
        result=summarize_b10_release_readiness(report())
        by_code={item["code"]:item for item in result["checks"]}
        self.assertEqual(len(by_code),10)
        for code in ("windows_regression","linux_ci","comfyui_real_gpu",
                     "multilingual_mobile","explicit_release_authorization"):
            self.assertEqual(by_code[code]["status"],"pending")
        self.assertEqual(by_code["explicit_release_authorization"]["evidence_type"],
                         "maintainer")

    def test_explicit_b9_contradiction_blocks_review(self):
        sample=report()
        sample["b9_closure"]["status"]="contradiction_detected"
        result=summarize_b10_release_readiness(sample)
        self.assertEqual(result["diagnostic_status"],"review_blocked")
        self.assertEqual(result["checks"][0]["status"],"blocked")
        self.assertFalse(result["candidate_tag_authorized"])

    def test_unsafe_ranked_claim_blocks_review(self):
        for key,value in (("ranking_eligible",True),
                          ("best_variant","v2"),("speedup_claim_allowed",True)):
            sample=report()
            sample["b10_results"][key]=value
            result=summarize_b10_release_readiness(sample)
            self.assertEqual(result["diagnostic_status"],"review_blocked")
            self.assertFalse(result["merge_authorized"])

    def test_unsafe_submission_authorization_blocks_review(self):
        sample=report()
        sample["b10_comparison_preflight"]["comparison_execution_authorized"]=True
        self.assertEqual(
            summarize_b10_release_readiness(sample)["diagnostic_status"],
            "review_blocked",
        )

    def test_missing_section_or_wrong_structure_refused(self):
        for key in ("b9_closure","b10_comparison_preflight","b10_results"):
            sample=report()
            sample.pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):
                summarize_b10_release_readiness(sample)

    def test_wrong_input_type_refused(self):
        for sample in (None,{},[],{"b9_closure":[],"b10_results":{},
                                   "b10_comparison_preflight":{}}):
            with self.subTest(sample=sample),self.assertRaises(ValueError):
                summarize_b10_release_readiness(sample)


if __name__=="__main__":
    unittest.main()

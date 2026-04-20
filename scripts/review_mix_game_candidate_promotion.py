#!/usr/bin/env python3
"""Review blocked-family candidate batches for promotion readiness without promoting them."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validate_mix_game_candidate_batch import (
    build_candidate_result,
    build_payload as build_batch_payload,
    get_path_base,
    get_repo_root,
    load_batch_spec,
    resolve_candidate_path,
    resolve_registry_path,
    validate_candidate_entry_shape,
)
from validate_mix_game_candidate_family import load_json_object, validate_candidate


PROMOTION_REVIEW_VERSION = "1.0"

REVIEW_VERDICT_VOCABULARY = {
    "non_promotable_template_placeholder": "Candidate matches a blocked-family template while retaining template/non-grounding markers. It is not source evidence.",
    "non_promotable_wrong_family": "Candidate is readable but either fails family-native identity markers or carries excluded inherited assumptions.",
    "non_promotable_missing_required_markers_or_provenance": "Candidate is readable but missing required family markers, candidate-range fields, or provenance structure.",
    "family_shape_match_missing_grounding_evidence": "Candidate shape matches the family but exact source evidence, complete provenance, or status blockers still prevent promotion.",
    "promotion_candidate_pending_human_review": "Candidate mechanically passes shape and provenance checks. This is still advisory and requires a separate human source-evidence review before any status change.",
    "review_execution_error": "The batch spec, registry, candidate JSON, or validator invocation failed closed.",
}

VALIDATOR_TO_REVIEW_VERDICT = {
    "candidate_non_grounding_template_match": "non_promotable_template_placeholder",
    "rejected_wrong_family_markers": "non_promotable_wrong_family",
    "rejected_excluded_inherited_assumptions": "non_promotable_wrong_family",
    "rejected_missing_required_markers_or_provenance": "non_promotable_missing_required_markers_or_provenance",
    "shape_match_missing_grounding_evidence": "family_shape_match_missing_grounding_evidence",
    "shape_match_with_grounding_evidence_candidate": "promotion_candidate_pending_human_review",
    "invalid_candidate_json": "review_execution_error",
}


def count_bucket(bucket: Any) -> int:
    if not isinstance(bucket, dict):
        return 0
    return sum(len(values) for values in bucket.values() if isinstance(values, list))


def get_family_rule(registry: dict[str, Any], family_id: Any) -> dict[str, Any] | None:
    families = registry.get("families")
    if not isinstance(families, list):
        return None
    return next((entry for entry in families if isinstance(entry, dict) and entry.get("familyId") == family_id), None)


def summarize_missing_markers(missing_markers: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for category, values in sorted(missing_markers.items()):
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, dict):
                if "path" in value:
                    out.append(f"{category}: {value['path']}")
                elif "key" in value:
                    out.append(f"{category}: {value['key']}")
                elif "stage" in value:
                    out.append(f"{category}: {value['stage']}")
                else:
                    out.append(f"{category}: {json.dumps(value, sort_keys=True)}")
            else:
                out.append(f"{category}: {value}")
    return out


def flatten_matched_categories(matched_markers: dict[str, Any]) -> set[str]:
    return {
        category
        for category, values in matched_markers.items()
        if isinstance(values, list) and values
    }


def build_satisfied_checks(validation: dict[str, Any], family_rule: dict[str, Any] | None) -> list[dict[str, Any]]:
    if family_rule is None:
        return []
    matched_categories = flatten_matched_categories(validation.get("matchedMarkers", {}))
    out: list[dict[str, Any]] = []
    if not validation.get("wrongFamilyMarkers") and not validation.get("missingMarkers"):
        out.append(
            {
                "check": "family_native_payload_markers_present",
                "basis": "No wrong-family markers or missing required payload markers were reported.",
            }
        )
    if not validation.get("excludedAssumptionCollisions"):
        out.append(
            {
                "check": "excluded_inherited_assumptions_absent",
                "basis": "No excluded-assumption collisions were reported.",
            }
        )
    if not validation.get("provenanceGaps"):
        out.append(
            {
                "check": "minimum_retained_provenance_complete",
                "basis": "No provenance gaps were reported.",
            }
        )
    if not validation.get("statusBlockers"):
        out.append(
            {
                "check": "candidate_status_blockers_absent",
                "basis": "No template, blocked-status, or provenance status blockers were reported.",
            }
        )
    if "manifestTransformationStages" in matched_categories:
        out.append(
            {
                "check": "required_transformation_stages_present",
                "basis": "Required retained-source, intermediate, and normalized-pack stage markers were found by the validator.",
            }
        )
    if validation.get("verdict") == "shape_match_with_grounding_evidence_candidate":
        for check in family_rule.get("promotionAcceptanceChecks", []):
            out.append(
                {
                    "check": check,
                    "basis": "Satisfied by the current validator verdict plus zero wrong-family markers, missing markers, provenance gaps, and status blockers.",
                }
            )
    return out


def build_missing_checks(validation: dict[str, Any], family_rule: dict[str, Any] | None) -> list[dict[str, Any]]:
    checks = []
    promotion_checks = []
    if family_rule is not None:
        promotion_checks = list(family_rule.get("promotionAcceptanceChecks", []))

    if validation.get("errors"):
        checks.append(
            {
                "check": "candidate_json_or_validator_execution",
                "basis": list(validation.get("errors", [])),
            }
        )
    if validation.get("wrongFamilyMarkers"):
        checks.append(
            {
                "check": "family_native_payload_identity",
                "basis": validation["wrongFamilyMarkers"],
            }
        )
    if validation.get("missingMarkers"):
        checks.append(
            {
                "check": "required_family_markers_or_range_fields",
                "basis": summarize_missing_markers(validation["missingMarkers"]),
            }
        )
    if validation.get("excludedAssumptionCollisions"):
        checks.append(
            {
                "check": "excluded_inherited_assumptions_absent",
                "basis": [
                    {
                        "id": item.get("id"),
                        "path": item.get("path"),
                        "reason": item.get("reason"),
                    }
                    for item in validation["excludedAssumptionCollisions"]
                    if isinstance(item, dict)
                ],
            }
        )
    if validation.get("provenanceGaps"):
        checks.append(
            {
                "check": "minimum_retained_provenance_complete",
                "basis": validation["provenanceGaps"],
            }
        )
    if validation.get("statusBlockers"):
        checks.append(
            {
                "check": "candidate_non_grounding_status_removed",
                "basis": validation["statusBlockers"],
            }
        )

    if validation.get("verdict") != "shape_match_with_grounding_evidence_candidate":
        for check in promotion_checks:
            checks.append(
                {
                    "check": check,
                    "basis": "Not yet satisfied by the current validator verdict.",
                }
            )
    return checks


def build_next_required_evidence(
    validation: dict[str, Any],
    family_rule: dict[str, Any] | None,
    review_verdict: str,
) -> list[str]:
    if family_rule is None:
        return ["Provide a candidate familyId that exists in the blocked-family contract registry."]

    family_id = family_rule["familyId"]
    evidence: list[str] = []
    if review_verdict == "non_promotable_template_placeholder":
        evidence.append("Replace candidate_non_grounding pack/manifest templates with source-bearing candidate artifacts.")
    if validation.get("wrongFamilyMarkers"):
        evidence.append(f"Supply a candidate whose family-native markers match `{family_id}` rather than the grounded two-card pushfold family or another blocked family.")
    if validation.get("excludedAssumptionCollisions"):
        evidence.append("Remove or re-normalize excluded inherited assumptions before treating the candidate as family-native.")
    if validation.get("missingMarkers"):
        evidence.append("Populate every required family payload marker, candidate-range node key, and candidate-range entry key reported in missingMarkers.")
    if validation.get("provenanceGaps") or validation.get("statusBlockers"):
        evidence.append("Provide exact source path or reference, retained basis path, retrieval timestamp, source hash/linkage, normalized artifact hashes, and manifest-linked transformation stages.")
    if validation.get("errors"):
        evidence.append("Fix unreadable JSON, missing files, unsupported batch shape, or unknown family ids before promotion review can proceed.")
    if review_verdict == "promotion_candidate_pending_human_review":
        evidence.append("Run a separate human source-evidence audit and explicit family-status decision; this review does not auto-promote currentRepoStatus.")

    for deliverable in family_rule.get("normalizationDeliverables", []):
        evidence.append(f"Required deliverable: {deliverable}")
    return evidence


def review_one_candidate(
    *,
    entry: Any,
    index: int,
    registry: dict[str, Any],
    registry_path: Path,
    path_base: Path,
    batch_result: dict[str, Any] | None,
) -> dict[str, Any]:
    shape_errors = validate_candidate_entry_shape(entry, index)
    if shape_errors:
        candidate_id = entry.get("candidateId", f"<candidate-{index}>") if isinstance(entry, dict) else f"<candidate-{index}>"
        return {
            "candidateId": candidate_id,
            "familyId": entry.get("familyId") if isinstance(entry, dict) else None,
            "packPath": entry.get("packPath") if isinstance(entry, dict) else None,
            "manifestPath": entry.get("manifestPath") if isinstance(entry, dict) else None,
            "validatorVerdict": "invalid_candidate_json",
            "reviewVerdict": "review_execution_error",
            "currentRegistryStatus": None,
            "familyNativeDecisionUnit": None,
            "candidateSelectorAxes": [],
            "satisfiedPromotionChecks": [],
            "missingPromotionChecks": [{"check": "candidate_batch_entry_shape", "basis": shape_errors}],
            "statusBlockers": [],
            "excludedAssumptionCollisions": [],
            "wrongFamilyMarkers": [],
            "missingMarkers": {},
            "provenanceGaps": [],
            "nextRequiredEvidence": ["Fix the batch candidate entry shape so familyId, packPath, and manifestPath are present."],
            "promotionAcceptanceChecks": [],
            "reviewNotes": ["Review failed closed before candidate validation."],
            "batchResult": batch_result or {},
        }

    family_id = entry["familyId"]
    family_rule = get_family_rule(registry, family_id)
    pack_path = resolve_candidate_path(entry["packPath"], path_base)
    manifest_path = resolve_candidate_path(entry["manifestPath"], path_base)

    try:
        validation = validate_candidate(registry, family_id, pack_path, manifest_path, registry_path)
    except ValueError as exc:
        validation = {
            "familyId": family_id,
            "currentRegistryStatus": None,
            "packPath": str(pack_path),
            "manifestPath": str(manifest_path),
            "verdict": "invalid_candidate_json",
            "matchedMarkers": {},
            "wrongFamilyMarkers": [],
            "missingMarkers": {},
            "excludedAssumptionCollisions": [],
            "provenanceGaps": [],
            "statusBlockers": [],
            "errors": [str(exc)],
            "promotionAcceptanceChecks": [],
        }

    validator_verdict = validation.get("verdict", "invalid_candidate_json")
    review_verdict = VALIDATOR_TO_REVIEW_VERDICT.get(str(validator_verdict), "review_execution_error")
    if family_rule is None:
        review_verdict = "review_execution_error"

    return {
        "candidateId": entry["candidateId"],
        "familyId": family_id,
        "packPath": entry["packPath"],
        "manifestPath": entry["manifestPath"],
        "resolvedPackPath": str(pack_path),
        "resolvedManifestPath": str(manifest_path),
        "expectedValidatorVerdict": entry.get("expectedVerdict"),
        "validatorVerdict": validator_verdict,
        "reviewVerdict": review_verdict,
        "currentRegistryStatus": validation.get("currentRegistryStatus"),
        "familyNativeDecisionUnit": None if family_rule is None else family_rule.get("familyNativeDecisionUnit"),
        "candidateSelectorAxes": [] if family_rule is None else family_rule.get("candidateSelectorAxes", []),
        "satisfiedPromotionChecks": build_satisfied_checks(validation, family_rule),
        "missingPromotionChecks": build_missing_checks(validation, family_rule),
        "statusBlockers": validation.get("statusBlockers", []),
        "excludedAssumptionCollisions": validation.get("excludedAssumptionCollisions", []),
        "wrongFamilyMarkers": validation.get("wrongFamilyMarkers", []),
        "missingMarkers": validation.get("missingMarkers", {}),
        "provenanceGaps": validation.get("provenanceGaps", []),
        "promotionAcceptanceChecks": validation.get("promotionAcceptanceChecks", []),
        "nextRequiredEvidence": build_next_required_evidence(validation, family_rule, review_verdict),
        "reviewNotes": [
            "Promotion review is advisory only and does not mutate currentRepoStatus.",
            "A promotion_candidate_pending_human_review verdict still requires a separate human source-evidence review.",
        ],
        "batchResult": batch_result or {},
    }


def build_summary(reviews: list[dict[str, Any]], batch_payload: dict[str, Any]) -> dict[str, Any]:
    by_review = Counter(review.get("reviewVerdict", "review_execution_error") for review in reviews)
    by_validator = Counter(review.get("validatorVerdict", "invalid_candidate_json") for review in reviews)
    review_error_count = sum(1 for review in reviews if review.get("reviewVerdict") == "review_execution_error")
    promotion_candidate_count = by_review.get("promotion_candidate_pending_human_review", 0)
    false_positive_risk_count = promotion_candidate_count
    return {
        "totalCandidates": len(reviews),
        "byReviewVerdict": dict(sorted(by_review.items())),
        "byValidatorVerdict": dict(sorted(by_validator.items())),
        "reviewExecutionErrorCount": review_error_count,
        "promotionCandidatePendingHumanReviewCount": promotion_candidate_count,
        "nonPromotableCount": len(reviews) - promotion_candidate_count - review_error_count,
        "falsePositiveRiskCount": false_positive_risk_count,
        "batchValidatorStatus": batch_payload.get("status"),
        "batchValidatorExecutionErrorCount": batch_payload.get("summary", {}).get("executionErrorCount"),
    }


def build_coverage_limits(reviews: list[dict[str, Any]]) -> list[str]:
    has_shape_match = any(
        review.get("reviewVerdict") in {"family_shape_match_missing_grounding_evidence", "promotion_candidate_pending_human_review"}
        for review in reviews
        if isinstance(review, dict)
    )
    has_pending_human_review = any(
        review.get("reviewVerdict") == "promotion_candidate_pending_human_review"
        for review in reviews
        if isinstance(review, dict)
    )

    coverage_limits: list[str] = []
    if has_shape_match:
        coverage_limits.append(
            "At least one real family-shaped non-template blocked-family candidate exists in scope for this review run."
        )
    else:
        coverage_limits.append(
            "Current repo-local controls exercise template placeholders and grounded two-card negative controls only."
        )

    if has_pending_human_review:
        coverage_limits.append(
            "promotion_candidate_pending_human_review is exercised by a real blocked-family candidate in scope; a separate human source-evidence audit is still required before any family-status change."
        )
    else:
        coverage_limits.append(
            "No real provenance-complete blocked-family candidate exists in scope to exercise promotion_candidate_pending_human_review."
        )

    if has_shape_match and not has_pending_human_review:
        coverage_limits.append(
            "family_shape_match_missing_grounding_evidence is exercised by at least one real blocked-family candidate in scope."
        )
    elif has_pending_human_review:
        coverage_limits.append(
            "At least one real blocked-family candidate in scope exceeds family_shape_match_missing_grounding_evidence and reaches promotion_candidate_pending_human_review."
        )
    else:
        coverage_limits.append(
            "No real family-shaped non-template blocked-family candidate exists in scope to exercise family_shape_match_missing_grounding_evidence."
        )
    return coverage_limits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-spec", required=True, help="Batch spec JSON path, or '-' to read from stdin.")
    parser.add_argument(
        "--registry",
        default=str(Path(__file__).resolve().parents[1] / "out" / "_codex" / "mix_game_family_contract_registry.json"),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = resolve_registry_path(args.registry, repo_root)

    spec, spec_error, resolved_spec_path = load_batch_spec(args.batch_spec)
    if spec_error or spec is None:
        batch_payload = build_batch_payload(
            batch_spec_path=args.batch_spec,
            registry_path=registry_path,
            status="invalid_batch_spec",
            results=[],
            execution_errors=[spec_error or "unknown_batch_spec_error"],
        )
        payload = {
            "promotionReviewVersion": PROMOTION_REVIEW_VERSION,
            "batchSpecPath": args.batch_spec,
            "registryPath": str(registry_path),
            "batchId": None,
            "pathBase": None,
            "status": "invalid_batch_spec",
            "reviewVerdictVocabulary": REVIEW_VERDICT_VOCABULARY,
            "currentGroundingBoundary": {},
            "summary": build_summary([], batch_payload),
            "batchValidationSummary": batch_payload.get("summary", {}),
            "executionErrors": batch_payload.get("executionErrors", []),
            "reviews": [],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    registry, registry_error = load_json_object(registry_path)
    if registry_error or registry is None:
        batch_payload = build_batch_payload(
            batch_spec_path=str(resolved_spec_path or args.batch_spec),
            registry_path=registry_path,
            batch_id=spec.get("batchId"),
            path_base_label=spec.get("pathBase", "repo_root"),
            status="invalid_registry",
            results=[],
            execution_errors=[registry_error or "unknown_registry_error"],
        )
        payload = {
            "promotionReviewVersion": PROMOTION_REVIEW_VERSION,
            "batchSpecPath": str(resolved_spec_path or args.batch_spec),
            "registryPath": str(registry_path),
            "batchId": spec.get("batchId"),
            "pathBase": spec.get("pathBase", "repo_root"),
            "status": "invalid_registry",
            "reviewVerdictVocabulary": REVIEW_VERDICT_VOCABULARY,
            "currentGroundingBoundary": {},
            "summary": build_summary([], batch_payload),
            "batchValidationSummary": batch_payload.get("summary", {}),
            "executionErrors": batch_payload.get("executionErrors", []),
            "reviews": [],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    candidates = spec.get("candidates")
    if not isinstance(candidates, list):
        batch_payload = build_batch_payload(
            batch_spec_path=str(resolved_spec_path or args.batch_spec),
            registry_path=registry_path,
            batch_id=spec.get("batchId"),
            path_base_label=spec.get("pathBase", "repo_root"),
            status="invalid_batch_spec",
            results=[],
            execution_errors=["candidates missing_or_not_list"],
        )
        payload = {
            "promotionReviewVersion": PROMOTION_REVIEW_VERSION,
            "batchSpecPath": str(resolved_spec_path or args.batch_spec),
            "registryPath": str(registry_path),
            "batchId": spec.get("batchId"),
            "pathBase": spec.get("pathBase", "repo_root"),
            "status": "invalid_batch_spec",
            "reviewVerdictVocabulary": REVIEW_VERDICT_VOCABULARY,
            "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
            "summary": build_summary([], batch_payload),
            "batchValidationSummary": batch_payload.get("summary", {}),
            "executionErrors": batch_payload.get("executionErrors", []),
            "reviews": [],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    path_base, path_base_error = get_path_base(spec, resolved_spec_path, repo_root)
    if path_base_error or path_base is None:
        batch_payload = build_batch_payload(
            batch_spec_path=str(resolved_spec_path or args.batch_spec),
            registry_path=registry_path,
            batch_id=spec.get("batchId"),
            path_base_label=spec.get("pathBase", "repo_root"),
            status="invalid_batch_spec",
            results=[],
            execution_errors=[path_base_error or "unknown_path_base_error"],
        )
        payload = {
            "promotionReviewVersion": PROMOTION_REVIEW_VERSION,
            "batchSpecPath": str(resolved_spec_path or args.batch_spec),
            "registryPath": str(registry_path),
            "batchId": spec.get("batchId"),
            "pathBase": spec.get("pathBase", "repo_root"),
            "status": "invalid_batch_spec",
            "reviewVerdictVocabulary": REVIEW_VERDICT_VOCABULARY,
            "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
            "summary": build_summary([], batch_payload),
            "batchValidationSummary": batch_payload.get("summary", {}),
            "executionErrors": batch_payload.get("executionErrors", []),
            "reviews": [],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    batch_results = [
        build_candidate_result(entry, index, registry, registry_path, path_base)
        for index, entry in enumerate(candidates)
    ]
    batch_execution_errors = [
        {"candidateId": result.get("candidateId"), "errors": result.get("executionErrors", [])}
        for result in batch_results
        if result.get("executionErrors")
    ]
    if batch_execution_errors:
        batch_status = "completed_with_errors"
    elif any(result.get("expectedVerdictMatched") is False for result in batch_results):
        batch_status = "completed_with_expected_verdict_mismatches"
    else:
        batch_status = "ok"
    batch_payload = build_batch_payload(
        batch_spec_path=str(resolved_spec_path or args.batch_spec),
        registry_path=registry_path,
        batch_id=spec.get("batchId"),
        path_base_label=spec.get("pathBase", "repo_root"),
        status=batch_status,
        results=batch_results,
        execution_errors=batch_execution_errors,
    )

    reviews = [
        review_one_candidate(
            entry=entry,
            index=index,
            registry=registry,
            registry_path=registry_path,
            path_base=path_base,
            batch_result=batch_results[index] if index < len(batch_results) else None,
        )
        for index, entry in enumerate(candidates)
    ]
    summary = build_summary(reviews, batch_payload)
    status = "ok"
    if summary["reviewExecutionErrorCount"] or batch_payload.get("status") not in {"ok", "completed_with_expected_verdict_mismatches"}:
        status = "completed_with_review_errors"

    payload = {
        "promotionReviewVersion": PROMOTION_REVIEW_VERSION,
        "batchSpecPath": str(resolved_spec_path or args.batch_spec),
        "registryPath": str(registry_path),
        "batchId": spec.get("batchId"),
        "pathBase": spec.get("pathBase", "repo_root"),
        "status": status,
        "reviewVerdictVocabulary": REVIEW_VERDICT_VOCABULARY,
        "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
        "summary": summary,
        "batchValidationSummary": batch_payload.get("summary", {}),
        "executionErrors": batch_payload.get("executionErrors", []),
        "coverageLimits": build_coverage_limits(reviews),
        "reviews": reviews,
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Parse PreflopAdvisor-style PLO hand tokens into UI-facing candidate buckets."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ZIP = Path(
    "out/_private/mix_game_candidate_sources/cc_high_4card/"
    "preflopadvisor_hu100bb_with_limp/"
    "preflopadvisor_37031d059b892606174a2b6ad0eb08477ac8b055.zip"
)
DEFAULT_RNG_PATH = "ranges/HU-100bb-with-limp/0.rng"
RANKS = "AKQJT98765432"
RANK_SORT_INDEX = {rank: index for index, rank in enumerate(RANKS)}
RANK_VALUE = {rank: len(RANKS) - 1 - index for index, rank in enumerate(RANKS)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Parse PreflopAdvisor/Monker-style PLO exact hand tokens and derive "
            "candidate bucket metadata for the repo's PLO v1 UI work."
        )
    )
    parser.add_argument(
        "--token",
        action="append",
        default=[],
        help="One exact hand token to parse. Repeat to parse multiple tokens.",
    )
    parser.add_argument(
        "--source-zip",
        default=str(DEFAULT_SOURCE_ZIP),
        help="Retained source zip used when summarizing a .rng file.",
    )
    parser.add_argument(
        "--rng-path",
        default=DEFAULT_RNG_PATH,
        help="Path inside the zip to the .rng file used for summary mode.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Summarize every token from the selected .rng file.",
    )
    parser.add_argument(
        "--pdf-suited-only",
        action="store_true",
        help="Keep only DS / SS / R tokens in summary mode to match the PDF coverage.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level.",
    )
    return parser.parse_args()


def extract_rank_groups(token: str) -> tuple[str, list[str], list[str]]:
    suited_groups = re.findall(r"\(([^)]+)\)", token)
    bare_ranks = re.sub(r"\([^)]*\)", "", token)
    if len(bare_ranks) + sum(len(group) for group in suited_groups) != 4:
        raise ValueError(f"unsupported token shape: {token}")
    return bare_ranks, suited_groups, list(bare_ranks + "".join(suited_groups))


def suitedness_family(suited_groups: list[str]) -> str:
    group_lengths = tuple(len(group) for group in suited_groups)
    if not suited_groups:
        return "R"
    if group_lengths == (2,):
        return "SS"
    if group_lengths == (2, 2):
        return "DS"
    if group_lengths == (3,):
        return "TRI"
    if group_lengths == (4,):
        return "QUAD"
    return "OTHER"


def rank_profile(ranks: list[str]) -> tuple[str, Counter[str]]:
    counts = Counter(ranks)
    multiplicities = sorted(counts.values(), reverse=True)
    profile_map = {
        (1, 1, 1, 1): "4-distinct",
        (2, 1, 1): "1-pair",
        (2, 2): "2-pair",
        (3, 1): "trips",
        (4,): "quads",
    }
    return profile_map.get(tuple(multiplicities), "other"), counts


def highest_pair_rank(rank_counts: Counter[str]) -> str | None:
    pair_ranks = [rank for rank, count in rank_counts.items() if count >= 2]
    if not pair_ranks:
        return None
    return min(pair_ranks, key=lambda rank: RANK_SORT_INDEX[rank])


def rundown_gap_count(ranks: list[str]) -> int | None:
    if len(set(ranks)) != 4 or "A" in ranks:
        return None
    values = sorted((RANK_VALUE[rank] for rank in ranks), reverse=True)
    return (values[0] - values[-1] + 1) - 4


def pdf_v1_bucket_candidate(ranks: list[str], rank_counts: Counter[str]) -> str:
    top_pair = highest_pair_rank(rank_counts)
    if top_pair is not None:
        if top_pair == "A":
            return "AA"
        if top_pair == "K":
            return "KK"
        if top_pair == "Q":
            return "QQ"
        if top_pair == "J":
            return "JJ"
        if top_pair == "T":
            return "TT"
        if top_pair in {"9", "8", "7", "6"}:
            return "99_66"
        return "55_22"

    if "A" in rank_counts:
        side_ranks = [rank for rank in ranks if rank != "A"]
        if all(rank in {"K", "Q", "J", "T"} for rank in side_ranks):
            return "A_KT"
        if all(rank in {"9", "8", "7", "6"} for rank in side_ranks):
            return "A_96"
        if all(rank in {"5", "4", "3", "2"} for rank in side_ranks):
            return "A_52"
        return "OTHER_A"

    gap_count = rundown_gap_count(ranks)
    if gap_count == 0:
        return "0G"
    if gap_count == 1:
        return "1G"
    if gap_count == 2:
        return "2G"
    return "OTHER"


def parse_token(token: str) -> dict[str, Any]:
    bare_ranks, suited_groups, ranks = extract_rank_groups(token)
    suitedness = suitedness_family(suited_groups)
    profile, rank_counts = rank_profile(ranks)
    gap_count = rundown_gap_count(ranks)
    return {
        "token": token,
        "bareRanks": bare_ranks,
        "suitedGroups": suited_groups,
        "ranks": ranks,
        "rankProfile": profile,
        "rankCounts": dict(sorted(rank_counts.items(), key=lambda item: RANK_SORT_INDEX[item[0]])),
        "containsAce": "A" in rank_counts,
        "suitednessFamily": suitedness,
        "pdfSourceCompatibleSuitedness": suitedness in {"DS", "SS", "R"},
        "rundownGapCountCandidate": gap_count,
        "rundownBucketCandidate": None if gap_count is None else f"{gap_count}G" if gap_count <= 2 else "OTHER",
        "pdfV1BucketCandidate": pdf_v1_bucket_candidate(ranks, rank_counts),
    }


def load_tokens_from_rng(source_zip: Path, rng_path: str) -> list[str]:
    with zipfile.ZipFile(source_zip) as zf:
        zip_entry_name = rng_path
        if zip_entry_name not in zf.namelist():
            matches = [name for name in zf.namelist() if name.endswith(rng_path)]
            if len(matches) != 1:
                raise KeyError(f"could not resolve rng path inside zip: {rng_path}")
            zip_entry_name = matches[0]
        raw = zf.read(zip_entry_name).decode("utf-8", "replace").splitlines()
    return raw[0::2]


def summarize_tokens(tokens: list[str], *, pdf_suited_only: bool) -> dict[str, Any]:
    parsed = [parse_token(token) for token in tokens]
    if pdf_suited_only:
        parsed = [item for item in parsed if item["pdfSourceCompatibleSuitedness"]]

    suitedness_counts = Counter(item["suitednessFamily"] for item in parsed)
    rank_profile_counts = Counter(item["rankProfile"] for item in parsed)
    bucket_counts = Counter(item["pdfV1BucketCandidate"] for item in parsed)
    bucket_by_suitedness = Counter(
        (item["pdfV1BucketCandidate"], item["suitednessFamily"]) for item in parsed
    )

    return {
        "tokenCount": len(parsed),
        "tokenCountKind": "exact_token_classes_not_weighted_combos",
        "pdfSuitedOnly": pdf_suited_only,
        "suitednessCounts": dict(sorted(suitedness_counts.items())),
        "rankProfileCounts": dict(sorted(rank_profile_counts.items())),
        "pdfV1BucketCounts": dict(
            sorted(bucket_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        "pdfV1BucketBySuitedness": [
            {"bucket": bucket, "suitedness": suitedness, "tokenCount": count}
            for (bucket, suitedness), count in sorted(
                bucket_by_suitedness.items(),
                key=lambda item: (item[0][0], item[0][1]),
            )
        ],
    }


def main() -> int:
    args = parse_args()

    if args.token:
        parsed_tokens = [parse_token(token) for token in args.token]
        payload: Any = parsed_tokens[0] if len(parsed_tokens) == 1 else parsed_tokens
        print(json.dumps(payload, indent=args.indent, sort_keys=False))
        return 0

    if not args.summary:
        raise SystemExit("choose --token or --summary")

    tokens = load_tokens_from_rng(Path(args.source_zip), args.rng_path)
    summary = summarize_tokens(tokens, pdf_suited_only=args.pdf_suited_only or False)
    print(json.dumps(summary, indent=args.indent, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

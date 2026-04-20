#!/usr/bin/env python3
"""Materialize retained PokerTips strategy articles into family-shaped blocked-family candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1.0"
TEMPLATE_VERSION = "0.1"
TEMPLATE_STATUS = "materialized_retained_source_grounding_evidence_candidate"
CANDIDATE_STATUS = "family_shaped_retained_source_candidate_with_grounding_evidence"
LICENSE_LABEL = "copyright_notice_only_all_rights_reserved"
REDISTRIBUTION_NOTE = (
    "Retained from a public PokerTips strategy article whose footer states copyright 2025 "
    "PokerTips.org, all rights reserved; downstream redistribution beyond repo-local review "
    "remains a user review item."
)
RETAINED_BASIS_TYPE = "html_strategy_article"
DEFAULT_REGISTRY = "out/_codex/mix_game_family_contract_registry.json"


FAMILY_CONFIGS: dict[str, dict[str, Any]] = {
    "stud_high": {
        "candidate_dir": "out/_private/mix_game_candidate_staging/stud_high/pokertips_7_card_stud_strategy",
        "family_slug": "stud_high",
        "source_name": "PokerTips 7 Card Stud strategy article",
        "game_form": "7 Card Stud",
        "article_note": (
            "Materialized from retained PokerTips 7 Card Stud article sections into "
            "practical heuristic nodes for a family-shaped stud_high candidate."
        ),
        "meta_updates": {
            "gameForm": "7 Card Stud",
            "familyId": "stud_high",
            "streetModel": "stud",
            "street": "3rd",
            "potResolutionModel": "high_only_single_pot",
            "privateCardCountAtDecision": 3,
            "lifecyclePrivateCardCount": 7,
            "bringInModel": "not_specified_in_source_article",
            "seatModel": "stud_order",
            "visibleCardModel": "up_cards_visible_article_context",
            "deadCardModel": "exposed_opponent_cards_discussed_qualitatively",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "family_identity_updates": {
            "gameForm": "7 Card Stud",
            "familyId": "stud_high",
            "streetModel": "stud",
            "street": "3rd",
            "potResolutionModel": "high_only_single_pot",
            "privateCardCountAtDecision": 3,
            "lifecyclePrivateCardCount": 7,
            "bringInModel": "not_specified_in_source_article",
            "seatModel": "stud_order",
            "visibleCardModel": "up_cards_visible_article_context",
            "deadCardModel": "exposed_opponent_cards_discussed_qualitatively",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "node_specs": [
            {
                "heading": "Starting Hands",
                "decisionNodeId": "starting_hands",
                "street": "3rd",
                "bringInModel": "not_specified_in_source_article",
                "actingSeatOrRole": "not_specified_in_source_article_context",
                "actingOrderState": "position_sensitive_pre_completion_discussion",
                "visibleDeadSnapshot": "qualitative_exposed_cards_and_outs_discussion",
                "doorCardContext": "section::starting_hands",
                "openPathOrFacingCompletion": "first_voluntary_bet_section_guidance",
                "practical_entries": [
                    {
                        "heuristicId": "tighten_early_loosen_late",
                        "scenarioLabel": "Early positions need full three-card quality; late unopened spots can lean more on the up card",
                        "recommendedAction": "tighten_early_opening_requirements",
                        "actionClass": "context_dependent_open_or_fold",
                        "appliesWhen": [
                            "Third-street stud-high starting hands before the bring-in is heavily contested",
                            "Comparing early-left-of-bring-in seats against later unopened seats",
                        ],
                        "adjustOrFoldWhen": [
                            "In early positions all three cards matter and the opening bar should be tighter",
                            "In later unopened spots a strong up card can be enough to complete more often",
                            "Facing a completion and a raise, require a pretty strong three-card hand",
                        ],
                        "rationale": "The source makes position the first filter for whether a stud-high starter is playable or merely cosmetic.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                    {
                        "heuristicId": "rolled_up_jam",
                        "scenarioLabel": "Rolled-up third street start",
                        "recommendedAction": "raise_and_reraise_aggressively",
                        "actionClass": "fast_play_monster",
                        "appliesWhen": [
                            "Your first three cards are three-of-a-kind on third street",
                        ],
                        "adjustOrFoldWhen": [],
                        "rationale": "The source calls rolled-up the best starting hand in Stud and explicitly recommends piling money in.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 2}],
                    },
                    {
                        "heuristicId": "live_outs_draw_starters",
                        "scenarioLabel": "Good stud draw starters stay playable only while their outs are live",
                        "recommendedAction": "play_good_pairs_flushes_or_connectors_when_outs_are_live",
                        "actionClass": "play_or_fold_by_live_outs",
                        "appliesWhen": [
                            "High pair, concealed pair, three-flush, or three-straight style starter",
                        ],
                        "adjustOrFoldWhen": [
                            "Downgrade or fold flush and straight draws when multiple relevant outs are already exposed",
                        ],
                        "rationale": "The source explicitly ties these starters to how many suit or straight outs are visible in other players' up cards.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 3}],
                    },
                    {
                        "heuristicId": "three_high_cards_context",
                        "scenarioLabel": "Three broadway-style high cards are playable unopened but fold to heavy third-street strength",
                        "recommendedAction": "complete_unopened_fold_vs_completion_and_raise",
                        "actionClass": "conditional_complete_or_fold",
                        "appliesWhen": [
                            "Three high cards such as A-K down with J up in an unopened pot",
                        ],
                        "adjustOrFoldWhen": [
                            "Fold when facing both a completion and a raise",
                            "Complete the bring-in when there is no action and you can realize high-pair potential",
                        ],
                        "rationale": "The source gives an explicit three-high-card example with opposite advice depending on prior third-street aggression.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 4}],
                    },
                ],
            },
            {
                "heading": "Bluffing",
                "decisionNodeId": "bluffing",
                "street": "3rd",
                "bringInModel": "not_specified_in_source_article",
                "actingSeatOrRole": "aggressor_after_completion_example",
                "actingOrderState": "heads_up_or_multiway_after_completion_discussion",
                "visibleDeadSnapshot": "fourth_street_coordination_discussed_qualitatively",
                "doorCardContext": "section::bluffing",
                "openPathOrFacingCompletion": "completion_bluff_example",
                "practical_entries": [
                    {
                        "heuristicId": "heads_up_fourth_street_barrel",
                        "scenarioLabel": "Continue a third-street representation bluff mainly in heads-up pots when villain bricks fourth street",
                        "recommendedAction": "continue_bluff_on_fourth_street_when_villain_bricks",
                        "actionClass": "conditional_second_barrel",
                        "appliesWhen": [
                            "You completed or raised on third street to represent strength",
                            "Exactly one caller remains",
                            "The caller's fourth-street up card does not coordinate with their visible board",
                        ],
                        "adjustOrFoldWhen": [
                            "Give up more often once two or more players continue unless your own hand improves considerably",
                            "Slow down when the caller's fourth-street card clearly improves pair, straight, or flush potential",
                        ],
                        "rationale": "The source explicitly anchors bluff continuation to player count and how well the new up card connects with the opponent's visible structure.",
                        "sourceRefs": [
                            {"kind": "paragraph", "ordinal": 1},
                            {"kind": "bullet", "ordinal": 1},
                            {"kind": "bullet", "ordinal": 2},
                            {"kind": "paragraph", "ordinal": 2},
                        ],
                    },
                    {
                        "heuristicId": "heads_up_aggressor_pressure",
                        "scenarioLabel": "As the heads-up aggressor, pressure visible brick cards",
                        "recommendedAction": "bet_again_when_opponent_catches_uncoordinated_upcard",
                        "actionClass": "heads_up_pressure_bet",
                        "appliesWhen": [
                            "Heads-up stud pot after you showed aggression earlier in the hand",
                            "Opponent catches a card that does not seem to fit their visible hand story",
                        ],
                        "adjustOrFoldWhen": [
                            "Do not auto-fire when the new up card obviously strengthens their visible pair, draw, or made-hand line",
                        ],
                        "rationale": "The source closes by stating that heads-up aggressors can often win simply by betting when the opponent's new up card appears to miss.",
                        "sourceRefs": [
                            {"kind": "paragraph", "ordinal": 2},
                            {"kind": "paragraph", "ordinal": 3},
                        ],
                    },
                ],
            },
        ],
        "normalization_notes": [
            "The normalized candidate converts retained article prose into actionable heuristic entries rather than leaving the source as unstructured section text.",
            "Each heuristic preserves exact paragraph and bullet references so practical-use summaries remain auditable against the retained HTML basis.",
            "Selector values the article does not specify remain explicitly labeled as not_specified_in_source_article rather than being invented for convenience.",
        ],
        "extra_manifest_notes": [
            "Only article sections aligned to starting-hand and completion/bluff guidance were promoted into practical heuristic nodes.",
            "Later-street details mentioned inside the retained article remain inside rawLeaf evidence and were not expanded into unsupported exact range tables or separate node families.",
        ],
    },
    "stud_low_razz": {
        "candidate_dir": "out/_private/mix_game_candidate_staging/stud_low_razz/pokertips_razz_strategy",
        "family_slug": "stud_low_razz",
        "source_name": "PokerTips Razz strategy article",
        "game_form": "Razz",
        "article_note": (
            "Materialized from retained PokerTips Razz article sections into "
            "practical heuristic nodes for a family-shaped stud_low_razz candidate."
        ),
        "meta_updates": {
            "gameForm": "Razz",
            "familyId": "stud_low_razz",
            "streetModel": "stud",
            "street": "3rd",
            "potResolutionModel": "low_only_single_pot",
            "lowDirectionRule": "ace_to_five",
            "privateCardCountAtDecision": 3,
            "lifecyclePrivateCardCount": 7,
            "bringInModel": "lowest_upcard_bring_in_implied_by_article",
            "seatModel": "stud_order",
            "visibleCardModel": "up_cards_visible_article_context",
            "deadCardModel": "exposed_opponent_cards_discussed_qualitatively",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "family_identity_updates": {
            "gameForm": "Razz",
            "familyId": "stud_low_razz",
            "streetModel": "stud",
            "street": "3rd",
            "potResolutionModel": "low_only_single_pot",
            "lowDirectionRule": "ace_to_five",
            "privateCardCountAtDecision": 3,
            "lifecyclePrivateCardCount": 7,
            "bringInModel": "lowest_upcard_bring_in_implied_by_article",
            "seatModel": "stud_order",
            "visibleCardModel": "up_cards_visible_article_context",
            "deadCardModel": "exposed_opponent_cards_discussed_qualitatively",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "node_specs": [
            {
                "heading": "Position, Starting Hands and Outs",
                "decisionNodeId": "position_starting_hands_and_outs",
                "street": "3rd",
                "bringInModel": "lowest_upcard_bring_in_implied_by_article",
                "lowDirectionRule": "ace_to_five",
                "actingSeatOrRole": "not_specified_in_source_article_context",
                "actingOrderState": "position_relative_to_bring_in_discussed",
                "visibleDeadSnapshot": "qualitative_up_cards_and_outs_discussion",
                "doorCardContext": "section::position_starting_hands_and_outs",
                "facingAction": "third_street_starting_hand_guidance",
                "practical_entries": [
                    {
                        "heuristicId": "open_wider_late_than_early",
                        "scenarioLabel": "Open wider when action folds around toward the right of the bring-in",
                        "recommendedAction": "tighten_immediately_left_loosen_when_folds_reach_you",
                        "actionClass": "position_sensitive_opening",
                        "appliesWhen": [
                            "Comparing seats immediately left of the bring-in against later seats after folds",
                        ],
                        "adjustOrFoldWhen": [
                            "Immediately left of the bring-in needs a materially stronger start",
                            "As fewer players remain, you can raise with somewhat weaker razz hands",
                        ],
                        "rationale": "The source explicitly maps Razz starting-hand quality to how many players remain between you and the bring-in.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                    {
                        "heuristicId": "five_or_six_high_premium",
                        "scenarioLabel": "Five-high or better razz starts are premium; six-high is still comfortably playable",
                        "recommendedAction": "raise_or_reraise_with_five_high_or_better",
                        "actionClass": "aggressive_open_or_reraise",
                        "appliesWhen": [
                            "Unpaired Razz start whose highest card is five or lower",
                        ],
                        "adjustOrFoldWhen": [
                            "Six-high starts are usually still playable even from early position",
                            "Seven-high starts become more conditional on position and live outs",
                        ],
                        "rationale": "The source gives explicit practical thresholds at five-high, six-high, and seven-high.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 2}],
                    },
                    {
                        "heuristicId": "four_five_seven_visibility_rule",
                        "scenarioLabel": "Use visible low-card blockers before continuing with 4-5 down, 7 up style starts",
                        "recommendedAction": "play_only_when_low_outs_are_mostly_live",
                        "actionClass": "visibility_threshold_decision",
                        "appliesWhen": [
                            "Early-position hand similar to 4-5 down with 7 up",
                            "Zero or one of A, 2, 3, or 6 is exposed in opponents' up cards",
                        ],
                        "adjustOrFoldWhen": [
                            "Two exposed blockers makes the spot questionable",
                            "Three or more exposed blockers should usually become a fold",
                        ],
                        "rationale": "The source gives concrete blocker thresholds instead of a vague 'be careful with dead cards' warning.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 3}],
                    },
                    {
                        "heuristicId": "track_upcards_first",
                        "scenarioLabel": "Visible opponent cards matter at least as much as your own cards",
                        "recommendedAction": "audit_upcards_before_continuing",
                        "actionClass": "foundational_visibility_check",
                        "appliesWhen": [
                            "Any Razz continuation or opening decision where live low cards determine hand quality",
                        ],
                        "adjustOrFoldWhen": [
                            "Do not evaluate your hand in isolation from opponents' up cards",
                        ],
                        "rationale": "The source frames visible-card tracking as the difference between losing and winning Razz players.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 4}],
                    },
                ],
            }
        ],
        "normalization_notes": [
            "The normalized candidate converts retained Razz article prose into actionable heuristic entries instead of leaving the source as a flat paragraph dump.",
            "Each heuristic preserves exact paragraph references so practical-use summaries remain auditable against the retained HTML basis.",
            "The retained article implies low-door bring-in structure, but exact bring-in sizing and seat labels are not specified and remain labeled accordingly.",
        ],
        "extra_manifest_notes": [
            "The retained article directly states ace-to-five low-only rules and no low qualifier; those semantics are carried as family markers.",
            "Only the section aligned to starting-hand, position, and outs guidance was promoted into practical heuristic nodes in this pass.",
        ],
    },
    "stud_hilo": {
        "candidate_dir": "out/_private/mix_game_candidate_staging/stud_hilo/pokertips_7_card_stud_hi_lo_strategy",
        "family_slug": "stud_hilo",
        "source_name": "PokerTips 7 Card Stud Hi/Lo strategy article",
        "game_form": "7 Card Stud Hi/Lo",
        "article_note": (
            "Materialized from retained PokerTips 7 Card Stud Hi/Lo article sections into "
            "practical heuristic nodes for a family-shaped stud_hilo candidate."
        ),
        "meta_updates": {
            "gameForm": "7 Card Stud Hi/Lo",
            "familyId": "stud_hilo",
            "streetModel": "stud",
            "street": "3rd",
            "potResolutionModel": "hi_lo_split_pot",
            "privateCardCountAtDecision": 3,
            "lifecyclePrivateCardCount": 7,
            "bringInModel": "not_specified_in_source_article",
            "splitRule": "hi_lo_split_pot",
            "lowQualifierRule": "eight_or_better",
            "seatModel": "stud_order",
            "visibleCardModel": "up_cards_visible_article_context",
            "deadCardModel": "exposed_opponent_cards_discussed_qualitatively",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "family_identity_updates": {
            "gameForm": "7 Card Stud Hi/Lo",
            "familyId": "stud_hilo",
            "streetModel": "stud",
            "street": "3rd",
            "potResolutionModel": "hi_lo_split_pot",
            "privateCardCountAtDecision": 3,
            "lifecyclePrivateCardCount": 7,
            "bringInModel": "not_specified_in_source_article",
            "splitRule": "hi_lo_split_pot",
            "lowQualifierRule": "eight_or_better",
            "seatModel": "stud_order",
            "visibleCardModel": "up_cards_visible_article_context",
            "deadCardModel": "exposed_opponent_cards_discussed_qualitatively",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "node_specs": [
            {
                "heading": "Starting Hands",
                "decisionNodeId": "starting_hands",
                "street": "3rd",
                "bringInModel": "not_specified_in_source_article",
                "splitRule": "hi_lo_split_pot",
                "lowQualifierRule": "eight_or_better",
                "actingSeatOrRole": "not_specified_in_source_article_context",
                "actingOrderState": "starting_hand_selection_discussed",
                "visibleDeadSnapshot": "qualitative_exposed_cards_discussion",
                "doorCardContext": "section::starting_hands",
                "facingAction": "third_street_starting_hand_guidance",
                "practical_entries": [
                    {
                        "heuristicId": "avoid_middle_cards",
                        "scenarioLabel": "Avoid 9-T-J style starts that are trapped between the high and low halves",
                        "recommendedAction": "downgrade_or_fold_middle_card_starts_without_strong_backup",
                        "actionClass": "starting_hand_rejection_rule",
                        "appliesWhen": [
                            "Third-street Stud Hi/Lo starts built around Nines, Tens, or many Jacks",
                        ],
                        "adjustOrFoldWhen": [
                            "Treat these cards as low-disqualified and usually too weak to own the high half by themselves",
                        ],
                        "rationale": "The source explicitly calls these cards 'no man's land' because they miss both halves of the game too often.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                    {
                        "heuristicId": "ace_low_three_card_premium",
                        "scenarioLabel": "Ace-plus-wheel starts are premium split-pot starters",
                        "recommendedAction": "play_aggressively_with_ace_low_three_card_starts",
                        "actionClass": "premium_split_pot_open",
                        "appliesWhen": [
                            "Start contains an Ace plus supporting wheel cards, such as A-5 down with 3 up",
                        ],
                        "adjustOrFoldWhen": [
                            "Value rises when the hand also carries concealed high backup like an Ace or flush potential",
                        ],
                        "rationale": "The source gives A-5 down with 3 up as a very good example because it can win both halves.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                ],
            },
            {
                "heading": "Three to a Low",
                "decisionNodeId": "three_to_a_low",
                "street": "3rd",
                "bringInModel": "not_specified_in_source_article",
                "splitRule": "hi_lo_split_pot",
                "lowQualifierRule": "eight_or_better",
                "actingSeatOrRole": "not_specified_in_source_article_context",
                "actingOrderState": "low_draw_evaluation_discussed",
                "visibleDeadSnapshot": "qualitative_outs_and_remaining_players_discussion",
                "doorCardContext": "section::three_to_a_low",
                "facingAction": "third_street_low_draw_guidance",
                "practical_entries": [
                    {
                        "heuristicId": "three_to_low_checklist",
                        "scenarioLabel": "Do not auto-play every three-to-a-low start; run the checklist first",
                        "recommendedAction": "evaluate_low_quality_players_and_dead_outs_before_continue",
                        "actionClass": "pre_commit_checklist",
                        "appliesWhen": [
                            "Holding three to a low on third street in Stud Hi/Lo",
                        ],
                        "adjustOrFoldWhen": [
                            "Ask how low the draw is",
                            "Count how many players remain",
                            "Count how many low outs are already gone",
                        ],
                        "rationale": "The source explicitly turns this family into a three-question decision process rather than an automatic continue.",
                        "sourceRefs": [
                            {"kind": "paragraph", "ordinal": 1},
                            {"kind": "bullet", "ordinal": 1},
                            {"kind": "bullet", "ordinal": 2},
                            {"kind": "bullet", "ordinal": 3},
                        ],
                    },
                    {
                        "heuristicId": "weak_eight_low_fold_rule",
                        "scenarioLabel": "Weak eight-low draws should usually fold when real low competition or dead outs are visible",
                        "recommendedAction": "fold_weak_eight_low_draws_when_low_competition_exists",
                        "actionClass": "conditional_fold_or_attack",
                        "appliesWhen": [
                            "Weak three-to-a-low hand like 8-6 down with 4 up",
                        ],
                        "adjustOrFoldWhen": [
                            "Fold more often when low cards such as A, 2, 3, or 5 are showing in other hands",
                            "Continue or even raise only when most visible up cards are high and you are likely the lone low draw",
                        ],
                        "rationale": "The source gives a concrete weak eight-low example and tells you to pivot based on whether the low side is contested.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 2}],
                    },
                    {
                        "heuristicId": "made_low_freeroll_pressure",
                        "scenarioLabel": "Once you likely own the low half, pressure high-only opponents aggressively",
                        "recommendedAction": "bet_and_raise_made_lows_aggressively",
                        "actionClass": "freeroll_pressure",
                        "appliesWhen": [
                            "You have a made low and are likely the only qualifying low at showdown",
                            "Or two other players appear to be fighting for the high half",
                        ],
                        "adjustOrFoldWhen": [
                            "Avoid being the high-only caller against an aggressive made-low player unless you are very sure of the high half",
                        ],
                        "rationale": "The source repeatedly recommends pushing money in when you are freerolling the low half and others are contesting only the high side.",
                        "sourceRefs": [
                            {"kind": "paragraph", "ordinal": 3},
                            {"kind": "paragraph", "ordinal": 4},
                        ],
                    },
                ],
            },
        ],
        "normalization_notes": [
            "The normalized candidate converts retained split-pot article prose into actionable heuristic entries instead of leaving the source as a flat section dump.",
            "Each heuristic preserves exact paragraph and bullet references so practical-use summaries remain auditable against the retained HTML basis.",
            "Split-pot and eight-or-better qualifier semantics are carried explicitly in family markers and node fields.",
        ],
        "extra_manifest_notes": [
            "Only the retained sections aligned to starting-hand and low-draw guidance were promoted into practical heuristic nodes.",
            "High-side-only advice remains visible in the retained article but is not expanded into unsupported exact range tables or separate node families in this pass.",
        ],
    },
    "draw_triple_low": {
        "candidate_dir": "out/_private/mix_game_candidate_staging/draw_triple_low/pokertips_2_7_triple_draw_strategy",
        "family_slug": "draw_triple_low",
        "source_name": "PokerTips 2-7 Triple Draw strategy article",
        "game_form": "2-7 Triple Draw",
        "article_note": (
            "Materialized from retained PokerTips 2-7 Triple Draw article sections into "
            "practical heuristic nodes for a family-shaped draw_triple_low candidate."
        ),
        "meta_updates": {
            "gameForm": "2-7 Triple Draw",
            "familyId": "draw_triple_low",
            "drawModel": "triple_draw",
            "potResolutionModel": "low_only_single_pot",
            "lowSystem": "deuce_to_seven",
            "seatModel": "position_relative_to_button_or_heads_up_article_context",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "family_identity_updates": {
            "gameForm": "2-7 Triple Draw",
            "familyId": "draw_triple_low",
            "drawModel": "triple_draw",
            "potResolutionModel": "low_only_single_pot",
            "lowSystem": "deuce_to_seven",
            "seatModel": "position_relative_to_button_or_heads_up_article_context",
            "practicalUseModel": "actionable_article_heuristics",
        },
        "node_specs": [
            {
                "heading": "Starting Hands and Position",
                "decisionNodeId": "starting_hands_and_position",
                "drawRound": "opening_round_pre_first_draw_guidance",
                "remainingDraws": "3",
                "lowSystem": "deuce_to_seven",
                "patDrawState": "mixed_pat_and_drawing_starting_hand_guidance",
                "actingSeatOrOrder": "early_or_late_position_discussed",
                "facingAction": "first_entry_open_or_fold_guidance",
                "practical_entries": [
                    {
                        "heuristicId": "early_pat_or_one_card_away_threshold",
                        "scenarioLabel": "Early position wants a pat seven-or-eight or a hand that is one card away from strong",
                        "recommendedAction": "open_early_only_with_pat_or_near_pat_strength",
                        "actionClass": "early_position_strength_threshold",
                        "appliesWhen": [
                            "Opening round in early position before the first draw in 2-7 Triple Draw",
                        ],
                        "adjustOrFoldWhen": [
                            "Treat discard-two opens as rare exceptions rather than default continues",
                            "Do not lower the early-position bar just because the game is folded so far",
                        ],
                        "rationale": "The source explicitly says early position should start from a pat seven/eight or a hand that is one card away from strong.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                    {
                        "heuristicId": "early_discard_two_whitelist",
                        "scenarioLabel": "Early-position discard-two raises are limited to wheel-heavy starts such as 234 through 238",
                        "recommendedAction": "raise_only_whitelisted_discard_two_starts_from_early_position",
                        "actionClass": "discard_two_exception_rule",
                        "appliesWhen": [
                            "You would need to discard two cards from early position on the opening round",
                        ],
                        "adjustOrFoldWhen": [
                            "Hands outside 234, 235, 236, 237, or 238 should generally not be raised from early position",
                        ],
                        "rationale": "The source gives an explicit early-position whitelist instead of a vague preference for smooth discard-two hands.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                    {
                        "heuristicId": "button_pressure_open",
                        "scenarioLabel": "When folded to the button, late-position pressure can override raw card quality",
                        "recommendedAction": "raise_very_wide_when_folded_to_button",
                        "actionClass": "late_position_steal",
                        "appliesWhen": [
                            "Action folds to you on the button in a late-position opening spot",
                        ],
                        "adjustOrFoldWhen": [
                            "Expect blinds to fold often enough that immediate fold equity is part of the line",
                            "Prepare follow-up plans for single-blind calls rather than treating the open as all-in commitment",
                        ],
                        "rationale": "The source states that button opens can be raised regardless of cards because the blinds fold often enough.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 2}],
                    },
                    {
                        "heuristicId": "pat_nine_by_opponent_draw_count",
                        "scenarioLabel": "With position, decide whether a nine low stands pat by watching how many cards villain draws",
                        "recommendedAction": "stand_pat_vs_multi_card_draw_break_nine_vs_one_card_draw",
                        "actionClass": "position_informed_pat_decision",
                        "appliesWhen": [
                            "You hold a rough pat nine such as 9-7-5-3-2 and act after seeing the opponent draw",
                        ],
                        "adjustOrFoldWhen": [
                            "Consider standing pat when the opponent draws two or more cards",
                            "Break the nine more often when the opponent draws only one card and is likely already close",
                        ],
                        "rationale": "The source uses a nine-low example to show that draw-count visibility should directly change the keep-or-break decision.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 3}],
                    },
                ],
            },
            {
                "heading": "Bluffing and Value-Betting",
                "decisionNodeId": "bluffing_and_value_betting",
                "drawRound": "post_second_draw_or_third_draw_guidance",
                "remainingDraws": "1_or_0_discussed",
                "lowSystem": "deuce_to_seven",
                "patDrawState": "pat_vs_pat_or_pat_vs_draw_example",
                "actingSeatOrOrder": "heads_up_or_out_of_position_discussed",
                "facingAction": "bet_check_or_bluff_guidance",
                "practical_entries": [
                    {
                        "heuristicId": "final_round_oop_polar_bet",
                        "scenarioLabel": "Out of position in one-card versus one-card final-round spots, polarize between strong hands and total misses",
                        "recommendedAction": "bet_strong_hands_and_garbage_check_call_middle_showdown_value",
                        "actionClass": "final_round_polar_strategy",
                        "appliesWhen": [
                            "Heads-up or near-heads-up third-draw spot out of position",
                            "Both players drew one card on the last draw",
                        ],
                        "adjustOrFoldWhen": [
                            "Bet total garbage that cannot win at showdown",
                            "Check-call middling bluff-catchers like rough king-lows more often than betting them",
                        ],
                        "rationale": "The source gives an explicit final-round polar strategy instead of a generic reminder to bluff sometimes.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                    {
                        "heuristicId": "widen_bluffs_vs_super_passive",
                        "scenarioLabel": "Against super-passive opponents, widen the bluff bucket and shrink the check-call bucket",
                        "recommendedAction": "increase_bluff_frequency_reduce_passive_bluff_catches",
                        "actionClass": "opponent_profile_adjustment",
                        "appliesWhen": [
                            "Final betting round in one-card versus one-card spots against a very passive opponent",
                        ],
                        "adjustOrFoldWhen": [
                            "If villain rarely bets without a monster, convert more weak showdown hands into bluffs",
                            "Check-call less often when passive opponents under-bluff missed draws",
                        ],
                        "rationale": "The source explicitly carves out a passive-opponent adjustment rather than leaving the final-round plan static.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
                    },
                    {
                        "heuristicId": "second_draw_pat_probe",
                        "scenarioLabel": "When both players stand pat on the second draw and villain checks, bet almost always",
                        "recommendedAction": "probe_after_mutual_pat_and_check",
                        "actionClass": "pat_vs_pat_probe_bet",
                        "appliesWhen": [
                            "A player stood pat on the second draw",
                            "You also stood pat",
                            "That player checks to you before the river draw or final betting decision resolves",
                        ],
                        "adjustOrFoldWhen": [
                            "Bet your very strong made lows for value",
                            "Also bet medium-strength eights, nines, and tens to represent stronger pat hands",
                        ],
                        "rationale": "The source recommends near-auto-betting in this exact pat-versus-pat check-to-you configuration.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 2}],
                    },
                    {
                        "heuristicId": "bet_sets_up_easy_check_behind",
                        "scenarioLabel": "Probe-betting rough made hands can push worse pats into folding or breaking and simplify the river",
                        "recommendedAction": "bet_rough_made_lows_to_pressure_worse_pat_hands",
                        "actionClass": "representation_and_future_street_leverage",
                        "appliesWhen": [
                            "You hold a rough made hand such as a bad eight, nine, or ten after both players stand pat",
                        ],
                        "adjustOrFoldWhen": [
                            "Expect some worse pat tens to fold or call and break",
                            "Use the probe to create a cleaner check-behind option later when called",
                        ],
                        "rationale": "The source highlights both immediate fold equity and the downstream river simplification gained by betting rough made hands here.",
                        "sourceRefs": [{"kind": "paragraph", "ordinal": 2}],
                    },
                ],
            },
        ],
        "normalization_notes": [
            "The normalized candidate converts retained triple-draw article prose into actionable heuristic entries instead of leaving the source as a flat section dump.",
            "The retained article directly states deuce-to-seven lowball semantics; those semantics are carried explicitly in family markers.",
            "Each heuristic preserves exact paragraph references so practical-use summaries remain auditable against the retained HTML basis.",
        ],
        "extra_manifest_notes": [
            "Only article sections aligned to opening-round and later-round betting guidance were promoted into practical heuristic nodes.",
            "Hand-ranking and opponent-profile sections remain in the retained article but were not expanded into unsupported additional node families or exact range tables in this pass.",
        ],
    },
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(path_arg: str, root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return root / path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def slugify(text: str) -> str:
    out: list[str] = []
    previous_was_sep = False
    for char in text.lower():
        if char.isalnum():
            out.append(char)
            previous_was_sep = False
            continue
        if not previous_was_sep:
            out.append("_")
        previous_was_sep = True
    return "".join(out).strip("_")


def clean_text(text: str) -> str:
    return " ".join(text.split())


class ArticleSectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_article = False
        self.capture_tag: str | None = None
        self.capture_text: list[str] = []
        self.current_heading: str | None = None
        self.current_section: dict[str, Any] | None = None
        self.sections: list[dict[str, Any]] = []
        self._item_counts: dict[str, dict[str, int]] = {}
        self.article_title: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "article":
            self.in_article = True
        if not self.in_article:
            return
        if tag in ("h1", "h2", "h3", "p", "li"):
            self.capture_tag = tag
            self.capture_text = []

    def handle_endtag(self, tag: str) -> None:
        if self.in_article and self.capture_tag == tag:
            text = clean_text(" ".join(self.capture_text))
            if text:
                if tag in ("h1", "h2", "h3"):
                    if tag == "h1":
                        self.article_title = text
                    self.current_heading = text
                    self.current_section = {
                        "heading": text,
                        "headingSlug": slugify(text),
                        "level": tag,
                        "items": [],
                    }
                    self.sections.append(self.current_section)
                    self._item_counts[text] = {"p": 0, "li": 0}
                else:
                    heading = self.current_heading or "lead"
                    if self.current_section is None:
                        self.current_section = {
                            "heading": heading,
                            "headingSlug": slugify(heading),
                            "level": "lead",
                            "items": [],
                        }
                        self.sections.append(self.current_section)
                        self._item_counts.setdefault(heading, {"p": 0, "li": 0})
                    self._item_counts[heading][tag] += 1
                    ordinal = self._item_counts[heading][tag]
                    self.current_section["items"].append(
                        {
                            "kind": "paragraph" if tag == "p" else "bullet",
                            "kindTag": tag,
                            "ordinal": ordinal,
                            "text": text,
                        }
                    )
            self.capture_tag = None
            self.capture_text = []
        if tag == "article":
            self.in_article = False

    def handle_data(self, data: str) -> None:
        if self.in_article and self.capture_tag is not None:
            self.capture_text.append(data)


def load_seeded_html_source(candidate: dict[str, Any], candidate_dir: Path) -> tuple[Path, dict[str, Any]]:
    seeded = candidate.get("seededSourceSummary")
    if not isinstance(seeded, dict):
        raise ValueError("candidate.json missing seededSourceSummary")
    sources = seeded.get("sources")
    if not isinstance(sources, list):
        raise ValueError("candidate.json seededSourceSummary.sources missing_or_not_list")
    for item in sources:
        if not isinstance(item, dict):
            continue
        retained_path = item.get("retainedPath")
        if isinstance(retained_path, str) and retained_path.endswith(".html"):
            return candidate_dir / retained_path, item
    raise ValueError("candidate.json seededSourceSummary does not contain a retained HTML source")


def parse_article_sections(html_text: str) -> dict[str, Any]:
    parser = ArticleSectionParser()
    parser.feed(html_text)
    sections = [
        section
        for section in parser.sections
        if section.get("heading") not in (None, "Table of Contents")
        and section.get("items")
    ]
    if not sections:
        raise ValueError("no article sections with body items were parsed from retained HTML")
    return {
        "articleTitle": parser.article_title or "PokerTips strategy article",
        "sections": sections,
    }


def find_section(parsed: dict[str, Any], heading: str) -> dict[str, Any]:
    for section in parsed["sections"]:
        if section["heading"] == heading:
            return section
    raise ValueError(f"required article heading missing: {heading}")


def index_section_items(section: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (item["kind"], item["ordinal"]): item
        for item in section["items"]
    }


def resolve_source_items(section: dict[str, Any], refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    item_index = index_section_items(section)
    resolved: list[dict[str, Any]] = []
    for ref in refs:
        key = (ref["kind"], ref["ordinal"])
        if key not in item_index:
            raise ValueError(
                f"missing source item for heading={section['heading']} kind={ref['kind']} ordinal={ref['ordinal']}"
            )
        item = item_index[key]
        resolved.append(
            {
                "kind": item["kind"],
                "ordinal": item["ordinal"],
                "text": item["text"],
            }
        )
    return resolved


def build_intermediate_payload(
    *,
    family_id: str,
    config: dict[str, Any],
    parsed: dict[str, Any],
    html_rel: str,
    html_sha: str,
) -> dict[str, Any]:
    used_headings = {item["heading"] for item in config["node_specs"]}
    sections_payload: list[dict[str, Any]] = []
    for node_spec in config["node_specs"]:
        section = find_section(parsed, node_spec["heading"])
        items_payload = []
        for item in section["items"]:
            item_slug = f"{section['headingSlug']}::{item['kind']}_{item['ordinal']:02d}"
            items_payload.append(
                {
                    "entryId": item_slug,
                    "kind": item["kind"],
                    "ordinal": item["ordinal"],
                    "text": item["text"],
                }
            )
        heuristics_payload = []
        for heuristic in node_spec.get("practical_entries", []):
            heuristics_payload.append(
                {
                    "heuristicId": heuristic["heuristicId"],
                    "scenarioLabel": heuristic["scenarioLabel"],
                    "recommendedAction": heuristic["recommendedAction"],
                    "actionClass": heuristic["actionClass"],
                    "appliesWhen": list(heuristic.get("appliesWhen", [])),
                    "adjustOrFoldWhen": list(heuristic.get("adjustOrFoldWhen", [])),
                    "rationale": heuristic["rationale"],
                    "sourceItems": resolve_source_items(section, heuristic["sourceRefs"]),
                }
            )
        sections_payload.append(
            {
                "decisionNodeId": node_spec["decisionNodeId"],
                "heading": section["heading"],
                "headingSlug": section["headingSlug"],
                "itemCount": len(items_payload),
                "items": items_payload,
                "practicalHeuristicCount": len(heuristics_payload),
                "practicalHeuristics": heuristics_payload,
            }
        )

    unused_sections = [
        {
            "heading": section["heading"],
            "headingSlug": section["headingSlug"],
            "itemCount": len(section["items"]),
        }
        for section in parsed["sections"]
        if section["heading"] not in used_headings
    ]
    return {
        "materializer": "pokertips_strategy_article_sections",
        "scriptVersion": SCRIPT_VERSION,
        "familyId": family_id,
        "articleTitle": parsed["articleTitle"],
        "sourceHtmlPath": html_rel,
        "sourceHtmlSha256": html_sha,
        "selectedSections": sections_payload,
        "unusedSections": unused_sections,
    }


def build_candidate_ranges(
    *,
    config: dict[str, Any],
    parsed: dict[str, Any],
    intermediate_rel: str,
    html_rel: str,
    html_sha: str,
) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for node_spec in config["node_specs"]:
        section = find_section(parsed, node_spec["heading"])
        entries = []
        if node_spec.get("practical_entries"):
            for heuristic in node_spec["practical_entries"]:
                source_items = resolve_source_items(section, heuristic["sourceRefs"])
                hand_token = f"{section['headingSlug']}::heuristic::{heuristic['heuristicId']}"
                entries.append(
                    {
                        "handToken": hand_token,
                        "inclusionState": "actionable_article_heuristic",
                        "frequency": None,
                        "practicalUseForm": "actionable_article_heuristic",
                        "heuristicId": heuristic["heuristicId"],
                        "scenarioLabel": heuristic["scenarioLabel"],
                        "recommendedAction": heuristic["recommendedAction"],
                        "actionClass": heuristic["actionClass"],
                        "appliesWhen": list(heuristic.get("appliesWhen", [])),
                        "adjustOrFoldWhen": list(heuristic.get("adjustOrFoldWhen", [])),
                        "rationale": heuristic["rationale"],
                        "rawLeaf": {
                            "sourceHeading": section["heading"],
                            "sourceHeadingSlug": section["headingSlug"],
                            "sourceHtmlPath": html_rel,
                            "sourceHtmlSha256": html_sha,
                            "sourceIntermediatePath": intermediate_rel,
                            "sourceItemKind": "heuristic_bundle",
                            "sourceRefs": source_items,
                            "sourceText": " ".join(item["text"] for item in source_items),
                            "sourceTexts": [item["text"] for item in source_items],
                        },
                    }
                )
        else:
            for item in section["items"]:
                hand_token = f"{section['headingSlug']}::{item['kind']}_{item['ordinal']:02d}"
                entries.append(
                    {
                        "handToken": hand_token,
                        "inclusionState": "qualitative_guidance",
                        "frequency": None,
                        "rawLeaf": {
                            "sourceHeading": section["heading"],
                            "sourceHeadingSlug": section["headingSlug"],
                            "sourceHtmlPath": html_rel,
                            "sourceHtmlSha256": html_sha,
                            "sourceIntermediatePath": intermediate_rel,
                            "sourceItemKind": item["kind"],
                            "sourceOrdinal": item["ordinal"],
                            "sourceText": item["text"],
                        },
                    }
                )
        node: dict[str, Any] = {
            key: value
            for key, value in node_spec.items()
            if key not in {"heading", "practical_entries"}
        }
        node["entries"] = entries
        nodes.append(node)
    return nodes


def selector_axes_from_nodes(template_axes: dict[str, Any], nodes: list[dict[str, Any]]) -> dict[str, list[Any]]:
    selector_axes: dict[str, list[Any]] = {}
    for axis in template_axes:
        values: list[Any] = []
        for node in nodes:
            value = node.get(axis)
            if value not in values:
                values.append(value)
        selector_axes[axis] = values
    return selector_axes


def build_manifest_notes(config: dict[str, Any], section_headings: list[str]) -> list[str]:
    return [
        config["article_note"],
        f"Selected retained article sections: {', '.join(section_headings)}.",
        *config["extra_manifest_notes"],
    ]


def update_pack(
    *,
    pack: dict[str, Any],
    config: dict[str, Any],
    family_id: str,
    source_reference: str,
    candidate_ranges: list[dict[str, Any]],
) -> dict[str, Any]:
    pack["templateStatus"] = TEMPLATE_STATUS
    pack["templateVersion"] = TEMPLATE_VERSION
    pack["familyId"] = family_id
    pack["currentRepoStatus"] = "blocked_no_source"
    pack["nonGroundingReason"] = (
        "Candidate materialized from retained source basis with candidate-level grounding evidence, "
        "but currentRepoStatus remains blocked_no_source pending separate human source-evidence review."
    )
    meta = pack.setdefault("meta", {})
    meta.update(config["meta_updates"])
    meta["name"] = f"{family_id} candidate from retained PokerTips article sections"
    meta["source"] = source_reference
    meta["license"] = LICENSE_LABEL
    meta["notes"] = (
        "Materialized from retained strategy-article evidence into family-native blocked-family "
        "candidate nodes without inventing unsupported exact range grids."
    )
    pack["candidateRanges"] = candidate_ranges
    pack["selectorAxes"] = selector_axes_from_nodes(pack.get("selectorAxes", {}), candidate_ranges)
    pack["normalizationNotes"] = list(config["normalization_notes"])
    return pack


def update_manifest(
    *,
    manifest: dict[str, Any],
    config: dict[str, Any],
    family_id: str,
    source_reference: str,
    retained_basis_path: str,
    retained_basis_sha: str,
    retained_retrieved_at: str,
    intermediate_path: str,
    intermediate_sha: str,
    pack_path: str,
    pack_sha: str,
    seeded_sources: dict[str, Any],
    generated_at: str,
    section_headings: list[str],
) -> dict[str, Any]:
    manifest["templateStatus"] = TEMPLATE_STATUS
    manifest["templateVersion"] = TEMPLATE_VERSION
    manifest["familyId"] = family_id
    manifest["currentRepoStatus"] = "blocked_no_source"
    manifest["generatedAtUtc"] = generated_at
    manifest["nonGroundingReason"] = (
        "The candidate is materialized from retained source basis with complete candidate provenance, "
        "but the family remains blocked_no_source until a separate explicit review accepts the source evidence."
    )
    artifacts = manifest.setdefault("artifacts", {})
    artifacts["acceptanceReportPath"] = "none"
    artifacts["derivedBundlePath"] = "none"
    artifacts["normalizedManifestPath"] = "manifest.json"
    artifacts["normalizedPackPath"] = pack_path

    family_identity = manifest.setdefault("familyIdentity", {})
    family_identity.update(config["family_identity_updates"])

    normalization = manifest.setdefault("normalization", {})
    normalization["transformedIntermediatePath"] = intermediate_path
    normalization["normalizationNotes"] = list(config["normalization_notes"])

    manifest["notes"] = build_manifest_notes(config, section_headings)

    provenance = manifest.setdefault("provenance", {})
    artifact_hashes = provenance.setdefault("artifactHashes", {})
    artifact_hashes["normalizedPackSha256"] = pack_sha
    artifact_hashes["retainedBasisSha256"] = retained_basis_sha
    artifact_hashes["transformedIntermediateSha256"] = intermediate_sha
    provenance["seededRetainedSources"] = seeded_sources
    provenance["sourceSha256OrEquivalentLinkage"] = f"sha256:{retained_basis_sha}"
    provenance["transformationChain"] = [
        {
            "stage": "retained_source_basis",
            "path": retained_basis_path,
            "sha256OrEquivalentLinkage": f"sha256:{retained_basis_sha}",
        },
        {
            "stage": "transformed_intermediate",
            "path": intermediate_path,
            "sha256": intermediate_sha,
        },
        {
            "stage": "normalized_pack",
            "path": pack_path,
            "sha256": pack_sha,
        },
    ]

    source = manifest.setdefault("source", {})
    source["name"] = config["source_name"]
    source["exactSourcePathOrReference"] = source_reference
    source["retainedBasisPath"] = retained_basis_path
    source["retainedBasisType"] = RETAINED_BASIS_TYPE
    source["retrievedAt"] = retained_retrieved_at
    source["license"] = LICENSE_LABEL
    source["redistribution"] = REDISTRIBUTION_NOTE
    return manifest


def update_candidate_metadata(
    *,
    candidate: dict[str, Any],
    family_id: str,
    config: dict[str, Any],
    html_rel: str,
    html_sha: str,
    intermediate_rel: str,
    intermediate_sha: str,
    pack_sha: str,
    candidate_ranges: list[dict[str, Any]],
    pack_selector_axes: dict[str, list[Any]],
) -> dict[str, Any]:
    candidate["candidateStatus"] = CANDIDATE_STATUS
    candidate["currentRepoStatus"] = "blocked_no_source"
    candidate["expectedVerdict"] = "shape_match_with_grounding_evidence_candidate"
    candidate["familyId"] = family_id
    candidate["familySlug"] = config["family_slug"]
    candidate["packFile"] = "pack.json"
    candidate["manifestFile"] = "manifest.json"
    candidate["templateStatus"] = TEMPLATE_STATUS
    candidate["nonGroundingReason"] = (
        "Candidate materialized from retained source basis with candidate-level grounding evidence, "
        "but currentRepoStatus remains blocked_no_source pending separate human source-evidence review."
    )
    candidate["notes"] = config["article_note"]
    candidate["materializationSummary"] = {
        "scriptVersion": SCRIPT_VERSION,
        "nodeCount": len(candidate_ranges),
        "entryCountPerNode": [len(node.get("entries", [])) for node in candidate_ranges],
        "actionableHeuristicCount": sum(len(node.get("entries", [])) for node in candidate_ranges),
        "normalizedPackSha256": pack_sha,
        "retainedSourceStructure": {
            "htmlPath": html_rel,
            "htmlSha256": html_sha,
            "intermediatePath": intermediate_rel,
            "intermediateSha256": intermediate_sha,
        },
        "selectorAxes": pack_selector_axes,
    }
    return candidate


def materialize_one_family(family_id: str, config: dict[str, Any], root: Path) -> dict[str, Any]:
    candidate_dir = resolve_path(config["candidate_dir"], root)
    candidate_path = candidate_dir / "candidate.json"
    pack_path = candidate_dir / "pack.json"
    manifest_path = candidate_dir / "manifest.json"
    intermediate_path = candidate_dir / "intermediate" / "article_sections.json"

    candidate = read_json(candidate_path)
    pack = read_json(pack_path)
    manifest = read_json(manifest_path)

    html_path, html_meta = load_seeded_html_source(candidate, candidate_dir)
    html_rel = str(html_path.relative_to(candidate_dir)).replace("\\", "/")
    html_sha = sha256_file(html_path)
    html_text = html_path.read_text(encoding="utf-8")
    parsed = parse_article_sections(html_text)
    intermediate = build_intermediate_payload(
        family_id=family_id,
        config=config,
        parsed=parsed,
        html_rel=html_rel,
        html_sha=html_sha,
    )
    write_json(intermediate_path, intermediate)
    intermediate_rel = str(intermediate_path.relative_to(candidate_dir)).replace("\\", "/")
    intermediate_sha = sha256_file(intermediate_path)

    candidate_ranges = build_candidate_ranges(
        config=config,
        parsed=parsed,
        intermediate_rel=intermediate_rel,
        html_rel=html_rel,
        html_sha=html_sha,
    )

    source_reference = str(html_meta.get("sourceReference", ""))
    retrieved_at = str(html_meta.get("retrievedAt", ""))
    section_headings = [spec["heading"] for spec in config["node_specs"]]

    pack = update_pack(
        pack=pack,
        config=config,
        family_id=family_id,
        source_reference=source_reference,
        candidate_ranges=candidate_ranges,
    )
    write_json(pack_path, pack)
    pack_sha = sha256_file(pack_path)

    manifest = update_manifest(
        manifest=manifest,
        config=config,
        family_id=family_id,
        source_reference=source_reference,
        retained_basis_path=html_rel,
        retained_basis_sha=html_sha,
        retained_retrieved_at=retrieved_at,
        intermediate_path=intermediate_rel,
        intermediate_sha=intermediate_sha,
        pack_path="pack.json",
        pack_sha=pack_sha,
        seeded_sources=candidate["seededSourceSummary"],
        generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        section_headings=section_headings,
    )
    write_json(manifest_path, manifest)

    pack_selector_axes = selector_axes_from_nodes(pack.get("selectorAxes", {}), candidate_ranges)
    candidate = update_candidate_metadata(
        candidate=candidate,
        family_id=family_id,
        config=config,
        html_rel=html_rel,
        html_sha=html_sha,
        intermediate_rel=intermediate_rel,
        intermediate_sha=intermediate_sha,
        pack_sha=pack_sha,
        candidate_ranges=candidate_ranges,
        pack_selector_axes=pack_selector_axes,
    )
    write_json(candidate_path, candidate)

    return {
        "familyId": family_id,
        "candidateDir": str(candidate_dir),
        "candidateId": candidate.get("candidateId"),
        "articleTitle": parsed["articleTitle"],
        "selectedSections": section_headings,
        "nodeCount": len(candidate_ranges),
        "entryCountPerNode": [len(node.get("entries", [])) for node in candidate_ranges],
        "htmlPath": html_rel,
        "htmlSha256": html_sha,
        "intermediatePath": intermediate_rel,
        "intermediateSha256": intermediate_sha,
        "packSha256": pack_sha,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--family",
        action="append",
        choices=sorted(FAMILY_CONFIGS.keys()),
        help="Family id to materialize. Repeat to materialize more than one family. Defaults to all configured families.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    families = args.family or list(FAMILY_CONFIGS.keys())
    results = []
    for family_id in families:
        results.append(materialize_one_family(family_id, FAMILY_CONFIGS[family_id], root))
    json.dump(
        {
            "status": "ok",
            "scriptVersion": SCRIPT_VERSION,
            "materializedFamilies": results,
        },
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

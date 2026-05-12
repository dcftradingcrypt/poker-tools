window.__A5_TRIPLE_DRAW_PUBLIC_RANGES_V1 = {
  "dataset_id": "a5_triple_draw_pre_draw_public_ranges_v1",
  "version": 1,
  "scope": {
    "game": "fixed_limit_a5_triple_draw",
    "phase": "before_first_draw",
    "primary_views": [
      "first_in_open",
      "versus_open_continue"
    ],
    "position_buttons": [
      "EP",
      "CO",
      "BTN",
      "SB",
      "BB"
    ],
    "position_button_meaning": "shorthanded public-chart positions: EP/UTG-HJ, Cutoff, Button, Small Blind, and Big Blind",
    "open_positions": [
      "EP",
      "CO",
      "BTN",
      "SB"
    ],
    "defense_only_positions": [
      "BB"
    ],
    "excluded_from_first_in_open": [
      "BB"
    ],
    "excluded_reason": "public A-5 Triple Draw material does not publish a fixed big-blind first-in open row; BB remains a defense-only seat"
  },
  "strength_primer": {
    "best_hand": "A-2-3-4-5",
    "ranking_rule": "lowest five-card hand wins; aces play low and pairs are always bad",
    "straight_flush_rule": "straights and flushes do not count against the low",
    "normalization_rule": "because suits do not change low-hand value in A-5, the dataset is stored as rank-structure buckets such as A23, four wheel cards, and three to a six rather than suit-specific combos"
  },
  "collection_notes": [
    "CountingOuts 'Strategy before the First Draw' is the only public source that publishes explicit positional open totals and class-level percentages, so it anchors the open rows.",
    "BetMGM is used as a secondary cross-check for the open totals and the late-position widening story, not as the authoritative percentage source.",
    "Kevin Haney's CardPlayer article supplies boundary examples and cautionary trims, but it explicitly presents the ranges as educated guesses rather than exact science.",
    "WPT Global and the KKPOKER LIVE Players Guide PDF are retained to confirm that the target game is A-5 Lowball Triple Draw and that suits/straights/flushes do not change low value.",
    "No public source found in this collection publishes exact flat-call percentages by position, so the continue view is deliberately stored as action-class guidance instead of fake mixed frequencies."
  ],
  "position_order": [
    "EP",
    "CO",
    "BTN",
    "SB",
    "BB"
  ],
  "positions": {
    "EP": {
      "label": "EP / UTG-HJ",
      "first_in_open": {
        "anchor_chart_pct": "26.7%",
        "chart_source_ref": "countingouts_predraw",
        "position_read": "Merged public early-position baseline: A-5 equities run closer than in many other draw games, but the first seat still cuts the roughest three-card sixes and all two-card steal opens.",
        "public_range_read": "Made 7s or better, four wheel cards, four to a six, three wheel cards, and the stronger three-card-six subset A26-A46 / 236 / 246 / 346.",
        "open_table_rows": [
          [
            "Pat made hands",
            "Made 7s or better (0.8%)"
          ],
          [
            "Premium one-card draws",
            "Four wheel cards (1.9%)"
          ],
          [
            "Strong one-card sixes",
            "Four to a six (3.7%)"
          ],
          [
            "Core two-card draws",
            "Three wheel cards (12.7%)"
          ],
          [
            "Early-position three-card sixes",
            "A26-A46, 236, 246, 346 (7.6%)"
          ]
        ],
        "source_note": "CountingOuts is the only public source here with a class-by-class percentage breakdown. BetMGM's approximate 26% UTG-HJ figure matches the same structural shell."
      },
      "versus_open": {
        "scenario_read": "No public non-blind call chart gives exact percentages. The available guidance is class-based: pat hands and one-card draws mostly 3-bet, premium two-card draws can 3-bet, and weaker two-card draws can cold-call.",
        "continue_table_rows": [
          [
            "Any opener",
            "Re-raise pat hands and one-card draws rather than flat-calling"
          ],
          [
            "Premium two-card draws",
            "A23 / A24 / A34 can be value 3-bets; A23 may still mix in some cold-calls"
          ],
          [
            "Weaker two-card draws",
            "A36-type hands can cold-call instead of 3-betting"
          ],
          [
            "Raised-pot trim",
            "Bottom-opening examples such as 345 become much closer to folds once an early raise already exists"
          ]
        ],
        "source_note": "Haney's article frames these cut lines as educated guesses, so the repo surface keeps them as boundary guidance instead of inventing a numeric cold-call mix."
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw",
        "betmgm_basic",
        "wpt_rules",
        "kklive_players_guide_pdf"
      ]
    },
    "CO": {
      "label": "Cutoff",
      "first_in_open": {
        "anchor_chart_pct": "31.7%",
        "chart_source_ref": "countingouts_predraw",
        "position_read": "Merged public cutoff baseline: the main widen from EP is that the full three-to-a-six bucket comes in, while two-card steals still wait for the button.",
        "public_range_read": "Keep the entire EP shell and add the broader three-to-a-six class; practical floor examples around 356 or A47 are guidance, not exact mix points.",
        "open_table_rows": [
          [
            "Carry-over early core",
            "Full EP shell remains in the range (26.7%)"
          ],
          [
            "Late-position widen",
            "Add the broader three-to-a-six bucket; total open band rises to 31.7%"
          ],
          [
            "Practical floor examples",
            "Haney's cutoff floor is around 356 or A47, but not as a solver-backed frequency mix"
          ]
        ],
        "source_note": "CountingOuts gives the explicit 31.7% total. BetMGM repeats the same cutoff widen, and Haney supplies concrete bottom-of-range examples."
      },
      "versus_open": {
        "scenario_read": "Facing an earlier open from the cutoff, the public advice remains non-numeric and class based. In position you still prefer to 3-bet pat hands and one-card draws, then separate premium versus weaker two-card draws.",
        "continue_table_rows": [
          [
            "Vs earlier opens",
            "Re-raise pat hands and one-card draws to keep initiative and avoid face-up flats"
          ],
          [
            "Premium two-card draws",
            "A23 / A24 / A34 can attack wider early opens with 3-bets"
          ],
          [
            "Weaker two-card draws",
            "A36-type hands are reasonable cold-calls when you do continue"
          ],
          [
            "Marginal open-class hands",
            "Hands near the open floor lose value once the pot is already raised"
          ]
        ],
        "source_note": "Public sources do not publish a cutoff-specific call percentage row, so this seat stays a position-aware summary of the same class split."
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw",
        "betmgm_basic"
      ]
    },
    "BTN": {
      "label": "Button",
      "first_in_open": {
        "anchor_chart_pct": "42.7%",
        "chart_source_ref": "countingouts_predraw",
        "position_read": "Merged public button baseline: after carrying the cutoff shell, the button adds the steal-heavy two-card wheel-start bucket A2 / A3 / A4 / 23 / 24 / 34.",
        "public_range_read": "Keep the cutoff shell and add A2, A3, A4, 23, 24, and 34; Haney's button floor examples also reach 456 / A57 / 357 as practical edge hands.",
        "open_table_rows": [
          [
            "Cutoff carry-over",
            "Full CO shell remains in the range (31.7%)"
          ],
          [
            "Button-only two-card layer",
            "Add A2 / A3 / A4 / 23 / 24 / 34 (10.9%)"
          ],
          [
            "Practical steal floor",
            "456 / A57 / 357 are example button-edge opens, not exact mixed-frequency rows"
          ]
        ],
        "source_note": "CountingOuts provides the explicit 42.7% button total and the A2-through-34 extension. BetMGM repeats the same widen, while Haney shows how far the practical floor can stretch."
      },
      "versus_open": {
        "scenario_read": "In position versus earlier opens, the same public class logic applies: pat and one-card hands prefer 3-bets, premium two-card draws can 3-bet, and weaker two-card draws can flat. No exact button cold-call mix is published.",
        "continue_table_rows": [
          [
            "Vs EP or CO open",
            "Pat hands and one-card draws still prefer 3-bets over flats"
          ],
          [
            "Premium two-card draws",
            "A23 / A24 / A34 can pressure wider opening ranges with 3-bets"
          ],
          [
            "Weaker two-card draws",
            "A36-type hands realize better in position and can be cold-calls"
          ],
          [
            "Boundary discipline",
            "The weakest button steals are first to disappear once someone has already raised"
          ]
        ],
        "source_note": "The button gets the best realization, but the public material still stops at qualitative action classes rather than exact mix percentages."
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw",
        "betmgm_basic"
      ]
    },
    "SB": {
      "label": "Small Blind",
      "first_in_open": {
        "anchor_chart_pct": "dynamic",
        "chart_source_ref": "countingouts_predraw",
        "position_read": "Merged public small-blind baseline: against a tough big blind, opening the button range is the default; widen only when the BB over-folds and under-reraises.",
        "public_range_read": "Start from the button range versus strong opponents in the big blind, then add exploitative steals only against weaker BBs who fail to defend enough.",
        "open_table_rows": [
          [
            "Tough-BB baseline",
            "Use the button open shell as the default"
          ],
          [
            "Exploit widen",
            "Open wider only when the BB folds too much and does not reraise enough"
          ],
          [
            "Why it stays tighter",
            "Thin draws realize poorly out of position against a competent BB"
          ]
        ],
        "source_note": "CountingOuts gives only a dynamic SB rule, not a fixed percentage row. The UI keeps that honesty instead of fabricating an exact small-blind open total."
      },
      "versus_open": {
        "scenario_read": "The small blind is the clearest published blind-defense seat: mostly raise-or-fold against opens, with rare flats such as A2 versus loose late-position openers.",
        "continue_table_rows": [
          [
            "Default response",
            "Mostly raise or fold; if the hand is worth playing, 3-bet to isolate"
          ],
          [
            "Vs loose late opener",
            "A2 can flat-call sometimes against aggressive late-position opens"
          ],
          [
            "Vs tight EP open",
            "Fold A2 and other thin two-card draws much more often"
          ],
          [
            "Against one-card draws",
            "A2 has only about 33% against 3456 and needs to improve early"
          ]
        ],
        "source_note": "This seat is where the public advice is most specific: 3-bet-or-fold as the baseline, with a narrow exploitative flat range against loose late opens."
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw"
      ]
    },
    "BB": {
      "label": "Big Blind",
      "versus_open": {
        "scenario_read": "Public A-5 material documents the big blind only as a defense seat. The main baseline is to defend at least the button opening range versus late opens, tighten versus early opens, and widen sharply versus a small-blind steal.",
        "continue_table_rows": [
          [
            "Vs late-position open",
            "Defend with at least the button opening range"
          ],
          [
            "Vs early-position open",
            "Play a little tighter than the button baseline"
          ],
          [
            "Vs SB steal",
            "Add A5 / 25 / 35 / 45 to the button range to get above 50% defense"
          ],
          [
            "Re-raise rule",
            "Versus an SB raise, re-raise any two-card draw or better"
          ]
        ],
        "source_note": "CountingOuts is the only source in this set that spells out the late-open baseline and the A5 / 25 / 35 / 45 blind-versus-blind expansion."
      },
      "source_refs": [
        "countingouts_predraw"
      ]
    }
  },
  "source_index": {
    "countingouts_predraw": {
      "title": "CountingOuts: Ace to Five Triple Draw - Strategy before the First Draw",
      "weight": "primary",
      "url": "https://www.countingouts.com/ace-to-five-triple-draw-before-the-first-draw/"
    },
    "countingouts_rules_basic": {
      "title": "CountingOuts: Ace to Five Triple Draw Lowball Rules and Basic Strategy",
      "weight": "supporting",
      "url": "https://www.countingouts.com/ace-to-five-triple-draw-rules-and-basic-strategy/"
    },
    "cardplayer_predraw": {
      "title": "CardPlayer / Kevin Haney: Ace-To-Five Triple Draw: Playing Before The First Draw",
      "weight": "primary",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66523-phil-hellmuth-36-19/articles/24908-ace-to-five-triple-draw-playing-before-the-first-draw"
    },
    "betmgm_basic": {
      "title": "BetMGM: Ace-to-Five Triple Draw: Basic Strategy Tips",
      "weight": "secondary",
      "url": "https://poker.betmgm.com/en/blog/poker-guides/ace-to-five-triple-draw-strategy-tips/"
    },
    "wpt_rules": {
      "title": "WPT Global: Ace-to-Five Lowball Poker | Rules & Hand Rankings",
      "weight": "rules",
      "url": "https://wptglobal.com/how-to-play/ace-to-five"
    },
    "kklive_players_guide_pdf": {
      "title": "KKPOKER LIVE Players Guide (2024 Summer) PDF",
      "weight": "supplemental_pdf",
      "url": "https://pokerjapan.jp/wp-content/uploads/2024/07/2024-SUMMER-KKPOKER-LIVE-PLAYERS-GUIDE_0713.pdf"
    }
  },
  "source_extracts": {
    "countingouts_predraw": {
      "scope": "primary open totals and blind-defense class guidance",
      "position_notes": {
        "EP": "26.7% total built from made 7s+, four wheel cards, four to a six, three wheel cards, and A26-A46 / 236 / 246 / 346",
        "CO": "31.7% total by adding the broader three-to-a-six bucket",
        "BTN": "42.7% total by adding A2 through 34",
        "SB": "Use the button range as the baseline versus a tough BB; widen only against weak BB defense",
        "BB": "Defend at least the button range versus late opens; add A5 / 25 / 35 / 45 versus SB steals"
      }
    },
    "cardplayer_predraw": {
      "scope": "boundary examples and raised-pot trims",
      "position_notes": {
        "EP": "Bottom opens are around 345 or A46",
        "CO": "Cutoff floor examples include 356 or A47",
        "BTN": "Button floor examples include 456, A57, and 357, plus low two-card steals",
        "general": "The article labels these opens as educated guesses, not an exact science"
      }
    },
    "betmgm_basic": {
      "scope": "secondary total cross-check",
      "position_notes": {
        "EP": "roughly 26%",
        "CO": "roughly 31% with three-to-a-six adds",
        "BTN": "roughly 42% with A2-A4 and 23-34 adds"
      }
    },
    "wpt_rules": {
      "scope": "rule and normalization support",
      "position_notes": {
        "general": "A-2-3-4-5 is the best hand, straights and flushes do not count against you, and suits do not matter for the low"
      }
    },
    "kklive_players_guide_pdf": {
      "scope": "event and format confirmation",
      "position_notes": {
        "general": "The mixed-game guide lists A-5 Lowball Triple Draw as one of the fixed-limit rotation games"
      }
    }
  }
};

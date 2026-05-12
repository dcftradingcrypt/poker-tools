window.__STUD8_THIRD_STREET_PUBLIC_RANGES_V1 = {
  "dataset_id": "stud8_third_street_position_ranges_v1",
  "version": 1,
  "scope": {
    "game": "fixed_limit_seven_card_stud_hi_lo_eight_or_better",
    "phase": "third_street",
    "position_buttons": [
      "EP",
      "MP",
      "LP",
      "BI"
    ],
    "position_button_meaning": "normalized third-street positions relative to the bring-in: early non-steal, middle transition, late steal, and the bring-in seat itself",
    "reconstruction_method": "public-source practical range union; not a solver chart"
  },
  "collection_notes": [
    "Stud8 does not publish NLHE-style fixed seat charts, so the UI normalizes positions into early/non-steal, middle/transition, late/steal, and bring-in defense.",
    "Open and continue rows are reconstructed from public HTML strategy articles, the Japanese note and blog, and a PDF rulebook. When a source says reraise-or-fold, the dataset preserves that instead of inventing a flat-call frequency.",
    "The California casino PDF is retained to confirm bring-in, completion, and 8-or-better semantics. The actual range bands come from the strategy articles.",
    "Late-position ace-up widening and bring-in defense remain the highest-variance branches. The surface shows only the overlap the public sources support and leaves tails in the evidence tables."
  ],
  "global_source_refs": [
    "cardplayer_starting_hands",
    "pdf_aviator_rules"
  ],
  "position_order": [
    "EP",
    "MP",
    "LP",
    "BI"
  ],
  "positions": {
    "EP": {
      "label": "Early / Non-Steal",
      "seat_band": [
        "immediately_left_of_bring_in",
        "several_live_up_cards_still_behind"
      ],
      "position_summary": "This is the early third-street seat where the hand is not yet a steal and multiple live door cards remain behind.",
      "caution_note": "High-only hands lose value quickly here because they still need the field to miss low while many players remain to wake up with live baby cards or an ace.",
      "open_complete": {
        "section_label": "Open / Complete",
        "anchor_profile": "three-low or pair-plus-low opening seat",
        "public_range_read": "Complete with live scoop-oriented starts: ace-low three-card hands, connected or suited three-low hands, AA plus a low card, rolled-up trips, and only the safest live high pairs.",
        "table_columns": [
          "Class",
          "Reconstructed range / action"
        ],
        "table_rows": [
          [
            "Premium scoop lows",
            "A23 / A24 / A25, 345 / 346 / 456, especially when suited or very live"
          ],
          [
            "Three-low flushes",
            "Three low suited cards and live three-to-a-straight-flush starts"
          ],
          [
            "Pair plus low",
            "AA2 / AA3 / AA4, rolled-up low trips, 88+low and 77+low"
          ],
          [
            "Live high pairs",
            "KKx / QQx only when the pair is likely best high and low pressure behind is limited"
          ],
          [
            "Automatic folds",
            "9-T-J middling starts, rough low-only hands, naked Broadway, and high pairs with an ace plus many low cards behind"
          ]
        ],
        "source_note": "PokerNews and the Japanese sources all make early position a three-low-or-pair seat, while Haney adds the practical warning that high pairs must tighten sharply when an ace and many low doors remain behind.",
        "collected_rows": [
          {
            "source_ref": "pokernews_mixed_tips",
            "evidence_type": "direct_position_rule",
            "range_read": "Early position open-raises should aim for three low cards, a pair, or three-to-a-flush.",
            "notes": "This is the cleanest public early-position rule and defines the base row."
          },
          {
            "source_ref": "kihara_blog",
            "evidence_type": "japanese_rules_of_thumb",
            "range_read": "Without a big pair, cards from 9 to K are trash; default participation comes from three low cards or a big pair.",
            "notes": "This removes the middling-card tail from the early row."
          },
          {
            "source_ref": "kogoro_stud8",
            "evidence_type": "tiered_starting_hand_list",
            "range_read": "Any-position core starts from rolled-up trips, AA+low, suited low connectors, suited three lows, 88+low, 77+low, best pair, and A-led low hands.",
            "notes": "Used as the Japanese hierarchy that orders the early premium classes."
          },
          {
            "source_ref": "cardplayer_often_playable",
            "evidence_type": "practical_trim",
            "range_read": "High pairs can open early, but should fold when an ace and many low cards remain behind.",
            "notes": "Used to trim high-pair opens rather than to widen the row."
          },
          {
            "source_ref": "cardplayer_starting_hands",
            "evidence_type": "meta_boundary",
            "range_read": "Stud8 starting hands must be conditioned on exposed cards and prior action rather than treated as a rigid chart.",
            "notes": "Explains why the row is expressed as a normalized practical range instead of one fixed seat chart."
          }
        ]
      },
      "versus_complete": {
        "section_label": "Vs Complete / Continue",
        "anchor_profile": "continue only with real two-way equity",
        "public_range_read": "Continue aggressively with live ace-low cores, rolled-up trips, AA plus a low card, small pair plus ace kicker, and the strongest suited or connected three-low hands. Fold rough one-way starts and most middling high-only hands.",
        "table_columns": [
          "Band",
          "Reconstructed continue range / action"
        ],
        "table_rows": [
          [
            "Reraise or pressure",
            "AA+low, rolled-up trips, live A23 / A24 / A35s, small pair plus ace kicker"
          ],
          [
            "Continue selectively",
            "Strong one-gappers and ace-seven or ace-eight lows only when live and the opener can still be light"
          ],
          [
            "Fold more often",
            "QQ versus a king complete, high pairs versus a non-steal ace complete, 889 versus Q/K strength, rough low-only hands, and 9-T-J no-man's-land"
          ]
        ],
        "source_note": "The public overlap here is aggressive continue with pair-plus-ace or live ace-low, and disciplined folds with rough razz lows or high-only holdings against legitimate strength.",
        "collected_rows": [
          {
            "source_ref": "cardplayer_realizing_equity",
            "evidence_type": "realization_rule",
            "range_read": "Rough low hands without an ace should fold even at attractive immediate odds when an ace shows strength; small pair plus ace and A-led three lows should be reraised by default.",
            "notes": "This defines the early continue bucket."
          },
          {
            "source_ref": "cardplayer_often_playable",
            "evidence_type": "fold_boundary",
            "range_read": "High pairs fold to a non-steal ace complete, and queens should fold when a king completes.",
            "notes": "Used for the high-pair fold row."
          },
          {
            "source_ref": "kogoro_stud8",
            "evidence_type": "japanese_fold_rule",
            "range_read": "889 without low support should fold cleanly against a Q or K completion.",
            "notes": "This is the cleanest public mid-pair fold example."
          },
          {
            "source_ref": "cardplayer_sometimes_playable",
            "evidence_type": "do_not_flat_rule",
            "range_read": "Rough razz lows are not for calling legitimate completes; they belong only in steals or bring-in defense.",
            "notes": "This removes the low-only bluff-catcher bucket."
          }
        ]
      },
      "source_refs": [
        "pokernews_mixed_tips",
        "kihara_blog",
        "kogoro_stud8",
        "cardplayer_often_playable",
        "cardplayer_starting_hands",
        "cardplayer_realizing_equity",
        "cardplayer_sometimes_playable"
      ]
    },
    "MP": {
      "label": "Middle / Transition",
      "seat_band": [
        "one_or_two_players_still_behind",
        "partial_steal_pressure_possible"
      ],
      "position_summary": "This is the middle third-street seat where some folds may already exist, but the hand is not yet a pure steal the way a late ace-up spot can be.",
      "caution_note": "Middle position adds more ace-led and one-gap lows, but it is still a bad place to drift into rough low-only hands or one-way traps that need the table to cooperate.",
      "open_complete": {
        "section_label": "Open / Complete",
        "anchor_profile": "carry the early core and add ace-led and smooth low extensions",
        "public_range_read": "Keep every early premium and add exposed-ace opens with at least one low card, smooth one-gappers, ace-seven and ace-eight lows in shorthanded contexts, and selected low pairs with high kickers when overcards behind are capped.",
        "table_columns": [
          "Class",
          "Reconstructed range / action"
        ],
        "table_rows": [
          [
            "Carry the EP core",
            "All early premiums remain opens"
          ],
          [
            "Ace-led extensions",
            "Ace exposed with at least one low card; ace-seven and ace-eight lows when live and preferably shorthanded"
          ],
          [
            "Smooth one-gappers",
            "235 / 245 / 346 / 356 / 457 as standard adds; 467 / 568 near the edge"
          ],
          [
            "Low pair plus high kicker",
            "K66 / Q77 type completes when the threatening cards behind are limited"
          ],
          [
            "Still too weak",
            "Rough two-gappers, nine-up traps, and medium pairs with too many dangerous door cards behind"
          ]
        ],
        "source_note": "Middle position is where the public sources begin to add ace-led marginals and the smoother one-gappers, but only while the exposed-card map remains favorable.",
        "collected_rows": [
          {
            "source_ref": "pokernews_mixed_tips",
            "evidence_type": "direct_position_rule",
            "range_read": "Middle position can open-raise ace combinations that contain at least one low card of eight or lower.",
            "notes": "This defines the middle-position ace rule."
          },
          {
            "source_ref": "cardplayer_often_playable",
            "evidence_type": "class_upgrade",
            "range_read": "One-gappers and ace-seven or ace-eight lows are often playable, especially with an ace up and in shorthanded pots.",
            "notes": "Used for the smooth low expansion."
          },
          {
            "source_ref": "cardplayer_sometimes_playable",
            "evidence_type": "position_gate",
            "range_read": "Medium pairs are mostly playable as an open complete from middle or later position when there are not too many threatening cards behind.",
            "notes": "This is the main middle-position medium-pair add."
          },
          {
            "source_ref": "kogoro_stud8",
            "evidence_type": "japanese_tier_list",
            "range_read": "A-led low hands, standard three-low starts, and low connectors remain within the any-position complete core.",
            "notes": "Used as the overlap check on the middle seat."
          },
          {
            "source_ref": "cardplayer_realizing_equity",
            "evidence_type": "aggressive_default",
            "range_read": "Small pairs with an ace kicker and ace-headed three-low hands should default toward reraising rather than passive flatting.",
            "notes": "Used to keep the middle row aggressive instead of call-heavy."
          }
        ]
      },
      "versus_complete": {
        "section_label": "Vs Complete / Continue",
        "anchor_profile": "attack possible steals, but avoid getting sandwiched",
        "public_range_read": "Middle position can pressure a likely steal with live 568 or 578 type starts, ace-low holdings, and small pair plus ace. It should still fold rough ace-eight lows, rough razz lows, and middling high-only hands against real strength.",
        "table_columns": [
          "Band",
          "Reconstructed continue range / action"
        ],
        "table_rows": [
          [
            "Pressure continues",
            "568 / 578, live one-gappers, ace-low hands, and small pair plus ace when the opener can be wide"
          ],
          [
            "Continue selectively",
            "Ace-seven or ace-eight lows and disguised low pairs in heads-up or near-heads-up pots"
          ],
          [
            "Fold more often",
            "Rough ace-eight without flush backup versus five-complete plus ace-reraise, rough low-only hands, middling traps, and medium pairs facing clear high strength"
          ]
        ],
        "source_note": "Haney's public examples repeatedly split the middle row into pressure continues against stealable ranges and disciplined folds when the line already shows real high or ace strength.",
        "collected_rows": [
          {
            "source_ref": "cardplayer_often_playable",
            "evidence_type": "steal_counterexample",
            "range_read": "568-type hands can reraise a low-card completion from a steal position because they perform well against that wider range.",
            "notes": "This is the clearest public middle-position attack example."
          },
          {
            "source_ref": "cardplayer_often_playable",
            "evidence_type": "negative_example",
            "range_read": "A48 is not worth much when a five completes and an ace reraises, especially when an ace is already dead and the hand lacks flush backup.",
            "notes": "Used as the ace-eight fold boundary."
          },
          {
            "source_ref": "cardplayer_sometimes_playable",
            "evidence_type": "do_not_flat_rule",
            "range_read": "Rough razz lows should not be calling legitimate completes; they belong in steals or bring-in defense only.",
            "notes": "This removes the weak low-only continue row."
          },
          {
            "source_ref": "cardplayer_realizing_equity",
            "evidence_type": "aggressive_default",
            "range_read": "A-led three-low hands and pair-plus-ace starts realize equity well and should avoid face-up flat calls.",
            "notes": "Used to keep the continue row aggressive."
          }
        ]
      },
      "source_refs": [
        "pokernews_mixed_tips",
        "cardplayer_often_playable",
        "cardplayer_sometimes_playable",
        "cardplayer_realizing_equity",
        "kogoro_stud8"
      ]
    },
    "LP": {
      "label": "Late / Steal",
      "seat_band": [
        "few_players_left_to_act",
        "steal_pressure_and_up_card_asymmetry_matter_most"
      ],
      "position_summary": "This is the late third-street seat where steal pressure finally matters, especially when the door card is an ace and the remaining up-cards look weak.",
      "caution_note": "Stud8 still steals worse than Stud High or Razz because the bring-in is usually a low card and can defend with real equity. The late row is wide, but not empty-card wide.",
      "open_complete": {
        "section_label": "Open / Complete",
        "anchor_profile": "steal-aware row built around ace-up asymmetry",
        "public_range_read": "Late position keeps every earlier premium and widens mainly through ace-up completes, selected steal-only suited high-plus-two-low holdings, and a small band of late low extensions that still have real fallback equity if defended.",
        "table_columns": [
          "Class",
          "Reconstructed range / action"
        ],
        "table_rows": [
          [
            "Ace-up widen",
            "Open-complete almost any ace-up start when no stronger ace sits behind; trim only the worst Broadway-heavy aces and dead-ace configurations"
          ],
          [
            "Premium scoop core",
            "All EP and MP premiums remain strong opens"
          ],
          [
            "Late steal holdings",
            "AQ6, K45, JQK, A69, K32s, Q42s when the board says the steal can work and the hand still has some fallback equity"
          ],
          [
            "Late low extensions",
            "267 / 278 and rough one-gappers only when folded to, live, and likely to play heads-up"
          ],
          [
            "Still fold",
            "Dead-ace steals, middle-card no-man's-land, and pure high garbage with no scoop path"
          ]
        ],
        "source_note": "Late-position widening is driven by ace-up pressure first and by carefully chosen steal holdings second. The common theme is that even the steal hands still need some hand to fall back on when the bring-in defends.",
        "collected_rows": [
          {
            "source_ref": "pokernews_mixed_tips",
            "evidence_type": "direct_position_rule",
            "range_read": "Late position should open-raise any exposed ace unless another ace is exposed behind, in which case the worst aces can fold.",
            "notes": "This is the broad late-position ace-up rule."
          },
          {
            "source_ref": "cardplayer_ohel_nines",
            "evidence_type": "late_ace_up_example",
            "range_read": "Against a nine up and the bring-in, an ace door card can open very wide; only the worst Broadway-heavy ace starts are omitted.",
            "notes": "Used as the clearest public late-position widening example."
          },
          {
            "source_ref": "cardplayer_ante_stealing",
            "evidence_type": "steal_boundary",
            "range_read": "High antes widen steal attempts, but Stud8 still needs some semblance of a hand because the bring-in can defend with three-low holdings.",
            "notes": "This keeps the late row from turning into a Stud High steal chart."
          },
          {
            "source_ref": "cardplayer_sometimes_playable",
            "evidence_type": "steal_holding_list",
            "range_read": "Ace Broadway low, wheel Broadway wheel, three high cards, and ace-up with reasonable hole cards are steal-only late-position holdings.",
            "notes": "Used for the late steal-only class."
          },
          {
            "source_ref": "kogoro_stud8",
            "evidence_type": "japanese_steal_rule",
            "range_read": "Even from middle or late position, steals should still use reasonably strong hands such as suited high-plus-two-low starts.",
            "notes": "This cross-check keeps the late row practical."
          }
        ]
      },
      "versus_complete": {
        "section_label": "Vs Complete / Continue",
        "anchor_profile": "defend wider versus steals, but respect ace-up strength",
        "public_range_read": "Late position can defend and reraise more aggressively versus possible steals, but should still become extremely tight against an ace-up complete unless it also shows an ace, buried aces, trips, or a very live suited wheel structure.",
        "table_columns": [
          "Band",
          "Reconstructed continue range / action"
        ],
        "table_rows": [
          [
            "Attack steals",
            "Ace-up hands, live 568 / 578, pair plus ace, and disguised two-way holdings can reraise likely steal completes"
          ],
          [
            "Continue selectively",
            "Live suited wheel holdings and late steal hands with real backup versus obviously wide opens"
          ],
          [
            "Snap folds versus strength",
            "Most non-ace hands versus an ace-up complete, queens and weak highs, rough low-only hands, and 889 versus Q/K strength"
          ]
        ],
        "source_note": "The public overlap is very asymmetrical: you can pressure late steals with real two-way hands, but an ace-up opener collapses the continue range of the non-ace hands almost immediately.",
        "collected_rows": [
          {
            "source_ref": "cardplayer_ohel_nines",
            "evidence_type": "ace_up_asymmetry",
            "range_read": "A nine up should continue against an ace up only with trips, buried aces, or some very live suited wheel holdings; queens are out.",
            "notes": "This is the clearest public late-position continue boundary."
          },
          {
            "source_ref": "cardplayer_often_playable",
            "evidence_type": "steal_counterexample",
            "range_read": "568-type one-gappers can reraise a steal-position low-card complete and often hold an equity edge against the opener's light range.",
            "notes": "Used for the late steal-defense attack row."
          },
          {
            "source_ref": "cardplayer_sometimes_playable",
            "evidence_type": "legitimate_complete_warning",
            "range_read": "Rough razz lows are not for calling legitimate completes; their job is steals or bring-in defense.",
            "notes": "This keeps the late continue row from drifting into weak flats."
          },
          {
            "source_ref": "kogoro_stud8",
            "evidence_type": "japanese_fold_rule",
            "range_read": "889 without low support should fold to Q or K strength.",
            "notes": "Used as the visible high-strength fold example."
          }
        ]
      },
      "source_refs": [
        "pokernews_mixed_tips",
        "cardplayer_ohel_nines",
        "cardplayer_ante_stealing",
        "cardplayer_sometimes_playable",
        "cardplayer_often_playable",
        "kogoro_stud8"
      ]
    },
    "BI": {
      "label": "Bring-In",
      "seat_band": [
        "forced_bring_in_seat",
        "decision_changes_if_action_returns_unopened_or_facing_a_complete"
      ],
      "position_summary": "This is the forced bring-in seat. The meaningful split is between action returning uncompleted and defending after someone has already completed.",
      "caution_note": "Bring-in defense is structure-sensitive. High antes justify more defense and more reraising of the top of range, while low-ante games tighten both the steal and the defense sides.",
      "open_complete": {
        "section_label": "When Action Returns To The Bring-In",
        "anchor_profile": "complete wide only when the board lets the bring-in own the low up-card edge",
        "public_range_read": "If the bring-in is also the only low up-card and action returns unopened, complete very wide. If stronger low up-cards or an exposed ace remain to act, trapping with the bring-in and reraising later is preferred over blind auto-completion.",
        "table_columns": [
          "Band",
          "Reconstructed range / action"
        ],
        "table_rows": [
          [
            "Auto-complete zone",
            "Only low up-card showing and action comes back unraised; complete very wide"
          ],
          [
            "Complete or reraise for value",
            "Rolled-up trips, big pairs, AA+low, live ace-low three-card starts"
          ],
          [
            "Marginal continue",
            "One low plus one brick only when the hand still has two real ways of winning"
          ],
          [
            "Immediate muck",
            "Pure two-brick holdings once stronger up-cards have already shown interest"
          ]
        ],
        "source_note": "The bring-in row is not a normal open seat. The public overlap is 'complete very wide only when you own the lone low up-card edge, otherwise let stronger low or ace-up hands declare themselves first.'",
        "collected_rows": [
          {
            "source_ref": "pokerstars_p3",
            "evidence_type": "bring_in_rule",
            "range_read": "If you have the only low up-card, you can almost always complete when action comes back unopened.",
            "notes": "This is the cleanest public bring-in opening rule."
          },
          {
            "source_ref": "pokerstars_p3",
            "evidence_type": "anti_auto_complete_rule",
            "range_read": "In normal active games, do not auto-complete from the bring-in before seeing whether a better low or ace-up seat will complete anyway.",
            "notes": "Used to separate the auto-complete zone from the trap line."
          },
          {
            "source_ref": "pdf_aviator_rules",
            "evidence_type": "formal_rules_pdf",
            "range_read": "The low up-card brings in the action and completion restores the full bet in seven-card stud high-low split eight-or-better.",
            "notes": "Retained to confirm the formal meaning of completion and the 8-or-better qualifier."
          }
        ]
      },
      "versus_complete": {
        "section_label": "Defend Vs Complete",
        "anchor_profile": "tight versus ace-up strength, aggressive with the real top of range",
        "public_range_read": "Fold rough razz hands and two-brick holdings when a legitimate ace-up or strong complete attacks. Defend and often reraise with buried aces, trips, small pair plus ace, live ace-low hands, and the best wheel-card two-way starts. In high-ante games, reraising the top of range matters because passive defense lets late opens print too much.",
        "table_columns": [
          "Band",
          "Reconstructed continue range / action"
        ],
        "table_rows": [
          [
            "Reraise core",
            "Buried aces, trips, small pair plus ace, live A23 / A35 / A36, strong wheel-card two-way holdings"
          ],
          [
            "Call selectively",
            "One low plus real backdoor support, or disguised pair-plus-low hands that still realize well heads-up"
          ],
          [
            "Fold more often",
            "Two bricks, rough razz hands without an ace, queens or most nine-up holdings versus ace-up, and weak low-only hands with dead outs"
          ]
        ],
        "source_note": "The common public thread is that bring-in defense should tighten sharply versus ace-up strength, but the top of range must reraise often enough to keep late opens honest in high-ante structures.",
        "collected_rows": [
          {
            "source_ref": "cardplayer_defending_bring_in",
            "evidence_type": "high_ante_defense_framework",
            "range_read": "Defending frequencies depend on holding, pot odds, and opener position; the top of range should often reraise rather than just call, especially in high-ante games.",
            "notes": "This is the main public bring-in defense framework."
          },
          {
            "source_ref": "cardplayer_realizing_equity",
            "evidence_type": "fold_bad_razz_hands",
            "range_read": "Rough low hands without an ace should fold even when pot odds look appealing against an ace-up completion, while small pair plus ace and A-led three lows should rereraise by default.",
            "notes": "Used for the tight-versus-ace and reraise-core rows."
          },
          {
            "source_ref": "cardplayer_ohel_nines",
            "evidence_type": "ace_up_asymmetry",
            "range_read": "Nine up should continue against an ace up only with trips, buried aces, or very live suited wheel holdings.",
            "notes": "Used as the non-ace bring-in fold boundary."
          },
          {
            "source_ref": "pokerstars_p3",
            "evidence_type": "practical_bring_in_filters",
            "range_read": "Two bricks facing a complete and callers should fold immediately, while one low plus backdoor low or flush support can continue selectively.",
            "notes": "Used for the bottom of the defend row."
          }
        ]
      },
      "source_refs": [
        "pokerstars_p3",
        "cardplayer_defending_bring_in",
        "cardplayer_realizing_equity",
        "cardplayer_ohel_nines",
        "pdf_aviator_rules"
      ]
    }
  },
  "source_index": {
    "cardplayer_starting_hands": {
      "short_label": "Haney Starting Hands",
      "title": "Poker Strategy: Seven Card Stud Eight-or-Better Starting Hands",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/poker-news/26012-poker-strategy-seven-card-stud-eight-or-better-starting-hands"
    },
    "cardplayer_often_playable": {
      "short_label": "Haney Often",
      "title": "Seven Card Stud Eight-or-Better: Often Playable Hands",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/poker-news/26126-seven-card-stud-eight-or-better-often-playable-hands"
    },
    "cardplayer_sometimes_playable": {
      "short_label": "Haney Sometimes",
      "title": "Seven Card Stud Eight-or-Better: Sometimes Playable Hands",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66469-daniel-negreanu-34-18/articles/24318-seven-card-stud-eight-or-better-sometimes-playable-hands"
    },
    "cardplayer_ante_stealing": {
      "short_label": "Haney Antes",
      "title": "Seven Card Stud Eight-Or-Better: The Ante Structure And Stealing",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66464-wpt-crowns-trio-of-new-champions-34-13/articles/24272-seven-card-stud-eight-or-better-the-ante-structure-and-stealing"
    },
    "cardplayer_realizing_equity": {
      "short_label": "Haney Equity",
      "title": "Seven Card Stud Eight-or-Better: Realizing Your Equity",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66449-the-bicycle-hotel-casino-33-24/articles/24124-seven-card-stud-eight-or-better-realizing-your-equity"
    },
    "cardplayer_defending_bring_in": {
      "short_label": "Haney Bring-In",
      "title": "Seven Card Stud Eight-Or-Better: Defending The Bring-In",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66477-michael-addamo-34-26/articles/24393-seven-card-stud-eight-or-better-defending-the-bring-in"
    },
    "cardplayer_ohel_nines": {
      "short_label": "Ohel Nines",
      "title": "The Problem With Nines In Stud 8 Featuring Randy Ohel",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66481-ali-imsirovic-35-3/articles/24441-the-problem-with-nines-in-stud-8-featuring-randy-ohel"
    },
    "pokernews_mixed_tips": {
      "short_label": "PokerNews Tips",
      "title": "Five Tips That Will Help You Crush Mixed Games",
      "weight": "secondary",
      "source_type": "HTML",
      "url": "https://www.pokernews.com/strategy/five-tips-that-will-help-you-crush-mixed-games-29860.htm"
    },
    "pokerstars_p3": {
      "short_label": "PokerStars P3",
      "title": "Stud Hi/Lo: Third Street (Part 3)",
      "weight": "secondary",
      "source_type": "HTML",
      "url": "https://www.pokerstars.com/poker/learn/lesson/stud-hilo-third-p3/"
    },
    "kihara_blog": {
      "short_label": "Kihara Blog",
      "title": "Mix Games Recommendation: Stud Hi/Lo",
      "weight": "secondary",
      "source_type": "HTML",
      "url": "https://kihara-poker.hatenablog.com/entry/2018/07/15/143218"
    },
    "kogoro_stud8": {
      "short_label": "Kogoro Note",
      "title": "Stud 8 Basic Strategy",
      "weight": "secondary",
      "source_type": "HTML",
      "url": "https://note.com/556nip/n/nfd985e18f6f2"
    },
    "pdf_aviator_rules": {
      "short_label": "Aviator PDF",
      "title": "Seven-Card Stud High-Low Split (8-or-Better) Rules",
      "weight": "supplemental_pdf",
      "source_type": "PDF",
      "url": "https://oag.ca.gov/sites/all/files/agweb/pdfs/gambling/Aviator.pdf"
    }
  },
  "source_extracts": {
    "cardplayer_starting_hands": {
      "scope": "meta rule",
      "notes": [
        "No fixed starting-hand charts exist in stud because up-cards and prior action change the value of most hands."
      ]
    },
    "cardplayer_often_playable": {
      "scope": "often-playable classes",
      "position_notes": {
        "EP": "High pairs tighten sharply when an ace and many low cards remain behind.",
        "MP": "One-gappers and ace-seven or ace-eight lows become playable when live and shorthanded.",
        "LP": "568 and 578 type hands can pressure likely steals."
      }
    },
    "cardplayer_sometimes_playable": {
      "scope": "marginal and steal-only holdings",
      "position_notes": {
        "MP": "Medium pairs and low-pair-plus-high-kicker hands are mostly middle-or-later opens when the board behind is capped.",
        "LP": "Steal holdings expand strongly with an ace up or favorable dead cards.",
        "EP": "Rough razz lows should not cold-call legitimate completes."
      }
    },
    "cardplayer_ante_stealing": {
      "scope": "steal and ante structure",
      "position_notes": {
        "LP": "High antes widen steals, but the bring-in still defends better in Stud8 than in Stud High.",
        "BI": "Defense frequency changes materially with ante size and opener position."
      }
    },
    "cardplayer_realizing_equity": {
      "scope": "third-street playability and realization",
      "position_notes": {
        "EP": "Rough low hands without an ace fold versus ace-up strength.",
        "MP": "Small pair plus ace and ace-headed three lows should default to reraising.",
        "BI": "Bring-in defense should be driven by realization rather than raw hot-cold equity."
      }
    },
    "cardplayer_defending_bring_in": {
      "scope": "bring-in defense framework",
      "position_notes": {
        "BI": "Reraising strong two-way starts matters in high-ante structures to stop late opens from auto-profiting."
      }
    },
    "cardplayer_ohel_nines": {
      "scope": "ace-up versus nine-up asymmetry",
      "position_notes": {
        "LP": "Ace-up can open very wide versus a nine up and the bring-in.",
        "BI": "Non-ace defenders become extremely tight against an ace-up opener."
      }
    },
    "pokernews_mixed_tips": {
      "scope": "position shorthand",
      "position_notes": {
        "EP": "Open-raise three lows, a pair, or three-to-a-flush.",
        "MP": "Open-raise ace-plus-low combos.",
        "LP": "Open-raise almost any ace-up start unless another ace remains behind."
      }
    },
    "pokerstars_p3": {
      "scope": "bring-in and trap hands",
      "position_notes": {
        "BI": "Only low up-card can complete very wide when action returns unopened.",
        "EP": "Nine-based low traps and medium high pairs without low support should be downgraded."
      }
    },
    "kihara_blog": {
      "scope": "Japanese core framing",
      "position_notes": {
        "EP": "Three lows or a big pair are the default entry classes.",
        "LP": "Middle cards from nine to king are close to trash unless they already form a big pair."
      }
    },
    "kogoro_stud8": {
      "scope": "Japanese tier list and fold trims",
      "position_notes": {
        "EP": "Any-position core includes rolled-up trips, AA+low, suited low connectors, 88+low, 77+low, best pair, and A-led low hands.",
        "LP": "Suited high-plus-two-low holdings become late-position steals.",
        "EP_continue": "889 folds to Q or K strength when it lacks low support."
      }
    },
    "pdf_aviator_rules": {
      "scope": "formal rules PDF",
      "notes": [
        "Low up-card brings in the action.",
        "Completion restores the full bet.",
        "The low half uses an eight-or-better qualifier."
      ]
    }
  },
  "source_coverage": [
    {
      "source_ref": "cardplayer_starting_hands",
      "used_for": "chart boundary and non-fixed-chart warning",
      "positions": [
        "EP",
        "MP",
        "LP"
      ]
    },
    {
      "source_ref": "cardplayer_often_playable",
      "used_for": "one-gapper, ace-seven or ace-eight, and high-pair boundaries",
      "positions": [
        "EP",
        "MP",
        "LP"
      ]
    },
    {
      "source_ref": "cardplayer_sometimes_playable",
      "used_for": "steal-only holdings, medium pairs, and do-not-flat rough lows",
      "positions": [
        "EP",
        "MP",
        "LP"
      ]
    },
    {
      "source_ref": "cardplayer_ante_stealing",
      "used_for": "late-position steal guardrails and high-ante widening",
      "positions": [
        "LP",
        "BI"
      ]
    },
    {
      "source_ref": "cardplayer_realizing_equity",
      "used_for": "reraising ace-low and pair-plus-ace starts, and folding rough non-ace lows",
      "positions": [
        "EP",
        "MP",
        "BI"
      ]
    },
    {
      "source_ref": "cardplayer_defending_bring_in",
      "used_for": "bring-in defense framework and reraise-first logic",
      "positions": [
        "BI"
      ]
    },
    {
      "source_ref": "cardplayer_ohel_nines",
      "used_for": "ace-up late-position widening and ultra-tight non-ace defense versus ace-up",
      "positions": [
        "LP",
        "BI"
      ]
    },
    {
      "source_ref": "pokernews_mixed_tips",
      "used_for": "early, middle, and late position shorthand",
      "positions": [
        "EP",
        "MP",
        "LP"
      ]
    },
    {
      "source_ref": "pokerstars_p3",
      "used_for": "bring-in lines and trap-hand exclusions",
      "positions": [
        "BI",
        "EP"
      ]
    },
    {
      "source_ref": "kihara_blog",
      "used_for": "Japanese framing on low-card value and middle-card trash",
      "positions": [
        "EP",
        "LP"
      ]
    },
    {
      "source_ref": "kogoro_stud8",
      "used_for": "Japanese starting-hand hierarchy and visible fold trims",
      "positions": [
        "EP",
        "MP",
        "LP"
      ]
    },
    {
      "source_ref": "pdf_aviator_rules",
      "used_for": "formal bring-in, completion, and 8-or-better rules",
      "positions": [
        "BI"
      ]
    }
  ]
};

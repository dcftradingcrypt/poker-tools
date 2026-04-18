window.__BADUGI_PRE_DRAW_PUBLIC_RANGES_V1 = {
  "dataset_id": "badugi_pre_draw_position_ranges_v4",
  "version": 4,
  "scope": {
    "game": "fixed_limit_badugi",
    "phase": "before_first_draw",
    "primary_view": "position_first",
    "table_format": "6-max public baseline",
    "position_buttons": [
      "EP",
      "MP",
      "CO",
      "BTN",
      "SB",
      "BB"
    ],
    "defense_only_positions": [
      "BB"
    ],
    "position_button_meaning": "First Position, Hijack, Cutoff, Button, Small Blind, and Big Blind"
  },
  "strength_primer": {
    "hand_class_order": [
      "any 4-card badugi beats any 3-card incomplete hand",
      "any 3-card incomplete hand beats any 2-card incomplete hand",
      "any 2-card incomplete hand beats any 1-card incomplete hand"
    ],
    "rank_order_rule": "within the same card-count class, lower high card is better, then lower next-highest card, and so on",
    "normalization_rule": "two-card starts are stored as unordered start classes such as A2, A3, 23, A4, 24, 34, A5, 25, 35, 45"
  },
  "collection_notes": [
    "CountingOuts Part 3 is still the only explicit public first-in chart, so its percentages remain the exact anchor rows.",
    "This surface no longer merges every mention into one giant open union. Each position separates exact chart anchor, practical core, conditional adds, and default folds.",
    "Raise-facing sections are reconstructed from CountingOuts Part 4, Danzer, Ohel, and concrete blind-defense examples in CountingOuts Parts 1, 5, and 6. They are guidance bands, not an exact solver matrix.",
    "The previous broad MP two-card row and broad BTN 6-high / 7-high / 8-high default two-card fringe were removed as defaults because the stronger public overlap does not support them.",
    "PDF material is kept as corroboration and wording support, not as authority that overrides the stronger HTML chart and article evidence."
  ],
  "verification": {
    "checked_on": "2026-04-18",
    "method": "CountingOuts Part 1 / 3 / 4 / 5 / 6, Kevin Haney opening / tri / two-card articles, Randy Ohel, George Danzer, CardPlayer opening-standards PDF, and the Ryan Eccles Scribd PDF were re-read and reduced into position-first open / raise-facing bands.",
    "confirmed_source_refs": [
      "countingouts_p1",
      "countingouts_p3",
      "countingouts_p4",
      "countingouts_p5",
      "countingouts_p6",
      "haney_opening",
      "haney_opening_pdf",
      "haney_three_card",
      "haney_two_card",
      "ohel_fundamentals",
      "danzer_interview",
      "pdf_badugi_guide"
    ]
  },
  "global_source_refs": [
    "countingouts_p3",
    "countingouts_p4",
    "haney_opening",
    "haney_opening_pdf",
    "haney_three_card",
    "haney_two_card",
    "ohel_fundamentals",
    "danzer_interview",
    "pdf_badugi_guide"
  ],
  "position_order": [
    "EP",
    "MP",
    "CO",
    "BTN",
    "SB",
    "BB"
  ],
  "positions": {
    "EP": {
      "label": "アーリーポジション",
      "role_label": "first-in anchor seat",
      "open_band": "14.3%基準 / 実戦では13〜14%",
      "versus_open_band": "do not defend marginal early opens",
      "position_summary": "最初の位置です。利益の中心は強い3枚で、弱い完成形や2枚ドローは基本レンジに入れません。",
      "caution_note": "Jの完成形や崩せるQ・Kは端の候補であって、3枚の代わりに大量に入れる手ではありません。",
      "overview": {
        "seat_trigger": "まだ 5 人が残っており、pat badugi と multi-way の reverse implied odds が最も重い位置です。",
        "open_identity": "利益の中心は premium tri です。弱い pat badugi は \"完成している\" ことだけでは enough ではありません。",
        "adds_here": "chart edge として pat J と breakable Q/K が残りますが、Haney の practical row では strong underside 条件が付きます。",
        "still_avoid": "two-card draw の default open、rough 8-tri、弱い unbreakable J/Q/K pat は残しません。"
      },
      "at_a_glance": {
        "open_core": "T-high+ pat badugi / all 7-tri / smooth 8-tri",
        "position_add": "pat J with strong underside / breakable Q-K at the chart edge",
        "vs_open": "non-BB continue は value-heavy。marginal UTG opens を守りにいかない。",
        "snap_fold": "all D2 / rough 8-tri / weak unbreakable J-Q-K pat"
      },
      "open_section": {
        "section_label": "オープンレンジ",
        "anchor_profile": "14.3% exact chart / 13-14% practical",
        "public_range_read": "UTG は exact chart をそのまま union 化するより、exact anchor と practical core を分けて読む方がズレません。公開 overlap は tri-first で、弱い pat と D2 はここでは主役になりません。",
        "table_columns": [
          "区分",
          "ハンドレンジ"
        ],
        "table_rows": [
          [
            "基準レンジ",
            "J以上のバドゥーギー / 崩せるQ・Kのバドゥーギー / 75X以上の3枚"
          ],
          [
            "実戦の中心",
            "T以上のバドゥーギー / すべての7の3枚 / スムーズな8の3枚"
          ],
          [
            "基本的に外す手",
            "すべての2枚ドロー / ラフな8の3枚 / 弱いJ〜Kの完成形"
          ]
        ],
        "range_groups": [
          {
            "label": "Published Anchor",
            "tone": "attack",
            "items": [
              "J-high+ badugi",
              "breakable Q-K badugi",
              "75X+ tri"
            ]
          },
          {
            "label": "Practical Core",
            "tone": "attack",
            "items": [
              "T-high+ pat",
              "all 7-tri",
              "smooth 8-tri"
            ]
          },
          {
            "label": "Do Not Auto-Open",
            "tone": "fold",
            "items": [
              "A2 / A3 / 23 / A4 D2",
              "rough 8-tri",
              "weak pat J-Q-K"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Default raise",
            "tone": "attack",
            "range_read": "Raise the tri-led core: all 7-tri, smooth 8-tri, and only the stronger made badugis.",
            "when": "6-max first-in",
            "examples": "A23x / 467x / 238x / T-high badugi"
          },
          {
            "label": "Edge only",
            "tone": "conditional",
            "range_read": "Pat J and breakable Q/K live only at the edge, not as a bulk replacement for tri hands.",
            "when": "passive lineup or strong underside",
            "examples": "Q632 / breakable K with a strong tri underneath"
          },
          {
            "label": "Snap fold",
            "tone": "fold",
            "range_read": "Keep every two-card draw and every rough 8 out of the UTG default row.",
            "when": "normal fixed-limit table",
            "examples": "A2xx / A3xx / 278x / weak J-Q-K pat"
          }
        ],
        "source_note": "CountingOuts supplies the literal 14.3% row. Haney and the CardPlayer PDF explain why the practical UTG row should be read as tri-heavy rather than as permission to mass-open weak pat badugis.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "explicit_chart",
            "range_read": "EP 14.3%: J-high or better badugi, breakable Q/K badugi, 75X+ tri.",
            "notes": "only explicit public first-in chart row"
          },
          {
            "source_ref": "haney_opening",
            "evidence_type": "direct_text",
            "range_read": "Suggested first-position row plays around 13-14% and prefers 7-tri plus smooth 8-tri over extra weak pats.",
            "notes": "weak pat-jacks often fold unless the underside is strong"
          },
          {
            "source_ref": "haney_three_card",
            "evidence_type": "direct_text",
            "range_read": "A seven-tri or better is playable from any position; select smooth 8-tri also work from the first two seats.",
            "notes": "smoothness matters"
          },
          {
            "source_ref": "haney_opening_pdf",
            "evidence_type": "supporting_pdf",
            "range_read": "CardPlayer PDF reproduces the suggested default opening chart and the 13-14% practical row.",
            "notes": "PDF cross-check"
          },
          {
            "source_ref": "haney_two_card",
            "evidence_type": "direct_text",
            "range_read": "Two-card draws should not be played from early position.",
            "notes": "late-open / BB-defense only bias"
          },
          {
            "source_ref": "pdf_badugi_guide",
            "evidence_type": "supplemental_pdf",
            "range_read": "Early position: play any 3 cards under a 7.",
            "notes": "older shorthand PDF; corroboration only"
          }
        ]
      },
      "versus_section": {
        "section_label": "After You Open / Facing Pressure",
        "anchor_profile": "continue value-heavy / no marginal defense",
        "public_range_read": "公開ソースは EP open defense の exact matrix を出していません。重なる部分はもっと単純で、non-BB continue は raise-or-fold に寄り、marginal early opens を守りすぎないことです。",
        "table_columns": [
          "Band",
          "Hand classes",
          "How to use"
        ],
        "table_rows": [
          [
            "Keep going",
            "Made badugis; premium 7-tri; best smooth 8-tri",
            "non-BB continue は face-up flat より value-heavy"
          ],
          [
            "Borderline only",
            "Strong pat J with real underside value",
            "close and lineup dependent"
          ],
          [
            "Release",
            "Chart-edge Q/K, weak J, rough 8-tri, exploit-only D2",
            "public overlap gives no reason to defend these wide"
          ]
        ],
        "range_groups": [
          {
            "label": "Continue Strongly",
            "tone": "attack",
            "items": [
              "made badugis",
              "premium 7-tri",
              "best smooth 8-tri"
            ]
          },
          {
            "label": "Rare Continue",
            "tone": "conditional",
            "items": [
              "strong pat J",
              "smoothest 8-tri only"
            ]
          },
          {
            "label": "Release",
            "tone": "fold",
            "items": [
              "edge Q-K pat",
              "weak J pat",
              "rough 8-tri",
              "all D2"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Do not get sticky",
            "tone": "fold",
            "range_read": "If you only opened because the hand was at the edge of the UTG row, it is not supposed to continue far once real pressure appears.",
            "when": "after opening EP",
            "examples": "chart-edge breakable Q-K / weak pat J / rough 8"
          },
          {
            "label": "Continue with real value",
            "tone": "attack",
            "range_read": "Made badugis and premium tri remain the part of range that can keep playing aggressively.",
            "when": "facing re-raise or strong draw-pressure",
            "examples": "T+ pat / 7-tri / best smooth 8-tri"
          }
        ],
        "source_note": "This is a reconstructed discipline panel, not a published UTG defense chart. The support is the non-BB raise-or-fold rule and Haney's repeated warning that weak pats and D2 perform poorly under pressure.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "direct_text",
            "range_read": "Outside the big blind, continue ranges should almost always re-raise rather than cold-call.",
            "notes": "global non-BB discipline"
          },
          {
            "source_ref": "countingouts_p4",
            "evidence_type": "reconstructed_threshold",
            "range_read": "J+ badugi and A36+ is the tight three-bet floor against very tight ranges.",
            "notes": "supporting floor, not a literal EP-open defense chart"
          },
          {
            "source_ref": "haney_opening",
            "evidence_type": "direct_text",
            "range_read": "Weak pat-jacks often fold unless the underside is strong.",
            "notes": "why chart-edge pats should not over-defend"
          }
        ]
      },
      "source_refs": [
        "countingouts_p3",
        "countingouts_p4",
        "haney_opening",
        "haney_opening_pdf",
        "haney_three_card",
        "haney_two_card",
        "pdf_badugi_guide"
      ]
    },
    "MP": {
      "label": "ハイジャック",
      "role_label": "second seat / HJ opener",
      "open_band": "18.2%基準 / 最良のA2・A3だけ追加",
      "versus_open_band": "J+ badugi / A36+ tight continue",
      "position_summary": "EPより1段だけ広げる位置です。まだ低い2枚ドローをまとめて入れる場所ではありません。",
      "caution_note": "A2・A3でも良いブロッカー付きだけを少量追加するくらいで、23・A4・24を自動で開く位置ではありません。",
      "overview": {
        "seat_trigger": "まだ 4 人が残っており、multi-way も pat collision も十分あります。",
        "open_identity": "7-tri を軸にしつつ、smooth 8 を少し増やす seat です。",
        "adds_here": "best A2/A3 D2 with blockers がようやく候補に入ります。",
        "still_avoid": "23 / A4 / 24 の routine open や full 5-high D2 ladder はまだ default にしません。"
      },
      "at_a_glance": {
        "open_core": "strong J-T+ pat / all 7-tri / reducible 8-tri / best A2-A3 D2",
        "position_add": "pat J more often / blocker-rich A2-A3",
        "vs_open": "EP open には J+ badugi / A36+ 近辺から。flat D2 は作らない。",
        "snap_fold": "23-A4-24 as auto-open / rough 8-tri / weak pat Q-K"
      },
      "open_section": {
        "section_label": "オープンレンジ",
        "anchor_profile": "18.2% exact chart / best low D2 only",
        "public_range_read": "HJ は exact anchor と practical read のズレが大きい seat です。CountingOuts の explicit row は no-D2 ですが、Haney は very best low D2 を少量だけ足します。ここを全部の 2-high through 5-high に広げると default としては行きすぎます。",
        "table_columns": [
          "区分",
          "ハンドレンジ"
        ],
        "table_rows": [
          [
            "基準レンジ",
            "Q以上のバドゥーギー / 崩せるKのバドゥーギー / A48以上の3枚"
          ],
          [
            "実戦の中心",
            "T〜強いJのバドゥーギー / すべての7の3枚 / 減りやすい8の3枚 / 最良のA2・A3"
          ],
          [
            "基本的に外す手",
            "23・A4・24の常用オープン / 5スタート2枚ドロー全般 / 減りにくい8の3枚"
          ]
        ],
        "range_groups": [
          {
            "label": "Published Anchor",
            "tone": "attack",
            "items": [
              "Q-high+ badugi",
              "breakable K",
              "A48+ tri"
            ]
          },
          {
            "label": "Practical Core",
            "tone": "conditional",
            "items": [
              "T-high+ or strong J pat",
              "all 7-tri",
              "reducible 8-tri",
              "best A2",
              "best A3"
            ]
          },
          {
            "label": "Not Default",
            "tone": "fold",
            "items": [
              "23",
              "A4",
              "24",
              "A5-25-35-45",
              "rough 8-tri"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Default raise",
            "tone": "attack",
            "range_read": "Keep HJ open tri-led and let only the best blocker-rich D2 enter.",
            "when": "6-max HJ first-in",
            "examples": "7-tri / smooth 8-tri / premium A3 with low blockers"
          },
          {
            "label": "Conditioned adds",
            "tone": "conditional",
            "range_read": "Pat J and premium A2-A3 without ideal blockers are still closer than they look and want a calmer lineup.",
            "when": "players behind are not loose and aggressive",
            "examples": "J pat / A3 with low spade blockers"
          },
          {
            "label": "Skip as default",
            "tone": "fold",
            "range_read": "Do not turn the older PDF shorthand into a full MP two-card ladder.",
            "when": "baseline public surface",
            "examples": "23 / A4 / 24 / generic 5-high D2"
          }
        ],
        "source_note": "The current repo MP row was widened too far. Haney's text supports beginning with only the very best low D2, not the whole 2-high through 5-high class ladder.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "explicit_chart",
            "range_read": "MP 18.2%: Q-high or better badugi, breakable K, A48+ tri.",
            "notes": "literal HJ anchor"
          },
          {
            "source_ref": "haney_opening",
            "evidence_type": "direct_text",
            "range_read": "Hijack opens a few more 8-tri and only the very best two-card draws with useful blockers.",
            "notes": "best low D2 only"
          },
          {
            "source_ref": "haney_three_card",
            "evidence_type": "direct_text",
            "range_read": "Any 7-tri is playable and smooth 8-tri is the next practical layer.",
            "notes": "why rough 8s are still not default"
          },
          {
            "source_ref": "haney_opening_pdf",
            "evidence_type": "supporting_pdf",
            "range_read": "CardPlayer PDF shows HJ as the first seat where premium A2-A3 with blockers begin to appear.",
            "notes": "PDF wording support"
          },
          {
            "source_ref": "pdf_badugi_guide",
            "evidence_type": "supplemental_pdf",
            "range_read": "Mid position adds any 2 cards under a 5.",
            "notes": "kept only as shorthand support, not default authority"
          }
        ]
      },
      "versus_section": {
        "section_label": "Facing an Earlier Open",
        "anchor_profile": "J+ badugi / A36+ tight continue floor",
        "public_range_read": "HJ facing EP open is still a tight continue spot with many players left. The overlap across public sources is 3-bet or fold by default, with Danzer allowing only very close calls in tighter full-ring style spots.",
        "table_columns": [
          "Band",
          "Hand classes",
          "How to use"
        ],
        "table_rows": [
          [
            "Tight 3-bet core",
            "J+ badugi; A36+",
            "CountingOuts Part 4 の tight floor"
          ],
          [
            "Close exceptions",
            "Three low cards below a six in very tight full-ring style spots",
            "Danzer の call 例外"
          ],
          [
            "Default fold",
            "Any D2 cold-call; rough 8-tri; weak pats",
            "non-BB cold-calling is face-up and weakい"
          ]
        ],
        "range_groups": [
          {
            "label": "3-Bet Core",
            "tone": "attack",
            "items": [
              "J+ badugi",
              "A36+"
            ]
          },
          {
            "label": "Close Flat Only",
            "tone": "conditional",
            "items": [
              "sub-6 smooth tri in tight games"
            ]
          },
          {
            "label": "Skip",
            "tone": "fold",
            "items": [
              "all D2 cold-calls",
              "rough 8-tri",
              "weak pat hands"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Mostly 3-bet or fold",
            "tone": "attack",
            "range_read": "Non-BB continue is not a wide flatting game. Start around J+ badugi and A36+ when you face an EP open.",
            "when": "HJ vs EP open",
            "examples": "J pat / A36 / 346 and better"
          },
          {
            "label": "Flat only when truly close",
            "tone": "conditional",
            "range_read": "Danzer's exception is for close full-ring style spots, not for routine 6-max cold-calling.",
            "when": "very tight opener / little squeeze risk",
            "examples": "three low cards lower than six"
          },
          {
            "label": "Never turn D2 into a cold-call range",
            "tone": "fold",
            "range_read": "Haney explicitly flags early / cold-call D2 habits as a leak.",
            "when": "facing an open",
            "examples": "A2 / A3 / 23 smooth-calls"
          }
        ],
        "source_note": "The HJ continue row is guidance, not an exact matrix. The strong overlap is the tight Part 4 floor plus Danzer's narrow close-call exception.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p4",
            "evidence_type": "direct_text",
            "range_read": "Against even the tightest ranges, J+ badugi and A36+ appears to be a reasonable three-bet floor.",
            "notes": "tight continue baseline"
          },
          {
            "source_ref": "danzer_interview",
            "evidence_type": "rule_of_thumb",
            "range_read": "If it is very close, calling can be fine; with three cards lower than a six from the small blind versus early position at full ring, call can be reasonable.",
            "notes": "exception only"
          },
          {
            "source_ref": "haney_two_card",
            "evidence_type": "direct_text",
            "range_read": "Do not get in the habit of cold-calling three-bets or playing D2 too much from early seats.",
            "notes": "why D2 flats stay out"
          }
        ]
      },
      "source_refs": [
        "countingouts_p3",
        "countingouts_p4",
        "haney_opening",
        "haney_opening_pdf",
        "haney_three_card",
        "haney_two_card",
        "pdf_badugi_guide",
        "danzer_interview"
      ]
    },
    "CO": {
      "label": "カットオフ",
      "role_label": "late-position expansion seat",
      "open_band": "28.3%基準 / A2・A3中心、23・A4・24は条件付き",
      "versus_open_band": "J+ / A36+ core, widen to Q+ / A37+ vs loose opens",
      "position_summary": "後ろが3人だけになる最初の位置で、A2・A3が中心に入ります。23・A4・24は条件が良いときだけ追加します。",
      "caution_note": "弱い完成形をどこまで開くかはソース差があるので、ここでは安全側に寄せて見せています。",
      "overview": {
        "seat_trigger": "後ろは 3 人だけなので position realization が一気に改善します。",
        "open_identity": "8-tri と A2-A3 が row の中心です。",
        "adds_here": "23 / A4 / 24 が blocker と players behind によって入ります。",
        "still_avoid": "bad-blocker D2、rough 9-tri、generic 6-high+ D2 を default にしません。"
      },
      "at_a_glance": {
        "open_core": "published all badugis / 8-tri+ / A2-A3",
        "position_add": "23 / A4 / 24 with blockers / softer players behind",
        "vs_open": "earlier open には J+ / A36+ を core に、loose opener にだけ Q+ / A37+ へ widen",
        "snap_fold": "bad-blocker D2 / rough 9-tri / face-up cold-call D2"
      },
      "open_section": {
        "section_label": "オープンレンジ",
        "anchor_profile": "28.3% exact chart / Q-high+ practical pat default",
        "public_range_read": "CO は exact chart と practical pat row の差を honest に残すべき seat です。exact anchor は all badugi + 8-tri+ + A2/A3 ですが、Haney は weak pat を tighter に読み、23/A4/24 を judgment call に置きます。",
        "table_columns": [
          "区分",
          "ハンドレンジ"
        ],
        "table_rows": [
          [
            "基準レンジ",
            "すべてのバドゥーギー / 8以下の3枚 / A2・A3"
          ],
          [
            "実戦の中心",
            "Q以上のバドゥーギーを基本 / 8以下の3枚 / A2・A3"
          ],
          [
            "条件付きで追加",
            "23・A4・24。ブロッカーが良く、後ろやブラインドが弱いとき"
          ],
          [
            "基本的に外す手",
            "ラフな9の3枚 / 34・A5・25の常用 / 6以上の2枚ドロー"
          ]
        ],
        "range_groups": [
          {
            "label": "Published Anchor",
            "tone": "attack",
            "items": [
              "all badugis",
              "8-tri+",
              "A2",
              "A3"
            ]
          },
          {
            "label": "Practical Tighten",
            "tone": "conditional",
            "items": [
              "Q-high+ everyday pat default",
              "23",
              "A4",
              "24"
            ]
          },
          {
            "label": "Do Not Auto-Add",
            "tone": "fold",
            "items": [
              "34",
              "A5",
              "25",
              "rough 9-tri",
              "6-high+ D2"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Default raise",
            "tone": "attack",
            "range_read": "Open the exact late anchor first: 8-tri+, A2-A3, and the stronger pat badugis.",
            "when": "CO first-in",
            "examples": "578 tri / A2 / A3 / Q-high pat"
          },
          {
            "label": "Judgment adds",
            "tone": "conditional",
            "range_read": "23, A4, and 24 move in only when blockers and players behind cooperate.",
            "when": "good blockers / soft blinds / passive players behind",
            "examples": "23 with low spade blockers / A4 with helpful discards"
          },
          {
            "label": "Still not default",
            "tone": "fold",
            "range_read": "Do not let the late-position idea drift into a generic 34-A5-25-6-high D2 shell from cutoff.",
            "when": "baseline row",
            "examples": "34 / A5 / 25 / 56 / rough 9"
          }
        ],
        "source_note": "CO is where the current repo needed the biggest cleanup. The strong overlap is not \"all low two-card hands\"; it is A2-A3 core, with 23-A4-24 only as conditional adds.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "explicit_chart",
            "range_read": "CO 28.3%: all badugis, 8-tri or better, A2 and A3.",
            "notes": "literal public anchor"
          },
          {
            "source_ref": "haney_opening",
            "evidence_type": "direct_text",
            "range_read": "Q-high or better badugi is the practical recommendation; any 8-tri is worth opening; A2-A3 are standard; 23-A4-24 are judgment calls.",
            "notes": "main practical filter"
          },
          {
            "source_ref": "haney_two_card",
            "evidence_type": "direct_text",
            "range_read": "Late position is where two-card draws begin to make practical sense.",
            "notes": "late-open support, not blanket approval"
          },
          {
            "source_ref": "haney_opening_pdf",
            "evidence_type": "supporting_pdf",
            "range_read": "The CardPlayer PDF shows CO as the first seat where 23, A4, and 24 become candidate adds rather than folds by default.",
            "notes": "PDF cross-check"
          },
          {
            "source_ref": "danzer_interview",
            "evidence_type": "rule_of_thumb",
            "range_read": "Cutoff and button can loosen to two cards five or lower and one-card draws to a six or seven.",
            "notes": "broad support for late widening"
          }
        ]
      },
      "versus_section": {
        "section_label": "Facing an Earlier Open",
        "anchor_profile": "J+ / A36+ core, widen to Q+ / A37+ vs loose opener",
        "public_range_read": "CO is late enough to widen a little versus loose early opens, but public continues are still 3-bet heavy rather than flat heavy. The safe baseline is J+ badugi and A36+, then widen toward Q+ and A37+ only when the opener is loose enough.",
        "table_columns": [
          "Band",
          "Hand classes",
          "How to use"
        ],
        "table_rows": [
          [
            "Tight continue core",
            "J+ badugi; A36+",
            "tight or solid EP-HJ opener"
          ],
          [
            "Loose-opener widen",
            "Q+ badugi; A37+",
            "late position versus looser early opens"
          ],
          [
            "Default fold",
            "D2 cold-calls; marginal 8-tri; weak pats",
            "non-BB flat remains poor"
          ]
        ],
        "range_groups": [
          {
            "label": "Core 3-Bet",
            "tone": "attack",
            "items": [
              "J+ badugi",
              "A36+"
            ]
          },
          {
            "label": "Loose-Opener Widen",
            "tone": "conditional",
            "items": [
              "Q+ badugi",
              "A37+"
            ]
          },
          {
            "label": "Skip",
            "tone": "fold",
            "items": [
              "D2 cold-calls",
              "marginal 8-tri",
              "weak pat hands"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "3-bet the real continue range",
            "tone": "attack",
            "range_read": "Part 4's tight floor starts at J+ badugi and A36+; use that before inventing CO flatting ranges.",
            "when": "CO facing EP-HJ open",
            "examples": "J pat / A36 / 346 and better"
          },
          {
            "label": "Widen only versus weak opens",
            "tone": "conditional",
            "range_read": "Q+ badugi and A37+ belong to later-vs-later or looser-opener branches, not to every EP open.",
            "when": "loose early opener",
            "examples": "Q pat / A37"
          },
          {
            "label": "No D2 cold-call row",
            "tone": "fold",
            "range_read": "Keep A2-A4 type hands out of the CO continue row unless you are the big blind.",
            "when": "facing a raise",
            "examples": "A2 / A3 / 23 flats"
          }
        ],
        "source_note": "This panel uses CountingOuts Part 4 as the main continue threshold and keeps Danzer's call exception as a narrow supporting caveat only.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p4",
            "evidence_type": "direct_text",
            "range_read": "Against even the tightest ranges, J+ badugi and A36+ is reasonable. In late position versus a cutoff or loose early opener, Q+ badugi and A37+ can enter.",
            "notes": "main continue ladder"
          },
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "direct_text",
            "range_read": "Outside the big blind, continuing hands should almost always be re-raised rather than cold-called.",
            "notes": "why CO flatting stays thin"
          },
          {
            "source_ref": "danzer_interview",
            "evidence_type": "rule_of_thumb",
            "range_read": "Calling is only fine when the situation is very close.",
            "notes": "exception, not default"
          }
        ]
      },
      "source_refs": [
        "countingouts_p3",
        "countingouts_p4",
        "haney_opening",
        "haney_opening_pdf",
        "haney_three_card",
        "haney_two_card",
        "danzer_interview"
      ]
    },
    "BTN": {
      "label": "ボタン",
      "role_label": "widest first-in seat",
      "open_band": "38.2%基準 / 9の3枚と良質な2枚ドローまで",
      "versus_open_band": "J+ / A36+ vs tight, Q+ / A37+ vs CO",
      "position_summary": "唯一、どんな完成形でも開ける位置です。9の3枚や低い2枚ドローも広がりますが、34やA5にはまだ条件が残ります。",
      "caution_note": "6以上の2枚ドローを全部デフォルトで開くほどは広げません。広げるのは強いブロッカーや相手の降りすぎがあるときだけです。",
      "overview": {
        "seat_trigger": "後ろは blind だけで、steal EV が row の bottom を支えます。",
        "open_identity": "any badugi、rough 9-tri、A2-A4 系 D2 が button row の芯です。",
        "adds_here": "34 と A5 は good blockers が付いたときに入ります。",
        "still_avoid": "very rough 9、bad-blocker D2、generic 6-high+ D2 は default にしません。"
      },
      "at_a_glance": {
        "open_core": "all badugis / 9-tri+ / A2-A3-23-A4 / most 24",
        "position_add": "34 and A5 with good blockers",
        "vs_open": "tight opener には J+ / A36+、CO や loose opener には Q+ / A37+",
        "snap_fold": "very rough 9 / bad-blocker 34-A5-25 / fake wide D2 union"
      },
      "open_section": {
        "section_label": "オープンレンジ",
        "anchor_profile": "38.2% exact chart / blocker-qualified late D2 fringe",
        "public_range_read": "Button is the only row where any badugi and rough 9-tri are public baseline. The late D2 shell is wide, but it is still not a license to auto-open every 6-high, 7-high, or 8-high two-card class.",
        "table_columns": [
          "区分",
          "ハンドレンジ"
        ],
        "table_rows": [
          [
            "基準レンジ",
            "すべてのバドゥーギー / 9以下の3枚 / A2・A3・23・A4"
          ],
          [
            "実戦の中心",
            "すべてのバドゥーギー / ラフな9の3枚 / A2・A3 / 23・A4・24の大半"
          ],
          [
            "条件付きで追加",
            "34 と A5。良いブロッカー付きのとき"
          ],
          [
            "基本的に外す手",
            "6〜8スタートの2枚ドロー全般 / かなりラフな9の3枚 / ブロッカーの悪い34・A5・25"
          ]
        ],
        "range_groups": [
          {
            "label": "Published Anchor",
            "tone": "attack",
            "items": [
              "all badugis",
              "9-tri+",
              "A2",
              "A3",
              "23",
              "A4"
            ]
          },
          {
            "label": "Practical Core",
            "tone": "attack",
            "items": [
              "most 24",
              "rough 9-tri",
              "any badugi"
            ]
          },
          {
            "label": "Blocker Adds",
            "tone": "conditional",
            "items": [
              "34 with good blockers",
              "A5 with good blockers"
            ]
          },
          {
            "label": "Do Not Auto-Union",
            "tone": "fold",
            "items": [
              "all 6-high D2",
              "all 7-high D2",
              "all 8-high D2",
              "very rough 9",
              "bad-blocker 25"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Default raise",
            "tone": "attack",
            "range_read": "Button is where any badugi and rough 9-tri become normal steal hands.",
            "when": "BTN first-in",
            "examples": "K-high badugi / 579 tri / A2 / A3 / 23 / A4"
          },
          {
            "label": "Add only with blockers",
            "tone": "conditional",
            "range_read": "34 and A5 move in only when the discards help rather than hurt your draw.",
            "when": "good blockers / over-folding blinds",
            "examples": "34 with low blockers / A5 with good suit effects"
          },
          {
            "label": "Do not fake a giant D2 shell",
            "tone": "fold",
            "range_read": "The stronger public overlap does not support turning every 6-high, 7-high, or 8-high D2 into the baseline button row.",
            "when": "default public chart",
            "examples": "56 / 67 / 78 without a strong exploit"
          }
        ],
        "source_note": "This is the seat where the older JSON drifted into a list of everything mentioned anywhere. The rebuilt row keeps the exact chart, the late practical core, and the blocker-only fringe separate.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "explicit_chart",
            "range_read": "BTN 38.2%: all badugis, 9-tri or better, A2, A3, 23, A4.",
            "notes": "literal public anchor"
          },
          {
            "source_ref": "haney_opening",
            "evidence_type": "direct_text",
            "range_read": "Any badugi is playable from the button; rough 9-tri belongs here; any A2 or A3, most 23/A4/24, and 34/A5 with good blockers are opens.",
            "notes": "main button practical row"
          },
          {
            "source_ref": "haney_three_card",
            "evidence_type": "direct_text",
            "range_read": "Only on the button should rough nine-high tris enter the open range.",
            "notes": "9-tri threshold"
          },
          {
            "source_ref": "ohel_fundamentals",
            "evidence_type": "direct_text",
            "range_read": "When opening the button, you can open any badugi.",
            "notes": "button badugi breadth"
          },
          {
            "source_ref": "haney_opening_pdf",
            "evidence_type": "supporting_pdf",
            "range_read": "The CardPlayer PDF shows the exact button shell and explicitly places 34/A5 in a blocker-qualified add band.",
            "notes": "PDF cross-check"
          }
        ]
      },
      "versus_section": {
        "section_label": "Facing an Open",
        "anchor_profile": "J+ / A36+ vs tight, Q+ / A37+ vs CO",
        "public_range_read": "Button is the cleanest in-position continue seat. The public baseline is still aggressive rather than passive: J+ badugi and A36+ against tight ranges, widening to Q+ badugi and A37+ against CO or loose early opens. D2 cold-calls remain outside the core.",
        "table_columns": [
          "Band",
          "Hand classes",
          "How to use"
        ],
        "table_rows": [
          [
            "Tight-opener 3-bet",
            "J+ badugi; A36+",
            "tight early opener"
          ],
          [
            "CO or loose-opener widen",
            "Q+ badugi; A37+",
            "late-vs-late / loose early branches"
          ],
          [
            "Flat exceptions only",
            "Very close smooth tri spots",
            "no default D2 cold-call matrix"
          ]
        ],
        "range_groups": [
          {
            "label": "3-Bet Core",
            "tone": "attack",
            "items": [
              "J+ badugi",
              "A36+"
            ]
          },
          {
            "label": "Late / Loose Widen",
            "tone": "conditional",
            "items": [
              "Q+ badugi",
              "A37+"
            ]
          },
          {
            "label": "Not a D2 Flat Seat",
            "tone": "fold",
            "items": [
              "A2-A4 flats",
              "23 flats",
              "rough tri below floor"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Continue aggressively",
            "tone": "attack",
            "range_read": "Button is where the late-position Part 4 widen matters most, but the action still starts from a 3-bet rather than a passive cold-call.",
            "when": "BTN facing EP-HJ-CO open",
            "examples": "J pat / Q pat vs CO / A36 / A37"
          },
          {
            "label": "Flat only when truly close",
            "tone": "conditional",
            "range_read": "Danzer's close-call allowance exists, but it is an exception and mostly for near-threshold smooth tri hands.",
            "when": "very close spots",
            "examples": "smooth sub-6 tri"
          },
          {
            "label": "Skip D2 flats",
            "tone": "fold",
            "range_read": "Haney's two-card article does not support turning button continue into an A2-A4 cold-call range.",
            "when": "facing a raise",
            "examples": "A2 / A3 / 23 / A4 flats"
          }
        ],
        "source_note": "The button keep-playing row is still a re-raise-first surface. In-position comfort does not create a public D2 cold-call matrix.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p4",
            "evidence_type": "direct_text",
            "range_read": "Tight floor is J+ badugi and A36+; late-position widen is Q+ badugi and A37+ versus CO or loose opens.",
            "notes": "main continue thresholds"
          },
          {
            "source_ref": "danzer_interview",
            "evidence_type": "rule_of_thumb",
            "range_read": "When it is very close, calling can be fine.",
            "notes": "close-call exception only"
          },
          {
            "source_ref": "haney_two_card",
            "evidence_type": "direct_text",
            "range_read": "Two-card draws belong mainly to late opens or big blind defense, not routine cold-calls.",
            "notes": "why D2 flats stay out"
          }
        ]
      },
      "source_refs": [
        "countingouts_p3",
        "countingouts_p4",
        "haney_opening",
        "haney_opening_pdf",
        "haney_three_card",
        "haney_two_card",
        "ohel_fundamentals",
        "danzer_interview"
      ]
    },
    "SB": {
      "label": "スモールブラインド",
      "role_label": "blind-war expansion seat",
      "open_band": "可変 / ボタン基準 + 相手次第で追加",
      "versus_open_band": "3-bet-or-fold baseline / smooth wheel D2 flats only",
      "position_summary": "相手依存が最も強い位置です。先に開くときはボタンのレンジを土台にし、相手のビッグブラインドが弱いほど追加していきます。",
      "caution_note": "固定のパーセンテージとして扱わず、強いBB相手はボタン基準、弱いBB相手だけ追加という順で見るのが安全です。",
      "overview": {
        "seat_trigger": "blind war なので open と defend の両方が opponent model に大きく引っ張られます。",
        "open_identity": "first-in は BTN shell を起点にします。",
        "adds_here": "BB が弱い / over-fold なら 24, 34, A5, 25, 35, 45 を段階的に追加します。",
        "still_avoid": "rough wheel D2 flat、face-up cold-call、blind-vs-blind だからというだけの junk widen は残しません。"
      },
      "at_a_glance": {
        "open_core": "BTN shell vs strong BB",
        "position_add": "24 / 34 / A5 first, then 25 / 35 / 45 only in the softest blind wars",
        "vs_open": "mostly 3-bet or fold; smoothest wheel D2 flat only vs BTN steal",
        "snap_fold": "43 / 42 / rough D2 flats / generic blind junk"
      },
      "open_section": {
        "section_label": "オープンレンジ",
        "anchor_profile": "dynamic / button baseline plus exploit adds",
        "public_range_read": "Small blind first-in is not one fixed chart. The exact public rule is: use the button range versus strong BB, then add 24 / 34 / A5 / 25 / 35 / 45 as the BB weakens or over-folds.",
        "table_columns": [
          "区分",
          "ハンドレンジ"
        ],
        "table_rows": [
          [
            "基本",
            "強いビッグブラインド相手はボタンのオープンレンジをそのまま使う"
          ],
          [
            "追加する手",
            "まず 24・34・A5。さらに弱い相手には 25・35・45 まで"
          ],
          [
            "基本的に外す手",
            "上の追加リストを超える雑なブラインド戦レンジ"
          ]
        ],
        "range_groups": [
          {
            "label": "Strong-BB Base",
            "tone": "attack",
            "items": [
              "full BTN shell"
            ]
          },
          {
            "label": "Exploit Adds",
            "tone": "conditional",
            "items": [
              "24",
              "34",
              "A5",
              "25",
              "35",
              "45"
            ]
          },
          {
            "label": "Do Not Auto-Open",
            "tone": "fold",
            "items": [
              "wider D2 junk",
              "rough blind-war trash"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Start from button",
            "tone": "attack",
            "range_read": "Against strong or aggressive BB, just use the button opening shell.",
            "when": "SB first-in vs competent BB",
            "examples": "all badugis / 9-tri+ / A2-A4 core"
          },
          {
            "label": "Exploit add-on list",
            "tone": "conditional",
            "range_read": "Only widen through the published add-on list as the BB becomes softer.",
            "when": "BB over-folds or plays too straightforwardly",
            "examples": "24 / 34 / A5 / 25 / 35 / 45"
          },
          {
            "label": "No fake fixed %",
            "tone": "fold",
            "range_read": "Do not pretend SB has one exact first-in row across all BB types.",
            "when": "baseline UI read",
            "examples": "blind-war trash outside the add-on list"
          }
        ],
        "source_note": "This row is intentionally dynamic. CountingOuts gives the explicit add-on list, while Danzer and the older PDF only support the general idea that blind seats can widen.",
        "collected_rows": [
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "explicit_rule",
            "range_read": "Against tough players use the button opening range; against softer competition add 24, 34, A5, 25, 35, and 45.",
            "notes": "exact public SB open rule"
          },
          {
            "source_ref": "danzer_interview",
            "evidence_type": "rule_of_thumb",
            "range_read": "Blinds can widen to two cards five or lower and one-card draws to a six or seven.",
            "notes": "broad blind support"
          },
          {
            "source_ref": "pdf_badugi_guide",
            "evidence_type": "supplemental_pdf",
            "range_read": "Late position and blind seats can widen toward 3 cards under an 8 and 2 cards under a 5.",
            "notes": "older shorthand PDF"
          }
        ]
      },
      "versus_section": {
        "section_label": "Facing an Open / Blind Defense",
        "anchor_profile": "3-bet-or-fold baseline / smooth wheel flats only vs BTN",
        "public_range_read": "SB is the most context-heavy continue seat. The public overlap is 3-bet or fold except for the smoothest wheel-card two-card draws versus a button steal. Ohel trims the flat-call bucket to only the smoother half of wheel D2, while CountingOuts Part 4 widens the aggressive branch against a very loose button.",
        "table_columns": [
          "Band",
          "Hand classes",
          "How to use"
        ],
        "table_rows": [
          [
            "Versus EP-HJ-CO open",
            "Mostly 3-bet or fold; J+ badugi and A36+ as the tight floor",
            "Danzer close-call exception only"
          ],
          [
            "Versus BTN steal",
            "Flat only the smoothest wheel D2; 3-bet any badugi, A37+, A2, and A3 versus very loose BTN",
            "Ohel + CountingOuts Part 4"
          ],
          [
            "Default folds",
            "43 / 42-type rough D2; most face-up cold-calls",
            "SB flats stay narrow"
          ]
        ],
        "range_groups": [
          {
            "label": "3-Bet Core",
            "tone": "attack",
            "items": [
              "J+ badugi",
              "A36+",
              "Q+ badugi vs CO or loose opener",
              "A37+ vs CO or loose opener"
            ]
          },
          {
            "label": "BTN-Steal Flat Only",
            "tone": "conditional",
            "items": [
              "A2",
              "A3",
              "23",
              "A4",
              "smoothest wheel D2 only"
            ]
          },
          {
            "label": "Skip",
            "tone": "fold",
            "items": [
              "43",
              "42",
              "rough D2",
              "most non-BB cold-calls"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Mostly 3-bet or fold",
            "tone": "attack",
            "range_read": "Against normal opens, SB should not turn into a cold-call seat. Start from the tight Part 4 floor and widen only in late or loose branches.",
            "when": "SB facing EP-HJ-CO open",
            "examples": "J+ badugi / A36+ / Q+ badugi vs CO"
          },
          {
            "label": "Wheel-card flat bucket only",
            "tone": "conditional",
            "range_read": "Versus a button steal, keep flat-calls to the smoother half of wheel-card D2. Rough 43 and 42 are out.",
            "when": "SB vs BTN open",
            "examples": "A2 / A3 / 23 / A4"
          },
          {
            "label": "Exploit the very loose button aggressively",
            "tone": "attack",
            "range_read": "Against a very loose BTN, the aggressive branch widens to any badugi plus A37+, A2, and A3.",
            "when": "BTN opens extremely wide",
            "examples": "any pat / A37+ / A2 / A3"
          }
        ],
        "source_note": "The SB continue row is where Ohel and CountingOuts complement each other best: Ohel defines the flat bucket, while Part 4 defines the aggressive re-raise widen versus very loose steals.",
        "collected_rows": [
          {
            "source_ref": "ohel_fundamentals",
            "evidence_type": "direct_text",
            "range_read": "The small blind should have only the smoother portion of the wheel-card two-card draws; not 43 or 42.",
            "notes": "SB flat bucket"
          },
          {
            "source_ref": "countingouts_p4",
            "evidence_type": "direct_text",
            "range_read": "Against a very loose button opener, a small blind three-betting range could be any badugi, A37+, A2, and A3.",
            "notes": "aggressive steal response"
          },
          {
            "source_ref": "countingouts_p3",
            "evidence_type": "direct_text",
            "range_read": "Outside the big blind, continue hands should almost always be re-raised rather than cold-called.",
            "notes": "non-BB discipline"
          },
          {
            "source_ref": "danzer_interview",
            "evidence_type": "rule_of_thumb",
            "range_read": "If it is very close, calling can be fine.",
            "notes": "narrow supporting exception"
          }
        ]
      },
      "source_refs": [
        "countingouts_p3",
        "countingouts_p4",
        "ohel_fundamentals",
        "danzer_interview",
        "pdf_badugi_guide"
      ]
    },
    "BB": {
      "label": "ビッグブラインド",
      "role_label": "defense-only seat",
      "open_band": "",
      "versus_open_band": "スムーズなホイール2枚 / 一部の5スタート2枚 / 利益の出る3枚",
      "position_summary": "このゲームで最も広くコールを残せる位置です。アクションを閉じられるので、ここだけは明確なコールレンジがあります。",
      "caution_note": "それでもアーリーポジションのオープンにコールが入った場面ではかなり締めます。価格が良いからといって何でも残すわけではありません。",
      "overview": {
        "seat_trigger": "closing action と price の良さが BB defense の土台です。",
        "open_identity": "公開 first-in open row はありません。BB は defense-only として表示します。",
        "adds_here": "smooth wheel D2、some two-card fives、763 / 256 / A35-type tri examples が入ります。",
        "still_avoid": "rough D2 versus early open + call、bad blockers、junk tri は残しません。"
      },
      "at_a_glance": {
        "open_core": "no fixed BB first-in open row",
        "position_add": "closing action lets BB keep the widest flat bucket",
        "vs_open": "smooth wheel D2 / some 5-high D2 / profitable tri / value 3-bets with badugi and premium tri",
        "snap_fold": "rough D2 vs EP+call / bad blockers / junk tri"
      },
      "open_section": null,
      "versus_section": {
        "section_label": "コールレンジ",
        "anchor_profile": "widest continue seat / closing action matters",
        "public_range_read": "BB is where public badugi material actually allows flats. Ohel gives the core as smooth wheel D2 plus some two-card fives because BB closes the action. CountingOuts adds specific profitable tri defenses such as 763, 256, and A35-type holdings in the right price and induce spots.",
        "table_columns": [
          "区分",
          "ハンドレンジ"
        ],
        "table_rows": [
          [
            "CO・BTNのオープンにコール",
            "スムーズなホイール2枚ドロー / 一部の5スタート2枚ドロー / 利益の出る3枚ハンド"
          ],
          [
            "レイズにコールが付いた場面",
            "256型の2枚ドローや良い3枚はオッズが付けば残す"
          ],
          [
            "EPのオープンにコールが付いた場面",
            "かなり締める。ラフな2枚ドローは外す"
          ]
        ],
        "range_groups": [
          {
            "label": "Flat-Call Core",
            "tone": "attack",
            "items": [
              "A2",
              "A3",
              "23",
              "A4",
              "smooth 24",
              "some two-card 5s",
              "763",
              "256"
            ]
          },
          {
            "label": "Raise or Trap Upgrade",
            "tone": "conditional",
            "items": [
              "any badugi vs very loose BTN",
              "A37+",
              "A2",
              "A3",
              "A35 induce line"
            ]
          },
          {
            "label": "Respect Early Strength",
            "tone": "fold",
            "items": [
              "rough 5-high D2",
              "bad blockers",
              "D2 vs EP open + call",
              "junk tri"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "Defend wide only when closing action",
            "tone": "attack",
            "range_read": "BB is allowed to keep smooth wheel D2, some two-card fives, and profitable tri because it closes the action and gets the best price.",
            "when": "BB vs CO-BTN open",
            "examples": "A2 / A3 / 23 / A4 / smooth 24 / 763"
          },
          {
            "label": "Use overlay in multi-way late spots",
            "tone": "conditional",
            "range_read": "When late opens and calls create extra overlay, 256-type holdings can continue more often than they could heads-up against early strength.",
            "when": "CO raise + BTN call / similar late multi-way spots",
            "examples": "256"
          },
          {
            "label": "Tighten sharply versus early strength",
            "tone": "fold",
            "range_read": "Haney's main muck spot is specifically EP open plus another call. Rough D2 should leave the range there.",
            "when": "EP open + call",
            "examples": "rough A2 / rough 5-high D2"
          },
          {
            "label": "Exploit loose steals aggressively",
            "tone": "attack",
            "range_read": "Against very loose button steals, BB can raise any badugi and the premium tri branch; some strong five-tri like A35 can also flat to induce snowing.",
            "when": "BB vs very loose BTN",
            "examples": "any badugi / A37+ / A35"
          }
        ],
        "source_note": "BB is the only seat where the public record clearly keeps a real flat-call bucket. The examples matter here because they show exactly what kinds of tri and D2 holdings survive when price and position justify it.",
        "collected_rows": [
          {
            "source_ref": "ohel_fundamentals",
            "evidence_type": "direct_text",
            "range_read": "The big blind will have some two-card fives because he is closing the action and getting a better price.",
            "notes": "BB widens beyond SB"
          },
          {
            "source_ref": "countingouts_p1",
            "evidence_type": "example_hand",
            "range_read": "The big blind defends 763 versus a button open because the button has plenty of inferior hands and BB gets good pot odds.",
            "notes": "explicit tri defense example"
          },
          {
            "source_ref": "countingouts_p5",
            "evidence_type": "example_hand",
            "range_read": "BB can defend 256 versus a cutoff raise and a button call because the overlay and implied odds are too good to fold.",
            "notes": "late multi-way overlay example"
          },
          {
            "source_ref": "countingouts_p6",
            "evidence_type": "example_hand",
            "range_read": "Against opponents who love to snow, BB may just call with a strong hand like A35 to induce bluffs from a button opener.",
            "notes": "trap-call / induce branch"
          },
          {
            "source_ref": "haney_two_card",
            "evidence_type": "direct_text",
            "range_read": "Two-card draws belong mainly to late opens or when defending the big blind, but should usually be mucked against an early open followed by another call.",
            "notes": "main BB D2 filter"
          },
          {
            "source_ref": "countingouts_p4",
            "evidence_type": "direct_text",
            "range_read": "Against a very loose button opener, any badugi, A37+, A2, and A3 can enter the aggressive three-bet branch.",
            "notes": "loose-steal attack branch"
          }
        ]
      },
      "source_refs": [
        "countingouts_p1",
        "countingouts_p4",
        "countingouts_p5",
        "countingouts_p6",
        "haney_two_card",
        "ohel_fundamentals"
      ]
    }
  },
  "source_index": {
    "countingouts_p1": {
      "short_label": "CountingOuts P1",
      "title": "Mastering Badugi Part 1 – Introduction",
      "weight": "secondary_html",
      "source_type": "HTML",
      "url": "https://www.countingouts.com/mastering-badugi-part-1-introduction/"
    },
    "countingouts_p3": {
      "short_label": "CountingOuts P3",
      "title": "Mastering Badugi Part 3 – Strategy before the First Draw",
      "weight": "primary_html",
      "source_type": "HTML",
      "url": "https://www.countingouts.com/mastering-badugi-part-3-strategy-before-the-first-draw/"
    },
    "countingouts_p4": {
      "short_label": "CountingOuts P4",
      "title": "Mastering Badugi Part 4 – Three Betting Ranges",
      "weight": "primary_html",
      "source_type": "HTML",
      "url": "https://www.countingouts.com/mastering-badugi-part-4-three-betting-ranges/"
    },
    "countingouts_p5": {
      "short_label": "CountingOuts P5",
      "title": "Mastering Badugi Part 5 – Middle Rounds (ABC Play)",
      "weight": "supporting_html",
      "source_type": "HTML",
      "url": "https://www.countingouts.com/mastering-badugi-part-5-middle-rounds-abc-play/"
    },
    "countingouts_p6": {
      "short_label": "CountingOuts P6",
      "title": "Mastering Badugi Part 6 – Middle Rounds (Making Moves)",
      "weight": "supporting_html",
      "source_type": "HTML",
      "url": "https://www.countingouts.com/mastering-badugi-part-6-middle-rounds-making-moves/"
    },
    "haney_opening": {
      "short_label": "Haney Opening",
      "title": "Badugi: Opening Standards",
      "weight": "primary_html",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66443-seth-davies-33-18/articles/24061-badugi-opening-standards"
    },
    "haney_opening_pdf": {
      "short_label": "Haney Opening PDF",
      "title": "Card Player Vol. 33 No. 18 PDF – Badugi: Opening Standards",
      "weight": "primary_pdf",
      "source_type": "PDF",
      "url": "https://media.cardplayer.com/assets/magazines/000/066/443/pdf/33_18_web.pdf"
    },
    "haney_three_card": {
      "short_label": "Haney Tri Article",
      "title": "Badugi: Three-Card Badugis",
      "weight": "primary_html",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66435-global-poker-33-10/articles/23985-badugi-three-card-badugis"
    },
    "haney_two_card": {
      "short_label": "Haney D2 Article",
      "title": "Badugi: A Discussion On Two-Card Draws",
      "weight": "primary_html",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66437-timothy-adams-33-13/articles/24002-badugi-a-discussion-on-two-card-draws"
    },
    "ohel_fundamentals": {
      "short_label": "Randy Ohel",
      "title": "Poker Strategy Badugi Fundamentals With Randy Ohel",
      "weight": "secondary_html",
      "source_type": "HTML",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66432-poker-bot-expert-steve-blay-33-7/articles/23944-poker-strategy-badugi-fundamentals-with-randy-ohel"
    },
    "danzer_interview": {
      "short_label": "George Danzer",
      "title": "George Danzer Discusses Betting and Bluffing in Badugi",
      "weight": "secondary_html",
      "source_type": "HTML",
      "url": "https://www.pokernews.com/strategy/george-danzer-discusses-betting-and-bluffing-in-badugi-22109.htm"
    },
    "pdf_badugi_guide": {
      "short_label": "Ryan Eccles PDF",
      "title": "Badugi Poker: Rules and Strategies Guide",
      "weight": "supplemental_pdf",
      "source_type": "PDF",
      "url": "https://www.scribd.com/document/18032831/Badugi-Poker-The-Definitive-Guide"
    }
  }
};

window.__A5_TRIPLE_DRAW_PUBLIC_RANGES_V1 = {
  "dataset_id": "a5_triple_draw_pre_draw_public_ranges_v2",
  "version": 2,
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
    "position_button_meaning": "6-max / shorthanded public-chart seats: EP (UTG-HJ), Cutoff, Button, Small Blind, and Big Blind",
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
    "excluded_reason": "public A-5 Triple Draw material does not publish a fixed big-blind first-in open row; BB remains a defense-only seat",
    "reconstruction_method": "公開 HTML / PDF を確認し、solver 風の fake mix ではなく、position ごとの open / continue に再分解した public-source dataset"
  },
  "strength_primer": {
    "best_hand": "A-2-3-4-5",
    "ranking_rule": "lowest five-card hand wins; aces play low and pairs are always bad",
    "straight_flush_rule": "straights and flushes do not count against the low",
    "normalization_rule": "because suits do not change low-hand value in A-5, the dataset is stored as rank-structure buckets such as A23, four wheel cards, and three to a six rather than suit-specific combos"
  },
  "collection_notes": [
    "2026-04-18 に CountingOuts / CardPlayer / BetMGM / WPT / JOPT のリンク先と PDF を再確認し、A-5 をポジション別レンジへ組み直しました。",
    "Open の定量アンカーは CountingOuts の detailed predraw article を正本とし、EP 26.7% / CO 31.7% / BTN 42.7% を採用しています。",
    "BetMGM は 26% / 31% / 42% の概数クロスチェックとして使い、境界 hand の具体例は Kevin Haney の CardPlayer 記事で補っています。",
    "CountingOuts の basic article は early open を made sixes or better と丸めていますが、詳細記事の made 7s or better / 26.7% を優先しています。",
    "SB と BB は exact open % / call % が公開されていないため、UI は raise-or-fold baseline や defend floor をそのまま表示し、作り物の混合頻度は出していません。",
    "A-5 はスートが low の価値を変えないため、UI は suited combo の羅列ではなく、draw count と quality band でレンジを読ませる構造にしています。"
  ],
  "global_source_refs": [
    "countingouts_basic",
    "wpt_rules",
    "jopt_mix_td_pdf"
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
      "seat_band": [
        "short_handed_first_seat",
        "first_in_no_steal"
      ],
      "position_summary": "6-max相当の最初の席。A-5は2-7より少し広く開けますが、最下層の3枚6ローや2カード開始はまだ待つ位置です。",
      "caution_note": "公開ソースが最も強く警告しているのは、EPから粗い3枚6ローを入れ過ぎて multiway の reverse implied odds を背負うことです。",
      "overview": {
        "seat_trigger": "最初の席で、まだ steal ではなく後ろに複数人が残っています。",
        "open_identity": "Made 7s+、four wheel cards、four to a six、three wheel cards が土台です。",
        "adds_here": "EPで追加される3枚6ローは A26 / A36 / A46 / 236 / 246 / 346 の whitelist までです。",
        "still_avoid": "356 / 456 のような粗い3枚6ローと、A2 / A3 / A4 / 23 / 24 / 34 の2カード steal 帯はまだ待ちます。"
      },
      "at_a_glance": {
        "open_core": "26.7% / Made 7s+ + Four Wheel + Four to a Six + Three Wheel + 強い3枚6ロー。",
        "position_add": "この位置では 3枚6ローを全面採用せず、強い subset だけに止めます。",
        "vs_complete": "Pat hand / 1枚ドローは 3ベット中心。A23 / A24 / A34 は premium 2枚ドローとして再加圧候補です。",
        "snap_fold": "345 のような下端は、既に raise が入った pot では一気に苦しくなります。"
      },
      "open_complete": {
        "section_label": "First-In Open",
        "anchor_profile": "EP 26.7% / CountingOuts explicit chart",
        "public_range_read": "EP は Made 7s or better、four wheel cards、four to a six、three wheel cards、そして A26-A46 / 236 / 246 / 346 まで。必要ない説明文ではなく、ここをそのまま open shell に落としています。",
        "range_groups": [
          {
            "label": "EPで残す中核",
            "tone": "attack",
            "items": [
              "Made 7s or better",
              "Four wheel cards",
              "Four to a six",
              "Three wheel cards"
            ]
          },
          {
            "label": "EPでだけ許す3枚6ロー",
            "tone": "conditional",
            "items": [
              "A26",
              "A36",
              "A46",
              "236",
              "246",
              "346"
            ]
          },
          {
            "label": "まだ開かない帯",
            "tone": "fold",
            "items": [
              "356",
              "456",
              "A2",
              "A3",
              "A4",
              "23",
              "24",
              "34"
            ]
          }
        ],
        "table_columns": [
          "帯",
          "代表 hand / class",
          "扱い / 根拠"
        ],
        "table_rows": [
          [
            "Pat made",
            "Made 7s or better",
            "0.8% / EP から常時オープン。rough 7 は multiway では break 候補"
          ],
          [
            "1枚ドロー",
            "Four wheel cards",
            "1.9% / 最上位の1枚ドロー。対オープンでも再加圧帯"
          ],
          [
            "1枚ドロー",
            "Four to a six",
            "3.7% / 2456・3456 の rough 側は multiway で注意"
          ],
          [
            "2枚ドロー",
            "Three wheel cards (A23〜345)",
            "12.7% / EP の主力"
          ],
          [
            "3枚6ローの whitelist",
            "A26 / A36 / A46 / 236 / 246 / 346",
            "7.6% / EPではここまで。356・456 は cut"
          ]
        ],
        "source_note": "CountingOuts の detailed chart が EP 26.7% を明示し、Haney は UTG の底を 345 / A46 付近と補足します。BetMGM は 26% の概数 cross-check ですが、pat threshold を made 6 or better と丸めているため detailed article を優先します。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "explicit_chart",
            "range_read": "EP 26.7% = Made 7s+ / Four Wheel Cards / Four to a Six / Three Wheel Cards / A26-A46,236,246,346",
            "notes": "Open total と class breakdown の主ソース。"
          },
          {
            "source_ref": "cardplayer_predraw",
            "evidence_type": "boundary_example",
            "range_read": "UTG での最下層 open 例は 345 と A46 付近",
            "notes": "厳密科学ではないが、下端確認には有用。"
          },
          {
            "source_ref": "betmgm_basic",
            "evidence_type": "cross_check",
            "range_read": "UTG-HJ は約 26% で、3-4 wheel cards / four to a six / A26-A46 / 236 / 246 / 346 を含む",
            "notes": "概数の照合。pat made の表現は simplified。"
          }
        ]
      },
      "versus_complete": {
        "section_label": "Vs Open Continue",
        "anchor_profile": "exact call % unpublished / class guidance only",
        "public_range_read": "公開ソースはコール頻度を数値で出していません。ここでは 3ベット帯 / コール帯 / すぐ落ちる帯に分け、fake mixed frequency を作らずに残します。",
        "table_columns": [
          "アクション",
          "レンジ",
          "補足"
        ],
        "table_rows": [
          [
            "3ベット",
            "Pat hands / one-card draws / A23 / A24 / A34",
            "情報を隠しつつ equity を押し付ける"
          ],
          [
            "コール",
            "A23 mix / A36-type weaker two-card draws",
            "exact % は未公開。cold-call が自然な帯"
          ],
          [
            "フォールド寄り",
            "345 など EP 下端の rough 2枚ドロー",
            "pot が既に raise 済みなら価値が大きく下がる"
          ]
        ],
        "action_bands": [
          {
            "label": "3ベット中心",
            "tone": "attack",
            "range_read": "Pat hand と全 1枚ドローは基本的に再加圧。premium 2枚ドロー A23 / A24 / A34 も value 3ベット帯です。",
            "when": "single open に直面した時の基本線。",
            "examples": "pat 7+, four wheel, four to a six, A23"
          },
          {
            "label": "コールに回る帯",
            "tone": "conditional",
            "range_read": "A23 の一部や A36 型の弱め 2枚ドローは cold-call で十分です。",
            "when": "blind を残したい時、または initiative の価値が相対的に小さい 2枚ドロー。",
            "examples": "A23 mix / A36"
          },
          {
            "label": "既レイズ pot で削る帯",
            "tone": "fold",
            "range_read": "EP の下端に近い 345 などは、誰かが先に raise しているだけでかなり厳しくなります。",
            "when": "早い位置の open に向かう時や multiway 気味の時。",
            "examples": "345 / fringe 346 without strong blockers"
          }
        ],
        "source_note": "CountingOuts は pat / 1枚ドローの reraise と premium 2枚ドローの再加圧を明示し、Haney は raised pot では 345 のような境界 hand を締めるべきと補います。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "reraise_rule",
            "range_read": "Against an open, re-raise any pat hand or one-card draw; premium two-card draws such as A23 / A24 / A34 can also be reraises",
            "notes": "A23 は A2 に対して大きな equity edge がある。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "cold_call_rule",
            "range_read": "A23 can sometimes cold-call; weaker two-card draws such as A36 can cold-call instead of 3-betting",
            "notes": "exact call % は公開されていない。"
          },
          {
            "source_ref": "cardplayer_predraw",
            "evidence_type": "raised_pot_trim",
            "range_read": "An early-position open should push mediocre hands such as 345 toward folds",
            "notes": "Raised pot では底の手から消える。"
          }
        ]
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw",
        "betmgm_basic"
      ]
    },
    "CO": {
      "label": "Cutoff",
      "seat_band": [
        "late_position_cutoff"
      ],
      "position_summary": "CO は EP の殻を残したまま、3枚6ローを全面採用し始める席です。",
      "caution_note": "公開ソースは、button と blinds が loose なら 356 / 456 のような下端を削ってもほぼ損をしない、と明示しています。",
      "overview": {
        "seat_trigger": "後ろは Button と blinds だけ。steal の圧力が少し乗る位置です。",
        "open_identity": "EP の core はそのまま残り、3枚6ローが full bucket へ広がります。",
        "adds_here": "A26-A46 / 236 / 246 / 346 の whitelist を、CO では three to a six 全体へ広げます。",
        "still_avoid": "A2 / A3 / A4 / 23 / 24 / 34 の 2カード steal はまだ baseline ではなく、button 以降や exploit add の領域です。"
      },
      "at_a_glance": {
        "open_core": "31.7% / EP shell + three to a six full bucket。",
        "position_add": "この席での主な widen は 3枚6ローの全面採用で、2カード steal はまだ既定値に入れません。",
        "vs_complete": "Pat / 1枚ドローは引き続き 3ベット寄り。2枚ドローは premium と weaker を分けて扱います。",
        "snap_fold": "Loose button / blinds が残るなら 356 / 456 のような fringe は先に切ります。"
      },
      "open_complete": {
        "section_label": "First-In Open",
        "anchor_profile": "CO 31.7% / CountingOuts explicit chart",
        "public_range_read": "CO は EP shell を維持しつつ、three to a six を full bucket で追加する席です。ここで必要なのは「COで新しく入る hand class」を見える形にすることです。",
        "range_groups": [
          {
            "label": "EPから持ち越す核",
            "tone": "attack",
            "items": [
              "Made 7s or better",
              "Four wheel cards",
              "Four to a six",
              "Three wheel cards"
            ]
          },
          {
            "label": "COで広がる帯",
            "tone": "conditional",
            "items": [
              "Three to a six",
              "356",
              "456"
            ]
          },
          {
            "label": "まだ baseline 外",
            "tone": "fold",
            "items": [
              "A2",
              "A3",
              "A4",
              "23",
              "24",
              "34"
            ]
          }
        ],
        "table_columns": [
          "帯",
          "代表 hand / class",
          "扱い / 根拠"
        ],
        "table_rows": [
          [
            "持ち越し",
            "EP shell",
            "Made 7s+ / Four Wheel / Four to a Six / Three Wheel はそのまま残る"
          ],
          [
            "CO add",
            "Three to a six",
            "EP の whitelist ではなく full bucket を採用し、31.7% へ"
          ],
          [
            "下端のトリム",
            "356 / 456",
            "Button と blinds が loose なら cut してよい fringe"
          ],
          [
            "Exploit add only",
            "A2 / A3 / 23",
            "後ろが tight / weak なら widen 候補だが baseline の既定値ではない"
          ]
        ],
        "source_note": "CountingOuts は CO で three to a six を full bucket にすることを明示し、Haney は 356 / A47 を practical floor としています。BetMGM も 31% と同方向です。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "explicit_chart",
            "range_read": "CO 31.7% = Made 7s+ / Four Wheel Cards / Four to a Six / Three Wheel Cards / Three to a Six",
            "notes": "CO total と class add の主ソース。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "fringe_trim",
            "range_read": "If button and blinds are very loose you probably do not lose much by eliminating 356 and 456",
            "notes": "CO fringe の cut line。"
          },
          {
            "source_ref": "cardplayer_predraw",
            "evidence_type": "boundary_example",
            "range_read": "Cutoff floor examples are around 356 and A47",
            "notes": "実戦境界の補足。"
          }
        ]
      },
      "versus_complete": {
        "section_label": "Vs Open Continue",
        "anchor_profile": "in-position class split / no exact cold-call %",
        "public_range_read": "CO facing open でも public guidance は class ベースです。in-position の利点はありますが、pat / 1枚ドローを flat に寄せる理由は薄く、2枚ドローだけを premium と fringe に分けます。",
        "table_columns": [
          "アクション",
          "レンジ",
          "補足"
        ],
        "table_rows": [
          [
            "3ベット",
            "Pat hands / one-card draws / A23 / A24 / A34",
            "initiative と情報隠しの価値が高い"
          ],
          [
            "コール",
            "A23 mix / A36-type weaker two-card draws",
            "弱い 2枚ドローは flat に回してよい"
          ],
          [
            "フォールド寄り",
            "356 / 456 など CO fringe",
            "pot が raise 済みなら最初に落ちる帯"
          ]
        ],
        "action_bands": [
          {
            "label": "攻める継続帯",
            "tone": "attack",
            "range_read": "Pat hand と 1枚ドローは引き続き 3ベット中心。premium 2枚ドローも先に圧を掛けます。",
            "when": "EP / CO open に single-raised pot で向かう時。",
            "examples": "pat 7+, four wheel, four to a six, A23-A34"
          },
          {
            "label": "コールに回す帯",
            "tone": "conditional",
            "range_read": "A36 型の weaker 2枚ドローは in position で cold-call が自然です。",
            "when": "initiative より realization を取りたい時。",
            "examples": "A36 / mixed A23"
          },
          {
            "label": "raised pot で先に消える帯",
            "tone": "fold",
            "range_read": "CO の fringe open 候補は、相手が既に open しているだけで価値がかなり下がります。",
            "when": "tight early open や loose callers が残る時。",
            "examples": "356 / 456 / thin 3-card six tail"
          }
        ],
        "source_note": "CO専用の call % 表はありません。したがって UI は action class を position-aware に言い換えるだけに止めています。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "reraise_rule",
            "range_read": "Re-raise any pat hand or one-card draw; premium two-card draws can also be reraises",
            "notes": "CO でも class split の骨格は同じ。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "cold_call_rule",
            "range_read": "A23 may cold-call sometimes; weaker two-card draws such as A36 can cold-call",
            "notes": "公開された数値 mix はない。"
          },
          {
            "source_ref": "cardplayer_predraw",
            "evidence_type": "boundary_example",
            "range_read": "Cutoff floor examples are around 356 and A47",
            "notes": "fringe が既レイズ pot で後退する根拠に使う。"
          }
        ]
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw",
        "betmgm_basic"
      ]
    },
    "BTN": {
      "label": "Button",
      "seat_band": [
        "button",
        "steal_position"
      ],
      "position_summary": "Button は公開 chart で 2カード steal 帯がはっきり追加される最初の席です。",
      "caution_note": "Button で draw three をやり過ぎると顔が割れやすく、いちばん弱い steal は defend を受けた瞬間にすぐ消えます。",
      "overview": {
        "seat_trigger": "残りは blinds のみ。steal と realization の両方が最大化される席です。",
        "open_identity": "CO shell に A2 / A3 / A4 / 23 / 24 / 34 の 2カード wheel-start steal を足します。",
        "adds_here": "公開 chart の新規追加は A2 through 34 の 10.9%。Haney の practical floor は 456 / A57 / 357 まで伸びます。",
        "still_avoid": "A5 / 25 / 35 / 45 のような blind-vs-blind defense class は、公開 BTN first-in baseline にはまだ入りません。"
      },
      "at_a_glance": {
        "open_core": "42.7% / CO shell + A2 through 34。",
        "position_add": "Button で明確に増えるのは 2カード steal layer。公開ソースの境界例は 456 / A57 / 357 です。",
        "vs_complete": "In position でも pat / 1枚ドローは 3ベット中心。2枚ドローだけを flat 候補へ回します。",
        "snap_fold": "最弱の button steals は defend / reraise を受けると最初に消えます。"
      },
      "open_complete": {
        "section_label": "First-In Open",
        "anchor_profile": "BTN 42.7% / CountingOuts explicit chart",
        "public_range_read": "Button は CO shell を丸ごと持ち込み、A2 / A3 / A4 / 23 / 24 / 34 を追加する席です。ここでは「Button で何が新しく入るか」を一目で読めるようにしています。",
        "range_groups": [
          {
            "label": "COから持ち越す shell",
            "tone": "attack",
            "items": [
              "Made 7s or better",
              "Four wheel cards",
              "Four to a six",
              "Three wheel cards",
              "Three to a six"
            ]
          },
          {
            "label": "Buttonで新しく入る 2カード帯",
            "tone": "attack",
            "items": [
              "A2",
              "A3",
              "A4",
              "23",
              "24",
              "34"
            ]
          },
          {
            "label": "公開 baseline 外",
            "tone": "fold",
            "items": [
              "A5",
              "25",
              "35",
              "45"
            ]
          }
        ],
        "table_columns": [
          "帯",
          "代表 hand / class",
          "扱い / 根拠"
        ],
        "table_rows": [
          [
            "持ち越し",
            "CO shell",
            "31.7% の CO shell はすべて残る"
          ],
          [
            "BTN add",
            "A2 / A3 / A4 / 23 / 24 / 34",
            "10.9% の 2カード steal layer が加わり 42.7% へ"
          ],
          [
            "Practical floor",
            "456 / A57 / 357",
            "Haney の button 下端例。exact frequency ではない"
          ],
          [
            "公開 baseline 外",
            "A5 / 25 / 35 / 45",
            "BB vs SB defense で出る class。BTN first-in の既定値ではない"
          ]
        ],
        "source_note": "CountingOuts の 42.7% と A2 through 34 が Button の主アンカーです。BetMGM は 42% とほぼ一致し、Haney は 456 / A57 / 357 を bottom examples として補います。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "explicit_chart",
            "range_read": "BTN 42.7% = CO shell + A2 through 34 (10.9%)",
            "notes": "Button open total と exact add の主ソース。"
          },
          {
            "source_ref": "cardplayer_predraw",
            "evidence_type": "boundary_example",
            "range_read": "Button floor examples include 456, A57, 357, plus low two-card draws such as A2 / A3 / 23 / A4",
            "notes": "practical edge の補足。"
          },
          {
            "source_ref": "betmgm_basic",
            "evidence_type": "cross_check",
            "range_read": "Button opens about 42% by adding A-2-3-4 to the cutoff range",
            "notes": "概数の照合。"
          }
        ]
      },
      "versus_complete": {
        "section_label": "Vs Open Continue",
        "anchor_profile": "best realization seat / still no exact call %",
        "public_range_read": "Button は realization が最も良い席ですが、公開ソースが推す骨格は変わりません。pat / 1枚ドローは 3ベット、2枚ドローは premium と weaker で分けます。",
        "table_columns": [
          "アクション",
          "レンジ",
          "補足"
        ],
        "table_rows": [
          [
            "3ベット",
            "Pat hands / one-card draws / A23 / A24 / A34",
            "情報を与えず、heads-up 化しやすい"
          ],
          [
            "コール",
            "A36-type weaker two-card draws / mixed A23",
            "in position での realize が良い"
          ],
          [
            "フォールド寄り",
            "Weakest button steals",
            "先に raise が入ると真っ先に落ちる"
          ]
        ],
        "action_bands": [
          {
            "label": "前に出る継続帯",
            "tone": "attack",
            "range_read": "Pat hand と 1枚ドローは Button でも flat より 3ベットが主体です。",
            "when": "EP / CO open に向かう時。",
            "examples": "pat 7+, four wheel, four to a six, A23-A34"
          },
          {
            "label": "位置を生かすコール帯",
            "tone": "conditional",
            "range_read": "A36 型の weaker 2枚ドローは Button なら cold-call がしやすいです。",
            "when": "wider open に対して raw equity と realization を両立したい時。",
            "examples": "A36 / mixed A23"
          },
          {
            "label": "最弱 steal は撤退",
            "tone": "fold",
            "range_read": "Button first-in では入る hand でも、既に raise が入っているなら残す理由が薄いものがあります。",
            "when": "strong early open や squeeze 気味の展開。",
            "examples": "456 / A57 / 357 の下端側"
          }
        ],
        "source_note": "Button は seat edge があるものの、public source は exact flat-call mix を出していません。したがって表示は class split を honest に保ったままです。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "reraise_rule",
            "range_read": "Any pat hand or one-card draw should usually be reraised; premium two-card draws can also be reraises",
            "notes": "Button でも骨格は同じ。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "button_note",
            "range_read": "Opening too many three-card draws on the button becomes face-up because everyone sees you raising and drawing three often",
            "notes": "弱い steal が既レイズ pot で消える理由。"
          },
          {
            "source_ref": "cardplayer_predraw",
            "evidence_type": "boundary_example",
            "range_read": "Button floor examples include 456 / A57 / 357",
            "notes": "exact mix ではない practical floor。"
          }
        ]
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw",
        "betmgm_basic"
      ]
    },
    "SB": {
      "label": "Small Blind",
      "seat_band": [
        "small_blind",
        "blind_vs_blind_pressure"
      ],
      "position_summary": "SB は固定 open % が公開されていない席で、相手 BB の守り方に応じて Button baseline から上下する dynamic seat です。",
      "caution_note": "この席でやってはいけないのは、公開ソースにない exact steal % を勝手に作ることです。baseline は Button range で止めます。",
      "overview": {
        "seat_trigger": "常に out of position で、相手は BB 1人だけです。",
        "open_identity": "強い BB 相手の baseline は Button range。その外側は exploit widen です。",
        "adds_here": "BB が over-fold かつ under-reraise なら、Button shell より少し広く open できます。",
        "still_avoid": "Thin rough draws を OOP で自動 open する固定 chart は、公開情報からは作れません。"
      },
      "at_a_glance": {
        "open_core": "dynamic / tough BB には Button range baseline。",
        "position_add": "widen は exploit only。exact add-on list は公開ソースにありません。",
        "vs_complete": "この席の継続は mostly raise-or-fold。call は loose late opener への A2 など narrow exception。",
        "snap_fold": "Tight EP open に対する A2 と、それより薄い 2カード draws。"
      },
      "open_complete": {
        "section_label": "First-In Open",
        "anchor_profile": "dynamic / use BTN range vs tough BB",
        "public_range_read": "SB の honest baseline は「強い BB 相手には Button range で open」です。そこから先は exploit widen であって、公開 source は exact extra classes を列挙していません。",
        "range_groups": [
          {
            "label": "公開 baseline",
            "tone": "attack",
            "items": [
              "Button range"
            ]
          },
          {
            "label": "相手依存 widen",
            "tone": "conditional",
            "items": [
              "Open wider only when BB folds too much",
              "Open wider only when BB does not reraise enough"
            ]
          },
          {
            "label": "自動で広げない帯",
            "tone": "fold",
            "items": [
              "Thin rough draws out of position",
              "Unpublished exact steal tails"
            ]
          }
        ],
        "table_columns": [
          "帯",
          "代表 hand / class",
          "扱い / 根拠"
        ],
        "table_rows": [
          [
            "Default shell",
            "Button range",
            "強い BB 相手の baseline"
          ],
          [
            "Exploit widen",
            "Button range より少し広く",
            "BB が over-fold / under-reraise の時だけ"
          ],
          [
            "Do not fake precision",
            "Exact extra classes unpublished",
            "公開ソースにない固定 steal % は作らない"
          ]
        ],
        "source_note": "CountingOuts は SB に exact % row を出しておらず、Button range baseline + exploit widen のルールだけを与えます。UI もそれに合わせて dynamic 表示にしています。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "blind_rule",
            "range_read": "Against a tough player, opening with your button range appears reasonable",
            "notes": "SB default baseline。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "exploit_rule",
            "range_read": "Against weaker players you can open wider if the BB folds too much and does not reraise often",
            "notes": "Public source does not enumerate an exact add-on list。"
          }
        ]
      },
      "versus_complete": {
        "section_label": "Vs Open Continue",
        "anchor_profile": "mostly raise-or-fold / rare A2 flat",
        "public_range_read": "SB は対 open の public guidance が最も明確です。worth playing ならまず 3ベットで BB を締め出し、flat-call は A2 のような narrow exploit に限ります。",
        "table_columns": [
          "アクション",
          "レンジ",
          "補足"
        ],
        "table_rows": [
          [
            "3ベット default",
            "Pat hands / one-card draws / best two-card draws",
            "Playするなら isolate が基本"
          ],
          [
            "Rare flat",
            "A2 vs loose late opener",
            "例外的な exploit call"
          ],
          [
            "Fold more",
            "A2 and thinner vs tight EP open",
            "A2 は 3456 に対して約 33%"
          ]
        ],
        "action_bands": [
          {
            "label": "3ベット or fold が基本",
            "tone": "attack",
            "range_read": "この席でプレイする hand は、まず re-raise して BB を締め出す方向です。",
            "when": "single open facing の標準線。",
            "examples": "pat hands / one-card draws / premium two-card draws"
          },
          {
            "label": "例外コール",
            "tone": "conditional",
            "range_read": "Loose aggressive late opener に対する A2 は flat-call 候補になります。",
            "when": "late open が wide で、3ベットよりコールの方が exploit になる時。",
            "examples": "A2 vs BTN / CO loose open"
          },
          {
            "label": "tight early open には締める",
            "tone": "fold",
            "range_read": "Tight EP open に対する A2 やそれ以下の薄い 2カード draw は fold 寄りです。",
            "when": "one-card draw にぶつかる割合が高い相手。",
            "examples": "A2 vs tight EP; thinner two-card starts"
          }
        ],
        "source_note": "CountingOuts は SB に対して raise-or-fold baseline と A2 flat の例外、そして A2 vs 3456 が約 33% しかない点まで示しています。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "sb_raise_or_fold",
            "range_read": "From the small blind you should mostly play a raise or fold strategy",
            "notes": "SB continue の骨格。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "sb_exception_call",
            "range_read": "You can call from the small blind with a hand like A2 against a loose aggressive late-position open",
            "notes": "例外的 flat-call の根拠。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "equity_warning",
            "range_read": "Against 3456 the A2 only has around 33% equity",
            "notes": "tight early open に対して A2 を締める理由。"
          },
          {
            "source_ref": "cardplayer_predraw",
            "evidence_type": "one_card_draw_rule",
            "range_read": "Any one-card draw you choose to play should be three-bet so you do not divulge information",
            "notes": "3567 from the small blind is a concrete reraising example。"
          }
        ]
      },
      "source_refs": [
        "countingouts_predraw",
        "cardplayer_predraw"
      ]
    },
    "BB": {
      "label": "Big Blind",
      "seat_band": [
        "big_blind",
        "defense_only_seat"
      ],
      "position_summary": "公開 A-5 material では BB は defense seat であり、fixed first-in open row はありません。",
      "caution_note": "この席に open % を付けると fake chart になります。BB は opener 別 defense line と blind-vs-blind widen だけを前に出します。",
      "overview": {
        "seat_trigger": "closing action と position edge はあるが、公開情報は defense に集中しています。",
        "open_identity": "No fixed BB first-in row. Main display is defend / rereraise guidance by opener seat.",
        "adds_here": "Late-position open には少なくとも Button range で守り、SB steal には A5 / 25 / 35 / 45 を追加します。",
        "still_avoid": "早い位置 open に対する rough fringe の defend を無理に広げないこと。"
      },
      "at_a_glance": {
        "open_core": "No public fixed BB first-in row.",
        "position_add": "Vs late open = at least Button range; vs SB steal = Button range + A5 / 25 / 35 / 45.",
        "vs_complete": "SB raise 相手には any two-card draw or better を re-raise 候補に置きます。",
        "snap_fold": "EP open に対する rough fringe defend と、reverse implied odds の強い tail。"
      },
      "open_complete": {
        "section_label": "First-In Open",
        "anchor_profile": "defense only / no fixed BB open %",
        "public_range_read": "BB の公開データは first-in open chart ではなく defense 指針です。ここでは無理に open 行を作らず、defense-only seat だと明示します。",
        "table_columns": [
          "Status",
          "Current reading",
          "Notes"
        ],
        "table_rows": [
          [
            "No fixed row",
            "Use the BB defense panel below",
            "Public A-5 material focuses on facing an open, not on BB first-in opens"
          ]
        ],
        "source_note": "BB を first-in open seat として扱う fixed public chart は見つからなかったため、UI でも defense-only として固定しています。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "scope_note",
            "range_read": "Big blind guidance is framed only as defense versus a raiser",
            "notes": "Why BB has no first-in open row."
          }
        ]
      },
      "versus_complete": {
        "section_label": "Big Blind Call Range",
        "anchor_profile": "late open defend >= BTN range / vs SB steal >50% defense",
        "public_range_read": "BB は opener 別にコールレンジを読み分けます。late-position open には少なくとも Button opening range、early open にはそれより少し tight、SB steal には A5 / 25 / 35 / 45 を足して 50% 超 defense へ持っていくのが公開 baseline です。UI では BB を first-in open ではなく call range seat として表示します。",
        "table_columns": [
          "Facing open",
          "BB call range",
          "Notes"
        ],
        "table_rows": [
          [
            "Late-position open",
            "Defend with at least the Button opening range",
            "public defend floor"
          ],
          [
            "Early-position open",
            "Slightly tighter than the Button baseline",
            "trim rough fringe"
          ],
          [
            "SB steal",
            "Button range + A5 / 25 / 35 / 45",
            "gets you above 50% defense"
          ],
          [
            "Rereraise",
            "Any two-card draw or better vs SB raise",
            "punish over-wide steals"
          ]
        ],
        "action_bands": [
          {
            "label": "Blind-vs-blind で前に出る帯",
            "tone": "attack",
            "range_read": "SB raise 相手には any two-card draw or better を re-raise 候補に置きます。",
            "when": "BB closing action / heads-up blind war。",
            "examples": "A5 / 25 / 35 / 45 add-ons + any two-card draw or better"
          },
          {
            "label": "守る基準線",
            "tone": "conditional",
            "range_read": "Late open には少なくとも Button range で defend。Early open にはそこから少し締めます。",
            "when": "CO / BTN raise vs EP raise を分ける時。",
            "examples": "Button baseline vs late / tighter than button vs EP"
          },
          {
            "label": "締める帯",
            "tone": "fold",
            "range_read": "EP open に対する rough fringe defend は下げます。reverse implied odds が強い tail を無理に残しません。",
            "when": "早い位置の tight open や multiway 化しやすい場面。",
            "examples": "rough two-card fringe below the Button baseline"
          }
        ],
        "source_note": "CountingOuts が late-position defend floor、SB steal に対する A5 / 25 / 35 / 45 add、そして any two-card draw or better の rereraise を明示しています。",
        "collected_rows": [
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "defense_floor",
            "range_read": "Defend against a late-position raiser with at least the Button opening range",
            "notes": "BB continue の基本線。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "sb_steal_add",
            "range_read": "Adding A5, 25, 35, and 45 to the Button range gets you over 50% of hands versus an SB raise",
            "notes": "blind-vs-blind の widen。"
          },
          {
            "source_ref": "countingouts_predraw",
            "evidence_type": "rereraise_rule",
            "range_read": "Versus an SB raise, re-raise with any two-card draw or better",
            "notes": "BB attack band の主ソース。"
          }
        ]
      },
      "source_refs": [
        "countingouts_predraw"
      ]
    }
  },
  "source_index": {
    "countingouts_predraw": {
      "title": "CountingOuts: Ace to Five Triple Draw - Strategy before the First Draw",
      "short_label": "CountingOuts Predraw",
      "url": "https://www.countingouts.com/ace-to-five-triple-draw-before-the-first-draw/",
      "source_type": "HTML",
      "weight": "primary"
    },
    "countingouts_basic": {
      "title": "CountingOuts: Ace to Five Triple Draw Lowball Rules and Basic Strategy",
      "short_label": "CountingOuts Basic",
      "url": "https://www.countingouts.com/ace-to-five-triple-draw-rules-and-basic-strategy/",
      "source_type": "HTML",
      "weight": "supporting"
    },
    "cardplayer_predraw": {
      "title": "CardPlayer / Kevin Haney: Ace-To-Five Triple Draw: Playing Before The First Draw",
      "short_label": "CardPlayer Haney",
      "url": "https://www.cardplayer.com/cardplayer-poker-magazines/66523-phil-hellmuth-36-19/articles/24908-ace-to-five-triple-draw-playing-before-the-first-draw",
      "source_type": "HTML",
      "weight": "primary"
    },
    "betmgm_basic": {
      "title": "BetMGM: Ace-to-Five Triple Draw: Basic Strategy Tips",
      "short_label": "BetMGM Basic",
      "url": "https://poker.betmgm.com/en/blog/poker-guides/ace-to-five-triple-draw-strategy-tips/",
      "source_type": "HTML",
      "weight": "secondary"
    },
    "wpt_rules": {
      "title": "WPT Global: Ace-to-Five Lowball Poker | Rules & Hand Rankings",
      "short_label": "WPT Rules",
      "url": "https://wptglobal.com/ace-to-five",
      "source_type": "HTML",
      "weight": "rules"
    },
    "jopt_mix_td_pdf": {
      "title": "JOPT Tokyo Players Guide #49 MIX Triple Draw PDF",
      "short_label": "JOPT MIX TD PDF",
      "url": "https://japanopenpoker.com/wp-content/uploads/2024/12/Players_Guide_2025-JOPT-Tokyo01-TD2.pdf",
      "source_type": "PDF",
      "weight": "supplemental_pdf"
    }
  },
  "verification": {
    "checked_on": "2026-04-18",
    "method": "2026-04-18 に CountingOuts / CardPlayer / BetMGM / WPT rules / JOPT mix triple draw PDF を再確認し、position 別の open / continue へ再分解",
    "confirmed_source_refs": [
      "countingouts_predraw",
      "countingouts_basic",
      "cardplayer_predraw",
      "betmgm_basic",
      "wpt_rules",
      "jopt_mix_td_pdf"
    ]
  }
};

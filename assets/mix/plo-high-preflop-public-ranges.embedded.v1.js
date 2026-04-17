window.__PLO_HIGH_PREFLOP_PUBLIC_RANGES_V1 = {
  "dataset_id": "plo_high_preflop_position_ranges_v1",
  "version": 1,
  "scope": {
    "game": "pot_limit_omaha_high_4card",
    "phase": "preflop",
    "position_buttons": [
      "UTG",
      "HJ",
      "CO",
      "BTN",
      "SB",
      "BB"
    ],
    "position_button_meaning": "6-max cash の UTG / HJ(MP) / CO / BTN / SB / BB。BB は defense-only seat として表示する",
    "reconstruction_method": "公開 HTML 記事と Upswing PDF を再確認し、PLO の open / call / defend をポジション別の hand-family surface へ再分解した統合表示。完全 solver tree ではなく、公開で確認できる帯域と hand-family 境界に限定する"
  },
  "collection_notes": [
    "2026-04-18 に Upswing PDF、PokerVIP、PLO Genius の open / SB / blind-defense / 3-bet 記事、PLO Mastermind の cold-call 記事を再確認し、PLO High preflop を位置別に組み直しました。",
    "前回の shorthand 羅列はやめ、各席を open_first_in と versus_open に分け、open core / 位置で追加 / vs open / snap fold の front surface を作り直しています。",
    "公開ソースの性質上、PLO は combo dump より hand class・suitedness・frequency band で示されることが多いので、UI も family-first で表示します。",
    "UTG-HJ-CO-BTN は first-in open と、より前の open に対する continue を分離しました。SB は rake-sensitive な first-in と almost-no-call の defend を分け、BB は defense-only seat として表示します。",
    "Upswing PDF の pair / non-pair class table は detail surface として残しつつ、前面は position ごとの range interpretation に寄せています。",
    "画像中心で公開される solver graphic は exact combo chart を装わず、本文で確認できる frequency band と hand-family rule を前面に残しています。"
  ],
  "global_source_refs": [
    "upswing_rfi_pdf",
    "pokervip_6max_chart",
    "plogenius_opening_ranges",
    "plogenius_small_blind",
    "plogenius_blinds",
    "plomastermind_calling_preflop",
    "plogenius_ip_3bet",
    "plogenius_oop_3bet"
  ],
  "position_order": [
    "UTG",
    "HJ",
    "CO",
    "BTN",
    "SB",
    "BB"
  ],
  "positions": {
    "UTG": {
      "label": "UTG / first-in baseline",
      "role_label": "first-in open seat",
      "open_band": "16.8% to 17.9%",
      "versus_open_band": "n/a as caller; later seats continue only sparsely versus UTG",
      "source_seat": "direct UTG row across Upswing PDF, PLO Genius, and PokerVIP",
      "position_summary": "6-max の先頭 seat で、後ろ全員に position disadvantage を背負う最小 RFI 帯です。",
      "caution_note": "低〜中レートでは cold call が理論より多く multiway になりやすいので、公開 solver の末端 hand はそのまま真似せず trim する前提で読みます。",
      "overview": {
        "seat_trigger": "後ろに HJ / CO / BTN / SB / BB の全員が残るため、realization の悪い hand は open EV を失いやすい席です。",
        "open_identity": "AAxx、強い Ace-suited structure、premium double-suited Broadway、high-connected rundown、最良の pair+connectivity が軸です。",
        "adds_here": "UTG は widen する席ではなく、QQ / JJ / TT や connected hand の中でも suit と connectivity が高いものだけを残す seat として扱います。",
        "still_avoid": "rainbow middling pairs、backup のない low Ace、dangling 2/3/4 を抱えた disconnected hand、弱い 2-gap / non-Ace trash。"
      },
      "at_a_glance": {
        "open_core": "AAxx / AKKx・AQQx の強い suited 版 / AKQJds・AKJTds / QJT9r+ / 9876ss+",
        "position_add": "UTG では追加より cut line 管理が重要。QQ-JJ-TT も DS / best SS に寄せる",
        "vs_open": "この seat 自体に cold-call row はないが、後続 seat は rare flat + around 5% 3-bet + SB almost-no-call で圧力を返す",
        "snap_fold": "rainbow QQ/JJ/TT tail / weak A[5-2] / disconnected middle cards / tri-suit junk"
      },
      "open_first_in": {
        "section_label": "オープン / RFI",
        "public_range_read": "UTG の公開 overlap は、AAxx と Ace-suited premium、high-connected rundown、そして strong Broadway / pair structure を中核に置く narrow first-in range です。PokerVIP は保守的 floor、Upswing PDF は suit-sensitive exact class、PLO Genius は low-stakes で末端 hand を削る読みを与えます。",
        "range_groups": [
          {
            "label": "UTG core",
            "tone": "attack",
            "items": [
              "AAxx almost always",
              "AKKx / AQQx の strong suited structure",
              "AKQJds / AKJTds / AQJTds",
              "QJT9r+ / QT98ds",
              "9876ss+ / T986ss+ / T976ss+"
            ]
          },
          {
            "label": "UTG の下限で残す",
            "tone": "conditional",
            "items": [
              "KK / QQ / JJ / TT mostly DS or best SS",
              "99-66 は mainly DS and selective SS",
              "A[9-6] は mostly DS and best SS",
              "1-gap / 2-gap でも high-connected and well-suited only",
              "9988+ / JJT8ds+ / QQ98ss+ / QQT8ss+"
            ]
          },
          {
            "label": "UTG で切る",
            "tone": "fold",
            "items": [
              "rainbow medium pair tails",
              "backup のない A[5-2] rainbow",
              "Other non-A disconnected middling hands",
              "2 や 3 がぶら下がる weak structure",
              "unconnected tri-suit and trips junk"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "素直に開く帯",
            "tone": "attack",
            "range_read": "AAxx、Ace-suited premium、Broadway-heavy DS、最良の high rundown を first-in で開きます。",
            "when": "後ろが全員残るので、nuttiness と suitedness が強く、OOP でも EV を保ちやすい hand から始めます。",
            "examples": "AAxx / AKQJds / AKJTds / QJT9r / 9876ss"
          },
          {
            "label": "公開 GTO の末端",
            "tone": "conditional",
            "range_read": "QQ-JJ-TT、99-66、A[9-6]、一部 1-gap / 2-gap は suit と backup がある時だけ残します。",
            "when": "multiway 化しやすい low-to-mid stakes では、この帯を無条件採用せず trim する読みが PLO Genius と整合します。",
            "examples": "QQxxds / JJxxss / TT98ss / A987as"
          },
          {
            "label": "実戦では切りやすい帯",
            "tone": "fold",
            "range_read": "rainbow middling pair、weak low Ace、danglers 多めの connected hand、other non-A trash は UTG から外します。",
            "when": "reverse implied odds と OOP realization の悪さが最も厳しいためです。",
            "examples": "QQxx rainbow tail / A542r / disconnected 2-gap middling hand"
          }
        ],
        "table_columns": [
          "確認ソース",
          "頻度 / 境界",
          "意味"
        ],
        "table_rows": [
          [
            "Upswing PDF",
            "17.9%",
            "Monker 由来の exact UTG RFI total。AA は全 suit structure、KK-22 は suitedness で急激に枝分かれする"
          ],
          [
            "PLO Genius",
            "16.8%",
            "100BB low-stakes solver band。理論上より cold call が多い pool では末端 hand を削るよう促す"
          ],
          [
            "PokerVIP",
            "conservative shorthand floor",
            "Broadway-heavy / AAxx / premium rundown floor for first-in practice"
          ]
        ],
        "source_note": "UTG の実用再構築は、Upswing の class table を主軸に、PokerVIP の floor chart で具体例を補い、PLO Genius の low-stakes caution で下限を削る形が最も整合的です。",
        "collected_rows": [
          {
            "source_ref": "upswing_rfi_pdf",
            "evidence_type": "solver_frequency",
            "range_read": "Upswing の Monker-based PDF は UTG RFI を 17.9% とし、AA は常時 open、KK-22 と non-pair class は suitedness ごとに sharp に枝分かれさせる。",
            "notes": "PDF の pair / non-pair tables が exact class boundary の主ソース。"
          },
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "solver_frequency",
            "range_read": "PLO Genius は 100BB low-stakes 前提で UTG を 16.8% とし、pool が過剰に cold call するなら worst GTO fringe を落とすべきだと説明する。",
            "notes": "理論 band を実戦でどう削るかの補助。"
          },
          {
            "source_ref": "pokervip_6max_chart",
            "evidence_type": "conservative_chart",
            "range_read": "PokerVIP の UTG shorthand は Broadway-heavy premium と clean rundown の保守的 floor を与える。",
            "notes": "公開で読める具体例の floor chart。"
          }
        ]
      },
      "versus_open": {
        "section_label": "UTG オープンに対するテーブル反応",
        "public_range_read": "UTG open に対しては、後ろの seat は理論上かなりタイトに続きます。PLO Genius は cold call rare / 3-bet around 5% / SB almost-no-call / BB call under 14% という構図を本文で明示しており、低レート実戦ではこれより call が増えがちです。",
        "table_columns": [
          "後続 seat",
          "続き方",
          "読み"
        ],
        "table_rows": [
          [
            "HJ / CO",
            "thin cold call + around 5% 3-bet",
            "players behind が残るので flat は薄く、Ace-heavy pressure が中心"
          ],
          [
            "BTN",
            "main flatting seat",
            "guaranteed position があるため、UTG への cold call は BTN が最も持ちやすい"
          ],
          [
            "SB",
            "almost pure 3-bet-or-fold",
            "PLO Genius blind article は SB の cold call をほぼ消す"
          ],
          [
            "BB",
            "calls less than 14%",
            "closes action preflop だが、tight opener 相手に OOP defense は still selective"
          ]
        ],
        "source_note": "UTG に対する table reaction は、『どの seat が main caller か』『どこが almost-no-call か』を front に出す方が公開ソースの粒度に合います。",
        "collected_rows": [
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "reaction_band",
            "range_read": "PLO Genius は UTG open に対して cold call は rare、3-bet は around 5%、SB はほとんど call しないと説明する。",
            "notes": "UTG open に対する公開 reaction の本文根拠。"
          },
          {
            "source_ref": "plogenius_blinds",
            "evidence_type": "blind_boundary",
            "range_read": "SB cold call は leak になりやすく、BB は SB よりずっと頻繁に defend するという blind structure を与える。",
            "notes": "blind seat の極端な非対称性を補強する。"
          },
          {
            "source_ref": "plomastermind_calling_preflop",
            "evidence_type": "rake_warning",
            "range_read": "low stakes の passive preflop entry は rake で傷みやすく、後ろが多い seat ほど cold call を締めるべきだとする。",
            "notes": "HJ / CO のフラットが薄くなる理由を補う根拠。"
          }
        ]
      },
      "source_refs": [
        "upswing_rfi_pdf",
        "plogenius_opening_ranges",
        "pokervip_6max_chart",
        "plogenius_blinds",
        "plomastermind_calling_preflop"
      ]
    },
    "HJ": {
      "label": "HJ / MP transition",
      "role_label": "first-in open seat + first practical cold-call seat",
      "open_band": "21.5% to 21.8%",
      "versus_open_band": "thin cold call + tight Ace-heavy 3-bet versus UTG",
      "source_seat": "public MP row in PLO Genius and PokerVIP / HJ row in Upswing PDF",
      "position_summary": "UTG より 1 seat 後ろで、still-tight だが pure opening floor から実戦レンジへ少し広がる transition seat です。",
      "caution_note": "HJ は open も defend も『少し広がる』だけで、BTN のような realization edge はまだありません。players behind と rake が flat range を強く圧縮します。",
      "overview": {
        "seat_trigger": "UTG より 1 人少ないものの、CO / BTN / blinds がまだ控えているため、widen は Ace と suitedness を伴う構造から始まります。",
        "open_identity": "UTG core を維持しつつ、high-card DS / SS、better one-gap rundown、secondary pair structure を加える seat です。",
        "adds_here": "KK54ss+、QQBBss、QT98ss、J987ds、A876as、9987ss、9877ss、T998ss、any BBBBds を加える読みが PokerVIP の保守 chart と一致します。",
        "still_avoid": "Ace なしの naked pair tail、weak single-suited queens、low-dangler hand、disconnect した middling non-A。"
      },
      "at_a_glance": {
        "open_core": "UTG core + more A[K-T] / better 1-gap rundowns / stronger secondary pairs",
        "position_add": "KK54ss+ / QQBBss / QT98ss / J987ds / A876as / any BBBBds",
        "vs_open": "UTG に対しては thin cold call。call は KKxx / selective QQxx / in-between Ace DS rundown、3-bet は Ace-heavy premium に寄る",
        "snap_fold": "naked KK / QQ without Ace or suit / weak SS queens / bad low-dangler non-Ace hands"
      },
      "open_first_in": {
        "section_label": "オープン / RFI",
        "public_range_read": "HJ は UTG core を維持しつつ、より多くの suited broadway、better one-gap rundown、そして suited pair structure を取り込む位置です。Upswing の exact class table は UTG に比べて KK-22 と A[K-T] / A[9-6] / Other A の suited branch が明確に広がることを示します。",
        "range_groups": [
          {
            "label": "HJ core",
            "tone": "attack",
            "items": [
              "UTG core 全体",
              "A[K-T] and A[9-6] more often",
              "0-gap and strong 1-gap rundown",
              "KK / QQ / JJ / TT in more SS and some rainbow branches",
              "better Other A suited structures"
            ]
          },
          {
            "label": "HJ で追加する family",
            "tone": "conditional",
            "items": [
              "KK54ss+",
              "QQBBss",
              "QT98ss / J987ds",
              "A876as",
              "9875ss / 9865ss / 9987ss / 9877ss / T998ss",
              "any BBBBds hand"
            ]
          },
          {
            "label": "HJ でも切る帯",
            "tone": "fold",
            "items": [
              "weak rainbow pair tails",
              "A[5-2] rainbow tail",
              "disconnect した 2-gap middling hand",
              "low card dangler が重い non-Ace hand",
              "Other non-A weak tail"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "素直に open",
            "tone": "attack",
            "range_read": "UTG core に加え、HJ では high-card suited structure と best 1-gap がより多く open に残ります。",
            "when": "position はまだ弱いので、Ace と suit quality が十分な hand から widen します。",
            "examples": "AKQJds / QQxxds / A876as / J987ds"
          },
          {
            "label": "HJ 追加帯",
            "tone": "conditional",
            "range_read": "PokerVIP の explicit additions と Upswing の wider class rates が重なる hand を HJ add-on として扱います。",
            "when": "UTG では薄いが、HJ では one player fewer and slightly better realization で利益化しやすい帯です。",
            "examples": "KK54ss / QQBBss / QT98ss / any BBBBds"
          },
          {
            "label": "まだ外す帯",
            "tone": "fold",
            "range_read": "Ace なしの weak pair、bad low-A、disconnect した middling hand は HJ でも保留です。",
            "when": "CO / BTN / blinds がまだ多く残り、flat + squeeze pressure を受けるためです。",
            "examples": "naked QQxx / A542r / weak 2-gap middling hand"
          }
        ],
        "table_columns": [
          "確認ソース",
          "頻度 / 境界",
          "意味"
        ],
        "table_rows": [
          [
            "Upswing PDF",
            "21.8%",
            "HJ RFI total。KK/QQ/TT と A[K-T]、Other A の suited branch が UTG より大きく広がる"
          ],
          [
            "PLO Genius",
            "21.5%",
            "100BB low-stakes の MP opening frequency。UTG より widen するが still selective"
          ],
          [
            "PokerVIP",
            "UTG + explicit additions",
            "KK54ss+ / QQBBss / J987ds / A876as / any BBBBds を middle-seat add として提示"
          ]
        ],
        "source_note": "HJ open の reconstruction は、Upswing の exact class widening を背骨に、PokerVIP の explicit add list で具象化し、PLO Genius の low-stakes caution で fringe を締める形で作っています。",
        "collected_rows": [
          {
            "source_ref": "upswing_rfi_pdf",
            "evidence_type": "solver_frequency",
            "range_read": "Upswing PDF は HJ RFI を 21.8% とし、UTG より KK-22 と non-pair suited branches が明確に広がる。",
            "notes": "UTG と HJ の widening の exact 主ソース。"
          },
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "solver_frequency",
            "range_read": "PLO Genius は MP を 21.5% とし、early / middle は low-stakes で still selective に保つべきだと説明する。",
            "notes": "HJ を MP row として読む public article 根拠。"
          },
          {
            "source_ref": "pokervip_6max_chart",
            "evidence_type": "conservative_chart",
            "range_read": "PokerVIP の MP row は UTG へ specific add-on を積む形式で、HJ widening を category 単位で示す。",
            "notes": "explicit add list のソース。"
          }
        ]
      },
      "versus_open": {
        "section_label": "UTG オープンに対する継続",
        "public_range_read": "HJ が UTG open に向かう時は、cold call は『強いが 3-bet しきれない hand』だけに残り、3-bet は Ace-heavy premium に寄ります。PLO Mastermind の MP vs EP call examples と PLO Genius の MP vs UTG 3-bet article が、この split をかなりはっきり示しています。",
        "range_groups": [
          {
            "label": "3-bet 主力",
            "tone": "attack",
            "items": [
              "AAxx almost all",
              "AKKx / AQQx with suit and connectivity",
              "AKJT-type Ace-high DS rundown",
              "selective TT99ds / 6655ds / 5544ds",
              "strong SS Ax-connected hands such as A776 / AJT9 / AQJ8"
            ]
          },
          {
            "label": "thin cold call",
            "tone": "conditional",
            "items": [
              "KKxx class mainly DS or double-paired",
              "QQxx with Ace / nut suit / strong connectivity",
              "in-between Ace-high DS rundowns",
              "strong hands that are too good to fold but not sturdy enough to 3-bet"
            ]
          },
          {
            "label": "fold に回す帯",
            "tone": "fold",
            "items": [
              "naked KK / QQ without Ace",
              "weak single-suited queens",
              "low-dangler rundowns",
              "most non-Ace hands outside the top 3-bet shell"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "3-bet",
            "tone": "attack",
            "range_read": "UTG の narrow range に対しては Ace-heavy premium と high-connectivity suited hand を主に 3-bet します。",
            "when": "players behind も残るため、dominated されにくく、4-bet に耐えやすい構造が必要です。",
            "examples": "AAxx / AKKx / AQQx / AKJTds / TT99ds"
          },
          {
            "label": "cold call",
            "tone": "conditional",
            "range_read": "DS or double-paired KKxx、かなり選んだ QQxx、in-between Ace DS rundown が main call shell です。",
            "when": "3-bet に回すほどではないが、fold するには強すぎる hand だけが残ります。",
            "examples": "best KKxx call / selective QQxx / middling Ace DS rundown"
          },
          {
            "label": "fold",
            "tone": "fold",
            "range_read": "Ace なしの weak pair や weak single-suited queens、low-dangler hand は rake と squeeze risk で外します。",
            "when": "passive entry には fold equity がなく、後ろの squeeze も残るためです。",
            "examples": "naked QQxx / poor SS queens / low-dangler rundown"
          }
        ],
        "table_columns": [
          "ハンド帯 / spot",
          "主扱い",
          "補足"
        ],
        "table_rows": [
          [
            "KKxx class",
            "call 27% of the class",
            "PLO Mastermind は DS or double-paired kings を main cold-call shell として示す"
          ],
          [
            "QQxx class",
            "call 13% of the class",
            "Ace / nut suit / strong connectivity がない single-suited queens はかなり絞る"
          ],
          [
            "Ace-high DS rundowns",
            "call 17% of the class",
            "最強は 3-bet、真ん中の quality band が call、弱いものは fold"
          ],
          [
            "3-bet template",
            "tight Ace-heavy",
            "PLO Genius MP vs UTG は AAxx・AKKx・AQQx・Ace DS rundown・selective double pairs が中心"
          ]
        ],
        "source_note": "HJ vs UTG は、PLO Mastermind の cold-call bottom examples と、PLO Genius の MP vs UTG 3-bet template を並べると『call に残る class』と『3-bet に回る class』がかなりきれいに分かれます。",
        "collected_rows": [
          {
            "source_ref": "plomastermind_calling_preflop",
            "evidence_type": "cold_call_example",
            "range_read": "MP vs EP の bottom examples として、Kings class 27%、Queens class 13%、Ace-high DS rundown class 17% が call side に残る。",
            "notes": "HJ flat shell の具体的な public evidence。"
          },
          {
            "source_ref": "plogenius_ip_3bet",
            "evidence_type": "ip_3bet_template",
            "range_read": "MP vs UTG の 3-bet は AAxx、AKKx、AQQx、Ace-high DS rundown、selective double-paired hand、strong SS Ax-connected hand に集中する。",
            "notes": "HJ 3-bet shell の構造。"
          },
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "reaction_band",
            "range_read": "UTG open に対して MP/HJ の cold call は rare で、3-bet は around 5% とされる。",
            "notes": "HJ が thin flat seat であることの公開説明。"
          }
        ]
      },
      "source_refs": [
        "upswing_rfi_pdf",
        "plogenius_opening_ranges",
        "pokervip_6max_chart",
        "plomastermind_calling_preflop",
        "plogenius_ip_3bet"
      ]
    },
    "CO": {
      "label": "CO / late-position widen",
      "role_label": "first-in open seat + wider in-position continue seat",
      "open_band": "29% to 30%",
      "versus_open_band": "still tight versus UTG, slightly wider versus MP",
      "source_seat": "direct CO row across Upswing PDF and PLO Genius; late-position add list in PokerVIP",
      "position_summary": "CO は初めて『自分より position を持つ相手が 1 人に減る』席で、公開 open band がいちばん分かりやすく広がり始める位置です。",
      "caution_note": "CO は wide open の入口ですが、BTN だけは still huge factor です。BTN が loose なら公開 GTO の末端 hand をそのまま持ち込みません。",
      "overview": {
        "seat_trigger": "BTN だけが guaranteed positional threat なので、postflop realization が一段改善し、single-suited と middle rundown の一部が利益化しやすくなります。",
        "open_identity": "AAxx と broadway / ace-suited core を維持しつつ、more KK / QQ / JJ / TT、more 1-gap / 2-gap、more Other A suited branches を加える seat です。",
        "adds_here": "BBBxds、KKxx、QQ76ss+、A88xas+、5566+、4567ss+、7765ss+、8776ss+、A456as+、K765ks+、8654ds+、T98xds+、QJ9xds+、QT9xds+、any BBBBss を late-position add として使います。",
        "still_avoid": "BTN に dominated されやすい weak disconnected middling hand、rainbow low-A tail、weak Other non-A trash。"
      },
      "at_a_glance": {
        "open_core": "AAxx / almost any KK / more QQ-JJ-TT / A[K-T] / A[9-6] / stronger 1-gap and 2-gap",
        "position_add": "BBBxds / KKxx / QQ76ss+ / 5566+ / 4567ss+ / A456as+ / T98xds+ / any BBBBss",
        "vs_open": "UTG には still tight、MP には少し widen。flat は HJ より広いが low-stakes で loose-flat seat にはしない",
        "snap_fold": "weak rainbow A[5-2] / disconnected middling non-A / BTN pressure に耐えない loose tail"
      },
      "open_first_in": {
        "section_label": "オープン / RFI",
        "public_range_read": "CO では open band が 29-30% に広がり、Almost any KK combo is good enough to open という PLO Genius の説明どおり、pair branch と suited middling connectivity が明確に増えます。PokerVIP の CO add list はこの widen を hand-family へ落とした conservative shorthand です。",
        "range_groups": [
          {
            "label": "CO core",
            "tone": "attack",
            "items": [
              "UTG / HJ core 全体",
              "almost any KK combo",
              "more QQ / JJ / TT / 99-66",
              "more A[K-T] / A[9-6] / Other A suited",
              "more 1-gap and selected 2-gap"
            ]
          },
          {
            "label": "CO 追加 family",
            "tone": "conditional",
            "items": [
              "BBBxds and any BBBBss",
              "KKxx / QQ76ss+ / A88xas+",
              "5566+ / 4567ss+ / 7765ss+ / 8776ss+",
              "A456as+ / K765ks+ / 9765ss+ / 8654ds+",
              "JT9xss+ / T98xds+ / QJ9xds+ / QT9xds+"
            ]
          },
          {
            "label": "CO でもまだ外す",
            "tone": "fold",
            "items": [
              "BTN に dominated されやすい weak rainbow middling hand",
              "bad low-A tail",
              "disconnect した Other non-A",
              "garbage tri-suit / trips junk"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "積極的に open",
            "tone": "attack",
            "range_read": "UTG / HJ core に almost-any KK と wider suited connectivity を足して open します。",
            "when": "BTN 以外に position disadvantage が残らず、postflop realization が大きく改善するためです。",
            "examples": "KKxx / QQxxss / A88xas / 4567ss / T98xds"
          },
          {
            "label": "late-position add",
            "tone": "conditional",
            "range_read": "PokerVIP の explicit CO add list と Upswing の widened branches が重なる family を late-position widening として扱います。",
            "when": "BTN が過剰に VPIP しない時ほど、これらの middling but playable hand が利益化します。",
            "examples": "BBBxds / KKxx / 5566 / A456as / QJ9xds"
          },
          {
            "label": "BTN 依存で cut",
            "tone": "fold",
            "range_read": "BTN が loose に cold call / 3-bet する pool では、CO 末端の disconnected hand を削ります。",
            "when": "PLO Genius の CO article が BTN stats を最重要 adjustment point としているためです。",
            "examples": "rainbow low-A tail / weak Other non-A / bad middling disconnected hand"
          }
        ],
        "table_columns": [
          "確認ソース",
          "頻度 / 境界",
          "意味"
        ],
        "table_rows": [
          [
            "Upswing PDF",
            "30.0%",
            "CO RFI total。KK almost-any open と QQ-JJ-TT / A[K-T] / A[9-6] / Other A の widen が確認できる"
          ],
          [
            "PLO Genius",
            "around 29%",
            "100BB low-stakes solver band。CO の調整は BTN cold call / 3-bet と steal defense に強く依存すると説明"
          ],
          [
            "PokerVIP",
            "HJ + late add list",
            "BBBxds / KKxx / 5566+ / A456as+ / T98xds+ などの explicit late-position widening"
          ]
        ],
        "source_note": "CO open は、Upswing の exact class table、PLO Genius の『Almost any KK combo is good enough to open in CO』、PokerVIP の late add list が一番きれいにかみ合う spot です。",
        "collected_rows": [
          {
            "source_ref": "upswing_rfi_pdf",
            "evidence_type": "solver_frequency",
            "range_read": "Upswing PDF は CO RFI を 30.0% とし、KK almost-any と wider suited middling connectivity を許容する。",
            "notes": "CO widening の exact 背骨。"
          },
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "solver_frequency",
            "range_read": "PLO Genius は CO open を around 29% とし、BTN cold call / 3-bet と blind fold-to-steal を main adjustment point とする。",
            "notes": "CO の exploit focus。"
          },
          {
            "source_ref": "pokervip_6max_chart",
            "evidence_type": "conservative_chart",
            "range_read": "PokerVIP の CO row は late-position add list を explicit に列挙し、family widening を読みやすくする。",
            "notes": "具体例補完。"
          }
        ]
      },
      "versus_open": {
        "section_label": "より前のオープンに対する継続",
        "public_range_read": "CO は in-position continue seat として HJ より広く flat できますが、UTG 相手には依然 tight です。PLO Genius の IP 3-bet article は CO vs UTG が MP vs UTG とほぼ同じ、CO vs MP が 6.2% まで少し widen すると説明します。",
        "range_groups": [
          {
            "label": "3-bet 主力",
            "tone": "attack",
            "items": [
              "AAxx core",
              "premium connected DS hands",
              "selective Ax rundown",
              "UTG には MP template とほぼ同じ",
              "MP 相手には suited Ace / connected structure を少し wider"
            ]
          },
          {
            "label": "call shell",
            "tone": "conditional",
            "items": [
              "HJ より多めの KKxx / QQxx calls",
              "DS double-paired hands not strong enough to 3-bet",
              "in-between Ace-high DS rundowns",
              "position で利益化する connected DS / best SS"
            ]
          },
          {
            "label": "still fold",
            "tone": "fold",
            "items": [
              "weak rainbow pair tail",
              "bad low-A tail",
              "disconnect した middling non-A",
              "rake で削られる loose flats"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "vs UTG",
            "tone": "conditional",
            "range_read": "CO vs UTG 3-bet は MP vs UTG とほぼ同じで、Ace-heavy premium と strong suited connectivity に絞ります。",
            "when": "tight opener 相手で dominated されにくい構造を優先するためです。",
            "examples": "AAxx / AKKx / AQQx / premium Ace DS rundown"
          },
          {
            "label": "vs MP",
            "tone": "attack",
            "range_read": "CO vs MP は 6.2% まで少し widen し、suited Ace と connected structure が増えます。",
            "when": "open range が広がるぶん、CO 側の in-position pressure も増やせます。",
            "examples": "wider Ax connected 3-bets / more playable DS"
          },
          {
            "label": "flat / fold",
            "tone": "fold",
            "range_read": "low stakes では passive entry に rake が乗るので、HJ より広いとはいえ loose-flat seat にはしません。",
            "when": "PLO Mastermind が『closer to the button = wider calls』と言いつつ、low stakes の passive entry を締めるためです。",
            "examples": "best KKxx / QQxx / in-between DS call, weak tail fold"
          }
        ],
        "table_columns": [
          "spot",
          "主扱い",
          "補足"
        ],
        "table_rows": [
          [
            "CO vs UTG",
            "MP template とほぼ同じ 3-bet shell",
            "AAxx・premium DS・selective Ax rundown が中心"
          ],
          [
            "CO vs MP",
            "3-bet widens slightly to 6.2%",
            "suited Ace と connected structure を少し広げる"
          ],
          [
            "cold call",
            "HJ より広いが still disciplined",
            "button に近づくほど widen するが、rake が low-stakes flat を強く圧縮する"
          ]
        ],
        "source_note": "CO continue は『UTG にはまだ tight』『MP 相手に少し widen』『flat は HJ より広いが low-stakes では still disciplined』の 3 点に集約できます。",
        "collected_rows": [
          {
            "source_ref": "plogenius_ip_3bet",
            "evidence_type": "ip_3bet_template",
            "range_read": "CO vs UTG の 3-bet range は MP vs UTG とほぼ同じで、CO vs MP は 6.2% まで slightly widen する。",
            "notes": "CO 3-bet shell の基礎。"
          },
          {
            "source_ref": "plomastermind_calling_preflop",
            "evidence_type": "position_widen_rule",
            "range_read": "button に近づくほど cold call は widen するが、low stakes の passive entry は still tight に保つべきだとする。",
            "notes": "CO flat が HJ より広い理由と限界。"
          },
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "co_adjustment_rule",
            "range_read": "CO open / continue の主調整点は BTN の participation と blind defense である。",
            "notes": "CO の末端を自動で広げすぎない理由。"
          }
        ]
      },
      "source_refs": [
        "upswing_rfi_pdf",
        "plogenius_opening_ranges",
        "pokervip_6max_chart",
        "plomastermind_calling_preflop",
        "plogenius_ip_3bet"
      ]
    },
    "BTN": {
      "label": "BTN / widest first-in seat",
      "role_label": "widest first-in open seat + main cold-call seat",
      "open_band": "47.2% to roughly 48%",
      "versus_open_band": "widest in-position continue seat; 7.8% 3-bet versus CO",
      "source_seat": "direct BTN row in Upswing PDF and PokerVIP / BU row in PLO Genius",
      "position_summary": "BTN は公開ソースの中で最も広い first-in seat で、open も continue も position がそのまま EV source になります。",
      "caution_note": "BTN でも garbage は garbage のままです。公開 consensus は『open anything connected』ではなく、still suitedness・nut domination・connectivity を中心に widen しています。",
      "overview": {
        "seat_trigger": "後ろは blinds だけで、postflop は常に position を持つため、single-suited / middling connected hand の実現率が跳ね上がります。",
        "open_identity": "CO core を持ち込みつつ、wider single-suited middling rundown、A[5-2] suited branch、Other A、そして more Other DS / SS hands を open に残す seat です。",
        "adds_here": "BBBxss、QQxx、A66xas+、A234as+、2345ss+、4455+、3567ss+、4456ss+、6654ss+、7643ss+、K654ks+、7754ss+、8864ss+、J98xds+、876xss+、456xds+ が PokerVIP の explicit BTN add list です。",
        "still_avoid": "position があっても dominated されやすい disconnected middling rainbow、2/3 heavy weak structure、nut potential の薄い trash。"
      },
      "at_a_glance": {
        "open_core": "CO core + more SS middling rundown + more A[5-2] suited branch + more Other A + more Other DS/SS",
        "position_add": "BBBxss / QQxx / A234as+ / 2345ss+ / 4455+ / 3567ss+ / J98xds+ / 456xds+",
        "vs_open": "UTG/MP には main cold-call seat、CO には 7.8% 3-bet。KKxx/QQxx without Ace は mostly calls",
        "snap_fold": "dominated disconnected middling rainbow / weak low-dangler tail / structurally weak DS with deuce+trey"
      },
      "open_first_in": {
        "section_label": "オープン / RFI",
        "public_range_read": "BTN は公開ソルバー系の 47-48% 帯で、open frequency は table で最も広いです。ただし widen の中身は『more suited, more connected, more Ace-backed middling hands』であって、単なる all-connected ではありません。PokerVIP の BTN add list はこの widen を family 単位でかなり綺麗に切り出しています。",
        "range_groups": [
          {
            "label": "BTN core",
            "tone": "attack",
            "items": [
              "CO core 全体",
              "all A[K-T] and much more A[9-6] / A[5-2]",
              "more Other A and Other DS / SS",
              "more QQ / JJ / TT / 99-22",
              "much wider 1-gap / 2-gap and middling connected structure"
            ]
          },
          {
            "label": "BTN add list",
            "tone": "conditional",
            "items": [
              "BBBxss / QQxx",
              "A66xas+ / A234as+",
              "2345ss+ / 4455+ / 3567ss+ / 4456ss+",
              "6654ss+ / 7643ss+ / K654ks+ / 7754ss+ / 8864ss+",
              "J98xds+ / 876xss+ / 456xds+"
            ]
          },
          {
            "label": "BTN でも外す",
            "tone": "fold",
            "items": [
              "dominated disconnected middling rainbow",
              "weak low-dangler trash",
              "poor tri-suit hands",
              "nut potential が薄い connected-looking garbage"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "自由に open する帯",
            "tone": "attack",
            "range_read": "CO までの core をほぼ維持しながら、suited middling connectivity と Ace-backed tail を大きく追加します。",
            "when": "blinds しか後ろにおらず、全 street で position を持てるためです。",
            "examples": "QQxx / A234as / 2345ss / 3567ss / J98xds"
          },
          {
            "label": "BTN widening",
            "tone": "conditional",
            "range_read": "A[5-2] suited branch、Other A、Other DS / SS の一部は BTN で初めてまともに open side へ入ります。",
            "when": "position があっても suit / connectivity / nut domination は still required です。",
            "examples": "A66xas / K654ks / 876xss / 456xds"
          },
          {
            "label": "still fold",
            "tone": "fold",
            "range_read": "connected に見えるだけの weak middling hand や nut potential の薄い trash は BTN でも外します。",
            "when": "公開 consensus が BTN でも domination と suitedness を強く気にしているためです。",
            "examples": "weak disconnected rainbow / low-dangler middling trash"
          }
        ],
        "table_columns": [
          "確認ソース",
          "頻度 / 境界",
          "意味"
        ],
        "table_rows": [
          [
            "Upswing PDF",
            "47.2%",
            "BTN RFI total。A[K-T] は DS / SS / R すべて 100%、Other も 60/20/3 まで widen する"
          ],
          [
            "PLO Genius",
            "roughly 48%",
            "100BB low-stakes solver band。Button is where you can be closest to GTO opening frequency"
          ],
          [
            "PokerVIP",
            "CO + explicit BTN add list",
            "BBBxss / QQxx / A234as+ / 2345ss+ / 4455+ / J98xds+ / 456xds+"
          ]
        ],
        "source_note": "BTN open は数値だけでなく、『どの class が CO から新しく入るか』を前面に出す方が、PLO の hand-family study と UI の両方に合います。",
        "collected_rows": [
          {
            "source_ref": "upswing_rfi_pdf",
            "evidence_type": "solver_frequency",
            "range_read": "Upswing PDF は BTN RFI を 47.2% とし、A[K-T] 全開放、Other A / Other DS-SS branch の大幅 widen を示す。",
            "notes": "BTN widening の exact 主ソース。"
          },
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "solver_frequency",
            "range_read": "PLO Genius は BU を roughly 48% とし、最も GTO frequency に近づける first-in seat だと説明する。",
            "notes": "BTN の高頻度帯と exploit widen の根拠。"
          },
          {
            "source_ref": "pokervip_6max_chart",
            "evidence_type": "conservative_chart",
            "range_read": "PokerVIP の BTN row は CO add list に続く具体的な late-position widening family を提示する。",
            "notes": "open add-on family の可読性補助。"
          }
        ]
      },
      "versus_open": {
        "section_label": "より前のオープンに対する継続",
        "public_range_read": "BTN は公開ソースで main cold-call seat として扱われます。UTG / MP 相手にも flat をかなり持てますが、CO open 相手には 3-bet も 7.8% まで広がり、call と 3-bet の分業がいちばん見やすい seat です。",
        "range_groups": [
          {
            "label": "3-bet 主力",
            "tone": "attack",
            "items": [
              "nearly all non-trip AAxx versus CO",
              "most AKKx and AQQx",
              "roughly half of Ace-high DS rundowns",
              "AJT9 / AKT4 / AK75 style Ace-bearing hands",
              "BB vs SB では all AAxx + half AKKx/AQQx + most DS double pairs"
            ]
          },
          {
            "label": "call shell",
            "tone": "conditional",
            "items": [
              "KKxx and QQxx without an Ace mostly call",
              "in-between DS / SS connected hands",
              "strong but not 4-bet-happy pair structures",
              "more of the strong-not-premium class than any other seat"
            ]
          },
          {
            "label": "fold",
            "tone": "fold",
            "items": [
              "structurally weak DS with deuce+trey",
              "dominated disconnected middling hand",
              "weak low-A rainbow tail",
              "hands that rely only on position and not on structure"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "vs UTG / MP",
            "tone": "conditional",
            "range_read": "main cold-call seat として、strong-but-not-3bet class を多く flat します。",
            "when": "guaranteed position があり、HJ / CO より much easier に equity realization できるためです。",
            "examples": "KKxx no Ace / QQxx no Ace / best connected DS calls"
          },
          {
            "label": "vs CO",
            "tone": "attack",
            "range_read": "3-bet は 7.8% まで widen し、almost all non-trip AAxx・most AKKx/AQQx・about half Ace DS rundown を攻撃側へ回します。",
            "when": "later-position open ほど opener range が広くなり、BTN の IP pressure が強く通るためです。",
            "examples": "AAxx / AKKx / AQQx / Ace DS rundown / AJT9"
          },
          {
            "label": "call > 3-bet に寄せる帯",
            "tone": "fold",
            "range_read": "KKxx / QQxx without Ace は almost never 3-bet で、call side に回すのが基本です。",
            "when": "4-bet を受けると苦しく、しかも AAxx を unblock してしまうからです。",
            "examples": "KKxx no Ace / QQxx no Ace"
          }
        ],
        "table_columns": [
          "spot",
          "主扱い",
          "補足"
        ],
        "table_rows": [
          [
            "BTN vs UTG / MP",
            "main cold-call seat",
            "position guaranteed のため、strong-but-not-3bet class を最も多く flat できる"
          ],
          [
            "BTN vs CO",
            "7.8% 3-bet",
            "AAxx / AKKx / AQQx / about half Ace DS rundown を攻撃側へ回す"
          ],
          [
            "KKxx / QQxx without Ace",
            "mostly call, almost never 3-bet",
            "4-bet に弱く、AAxx を unblock するので call side が本線"
          ]
        ],
        "source_note": "BTN の継続レンジは「最も広いフラット席」と「CO に対する約 7.8% の攻撃席」の二面性で読むのが要点です。ここを分けると、コール帯と 3-bet 帯を羅列せずに整理できます。",
        "collected_rows": [
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "reaction_band",
            "range_read": "UTG open に対する main cold-call seat は BTN であり、guaranteed position が call frequency を支える。",
            "notes": "BTN flat seat の公開説明。"
          },
          {
            "source_ref": "plogenius_ip_3bet",
            "evidence_type": "ip_3bet_template",
            "range_read": "BTN vs CO では 7.8% 3-bet、nearly all non-trip AAxx、most AKKx/AQQx、about half Ace DS rundown が attack shell に入る。",
            "notes": "BTN attack shell の主ソース。"
          },
          {
            "source_ref": "plogenius_ip_3bet",
            "evidence_type": "call_only_pair_rule",
            "range_read": "KKxx と QQxx without Ace は almost never 3-bet で、calling range に回す。",
            "notes": "call side に残る premium pair の境界。"
          }
        ]
      },
      "source_refs": [
        "upswing_rfi_pdf",
        "plogenius_opening_ranges",
        "pokervip_6max_chart",
        "plogenius_ip_3bet"
      ]
    },
    "SB": {
      "label": "SB / rake-sensitive blind aggressor",
      "role_label": "rake-sensitive first-in blind seat + almost-no-call defense seat",
      "open_band": "low stakes: raise 37.4%; high stakes: limp 24.3% / raise 28.5%",
      "versus_open_band": "almost pure 3-bet-or-fold; 4.7% to 6.8% versus EP/MP/CO and about 9.7% to 10% versus BTN",
      "source_seat": "standalone SB article plus blind-defense and OOP 3-bet articles",
      "position_summary": "SB は first-in なら heads-up が確定する一方、全 street で OOP を背負う最も前提依存の seat です。",
      "caution_note": "この seat は fixed one-chart seat ではありません。rake によって limp が消えたり戻ったりし、open と defend の両方で SB cold call がほぼ消えます。",
      "overview": {
        "seat_trigger": "first-in なら opponent は BB だけですが、OOP で posted blind を抱えたまま playability threshold を決める必要があります。",
        "open_identity": "low stakes は raise/fold only が基準で、AA / KK / most QQ / double-paired hands が主力です。",
        "adds_here": "connected・connected pair・double suited の一部は open に残ります。AQ53ds や JJ53ds のように 2/3/4/5 を含んでも quality が高いものは playable とされます。",
        "still_avoid": "cold call、AA 以外の trips、2 や 3 が hand quality を損なう weak structure、BB の 3-bet に耐えない marginal tail。"
      },
      "at_a_glance": {
        "open_core": "all AA / all KK / most QQ / double-paired hands / best connected and DS classes",
        "position_add": "rake が低いほど limp mix が戻る。high stakes は limp 24.3% / raise 28.5% / fold 47.2%",
        "vs_open": "almost no cold call。vs EP/MP/CO は 4.7%-6.8% tight 3-bet、vs BTN は about 9.7%-10% まで widen",
        "snap_fold": "AA 以外の trips / deuce-tray heavy weak structure / KKQQ without Ace versus tight open / default cold call"
      },
      "open_first_in": {
        "section_label": "SB first-in strategy",
        "public_range_read": "SB first-in は公開ソースの中で最も rake-sensitive です。PLO Genius は low stakes で raise/fold only 37.4%、mid stakes でも no-limp 38.9%、high stakes で limp 24.3% / raise 28.5% / fold 47.2% を示し、SB を fixed one-chart ではなく opponent-and-rake dependent seat として扱います。",
        "range_groups": [
          {
            "label": "SB core opens",
            "tone": "attack",
            "items": [
              "all AA",
              "all KK",
              "vast majority of QQ",
              "double-paired hands",
              "best connected and double-suited hands"
            ]
          },
          {
            "label": "quality があれば open",
            "tone": "conditional",
            "items": [
              "connected hands",
              "connected pairs",
              "double-suited hands with strong side cards",
              "AQ53ds / JJ53ds style small-card exceptions",
              "some negative-EV-but-better-than-fold hands at low stakes"
            ]
          },
          {
            "label": "SB で外す",
            "tone": "fold",
            "items": [
              "AA 以外の trips",
              "weak 2 / 3 heavy hands",
              "unintuitive marginal tails",
              "BB 3-bet に耐えない disconnected trash"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "low-stakes baseline",
            "tone": "attack",
            "range_read": "raise/fold only を基本にし、limp を封印します。",
            "when": "高 rake では preflop で pot を取って rake を回避する価値が大きいためです。",
            "examples": "raise 37.4% / fold 62.6%"
          },
          {
            "label": "high-stakes mix",
            "tone": "conditional",
            "range_read": "rake が軽くなると limp mix が戻り、limp 24.3% / raise 28.5% / fold 47.2% に変化します。",
            "when": "OOP でも heads-up で postflop tree を扱いやすくなり、limp EV が回復するためです。",
            "examples": "high-stakes SB mix"
          },
          {
            "label": "quality cut line",
            "tone": "fold",
            "range_read": "AA 以外の trips と weak small-card structure は避け、connected / connected-pair / DS でも quality を要求します。",
            "when": "SB は posted blind の分、slightly negative EV open も混じるが、構造が悪い hand はなお不採用です。",
            "examples": "avoid weak trips / avoid low-dangler trash"
          }
        ],
        "table_columns": [
          "確認ソース",
          "頻度 / 境界",
          "意味"
        ],
        "table_rows": [
          [
            "PLO Genius low stakes",
            "raise 37.4% / fold 62.6%",
            "high-rake pool では raise/fold only baseline"
          ],
          [
            "PLO Genius mid stakes",
            "raise 38.9%",
            "still no-limp baseline"
          ],
          [
            "PLO Genius high stakes",
            "limp 24.3% / raise 28.5% / fold 47.2%",
            "lower rake では limp mix が戻る"
          ],
          [
            "PLO Genius category note",
            "all AA / all KK / most QQ / double-paired hands",
            "Only the strongest QQ and double-suited hands are obvious opens, with the rest decided by structure"
          ]
        ],
        "source_note": "SB first-in は exact fixed chart ではなく、rake structure と BB reaction が主変数です。だから UI も one static shorthand ではなく、low / mid / high stakes band と category rule に分けています。",
        "collected_rows": [
          {
            "source_ref": "plogenius_small_blind",
            "evidence_type": "solver_frequency",
            "range_read": "low stakes は raise/fold only 37.4% / 62.6%、mid stakes でも no-limp 38.9%、high stakes では limp 24.3% / raise 28.5% / fold 47.2%。",
            "notes": "SB first-in frequency の主ソース。"
          },
          {
            "source_ref": "plogenius_small_blind",
            "evidence_type": "category_rule",
            "range_read": "all AA・all KK・vast majority of QQ・double-paired hands が main open class で、connected / connected pair / DS は quality gate を通す。",
            "notes": "SB の hand-family cut line。"
          },
          {
            "source_ref": "plogenius_small_blind",
            "evidence_type": "small_card_exception",
            "range_read": "2 や 3 はしばしば playability を損なうが、AQ53ds や JJ53ds のような best side-card combination は open に残る。",
            "notes": "small-card exception を front に残す根拠。"
          }
        ]
      },
      "versus_open": {
        "section_label": "オープンに対する継続",
        "public_range_read": "SB defense の公開 overlap は非常に明快で、『cold call をほぼ消し、3-bet-or-fold に寄せる』です。EP / MP / CO 相手の 3-bet は 4.7%-6.8% と tight、BTN 相手だけ about 9.7%-10% まで widen します。",
        "range_groups": [
          {
            "label": "3-bet 主力",
            "tone": "attack",
            "items": [
              "almost all AAxx",
              "AKKx and Ace-backed AQQx",
              "strongest DS rundowns",
              "highly playable double-paired hands",
              "vs BTN では some JJxx / TTxx with Ace",
              "vs BTN では around 55% of Ace-high DS hands and about 35% of double-pairs"
            ]
          },
          {
            "label": "3-bet only if upgraded",
            "tone": "conditional",
            "items": [
              "KKxx / QQxx only when accompanied by Ace",
              "suited or well-connected Kings / Queens",
              "best no-more-than-one-gap DS rundown",
              "speculative but playable OOP hands only against BTN"
            ]
          },
          {
            "label": "default fold",
            "tone": "fold",
            "items": [
              "cold call almost always",
              "KK / QQ without Ace versus tight opens",
              "AA 以外の trips",
              "structurally weak DS with deuce+trey",
              "marginal OOP trash"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "vs EP / MP / CO",
            "tone": "conditional",
            "range_read": "3-bet frequency は 4.7%-6.8% で、AA-heavy premium と strongest DS rundown / playable double-pair に絞ります。",
            "when": "OOP で tight opener 相手なので、rarely dominated な structure が必要です。",
            "examples": "AAxx / Ace-backed KKxx or QQxx / best DS rundown"
          },
          {
            "label": "vs BTN",
            "tone": "attack",
            "range_read": "Button open には 9.7%-10% まで widen し、AQQx、Ace 付き JJxx-TTxx、about 55% of Ace-high DS、about 35% of double-pairs を attack shell に加えます。",
            "when": "BTN range が広く、SB の blocker / playability edge が増えるためです。",
            "examples": "AAxx / AKKx / AQQx / JJxx with Ace / Ace-high DS / double-pairs"
          },
          {
            "label": "cold call を消す",
            "tone": "fold",
            "range_read": "SB cold call は almost no-call として扱い、unless game is extremely soft 以外では default fold side へ置きます。",
            "when": "OOP multiway・range cap・BB squeeze reopen の3重苦があるためです。",
            "examples": "default response = 3-bet or fold"
          }
        ],
        "table_columns": [
          "spot",
          "主扱い",
          "補足"
        ],
        "table_rows": [
          [
            "SB cold call",
            "almost never",
            "PLO Genius blind article は SB call を明確に leak side へ置く"
          ],
          [
            "vs EP / MP / CO",
            "4.7% to 6.8% 3-bet",
            "tight, Ace-heavy, strongest DS rundown and double-pair only"
          ],
          [
            "vs BTN",
            "9.7% to about 10% 3-bet",
            "AKKx / AQQx / Ace-high DS / some JJxx-TTxx with Ace / more double-pairs"
          ]
        ],
        "source_note": "SB defend は『call almost never』を最上段に置かないと誤読しやすい seat です。そこから opener position に応じて 3-bet shell を太くするだけ、と考えるのが公開ソースに最も忠実です。",
        "collected_rows": [
          {
            "source_ref": "plogenius_blinds",
            "evidence_type": "blind_boundary",
            "range_read": "SB cold call は almost never。3-bet-or-fold が基本で、calling too wide は leak になりやすい。",
            "notes": "SB no-call rule の主ソース。"
          },
          {
            "source_ref": "plogenius_oop_3bet",
            "evidence_type": "oop_3bet_template",
            "range_read": "SB vs EP / MP / CO は 4.7%-6.8% 3-bet の tight Ace-heavy shell、vs BTN は 9.7%-10% まで widen する。",
            "notes": "SB opener-position dependent 3-bet band。"
          },
          {
            "source_ref": "plogenius_oop_3bet",
            "evidence_type": "ace_priority_rule",
            "range_read": "OOP 3-bet pots では Ace in hand が最重要 structural upgrade で、non-Ace hands は EP open 相手に about 1% しか 3-bet に残らない。",
            "notes": "SB の 3-bet が Ace-heavy に寄る理由。"
          }
        ]
      },
      "source_refs": [
        "plogenius_small_blind",
        "plogenius_blinds",
        "plogenius_oop_3bet"
      ]
    },
    "BB": {
      "label": "BB / defense-only seat",
      "role_label": "defense-only seat",
      "open_band": "n/a (unopened first-in row does not exist)",
      "versus_open_band": "widest defend seat; around 52% call and 13% 3-bet versus SB open",
      "source_seat": "blind-defense article plus IP 3-bet BB vs SB section",
      "position_summary": "BB は fixed first-in open row を持たず、preflop は defense-only seat として扱うのが自然です。",
      "caution_note": "BB は closes the action する一方、ほとんどの open 相手に OOP です。唯一 SB open 相手だけ position を持てるため、defend band が極端に広がります。",
      "overview": {
        "seat_trigger": "posted 1BB を守る必要はあるが、UTG / CO / BTN 相手のほとんどは OOP defense で、SB 相手だけは heads-up IP defense になります。",
        "open_identity": "BB は first-in open seat ではないため、前面は defend family に寄せます。",
        "adds_here": "vs SB では KK / QQ を全面防衛に回し、double-paired、connected hand の大半、5 以上の connected pair、ほぼ全ての suited Ace まで守備を広げます。",
        "still_avoid": "trips、unconnected tri-suit、deuce / trey heavy connected trash、tight UTG open に対する loose OOP flats。"
      },
      "at_a_glance": {
        "open_core": "n/a; BB is a defend seat",
        "position_add": "vs SB のみ heads-up IP になるため defend が大きく widen",
        "vs_open": "UTG には call under 14%、BTN には wider、SB には around 52% call + 13% 3-bet",
        "snap_fold": "trips / unconnected tri-suit / deuce-tray heavy weak connected hand / weak OOP flat tail"
      },
      "open_first_in": {
        "section_label": "BB の扱い",
        "public_range_read": "6-max では unopened pot が BB まで回ることはないため、BB に fixed first-in open row はありません。この panel では BB を open seat ではなく defend seat として表示します。",
        "table_columns": [
          "項目",
          "扱い",
          "補足"
        ],
        "table_rows": [
          [
            "First-in open",
            "n/a",
            "BB は unopened pot の first-in row を持たない"
          ],
          [
            "Main job",
            "defend",
            "posted blind を基準に、opener position に応じて call / 3-bet / fold を分ける"
          ],
          [
            "Special spot",
            "BB vs SB",
            "唯一、preflop defend しても postflop position を持てる blind battle"
          ]
        ],
        "source_note": "BB を無理に open chart として見せるより、defense seat だと front で明言する方が誤解がありません。",
        "collected_rows": [
          {
            "source_ref": "plogenius_blinds",
            "evidence_type": "blind_role_rule",
            "range_read": "BB は posted blind を守るために call frequency を持つ seat であり、SB とは defend structure が根本的に違う。",
            "notes": "BB role の基本説明。"
          }
        ]
      },
      "versus_open": {
        "section_label": "オープンに対する継続",
        "public_range_read": "BB は closes the action するため、SB よりずっと多く defend できます。ただし OOP defense は still selective で、真に大きく widen するのは BB vs SB です。公開記事の overlap は『UTG には call under 14%』『vs SB は call around 52% + 3-bet about 13%』『defend almost any suited Ace and most connected structures』に集約できます。",
        "range_groups": [
          {
            "label": "vs SB で広く defend",
            "tone": "attack",
            "items": [
              "3-bet all AAxx",
              "defend all KK and QQ, raising the best ones",
              "defend all double-paired hands",
              "defend most connected hands except deuce/tray-heavy ones",
              "defend most connected pairs five and higher",
              "defend almost any suited Ace"
            ]
          },
          {
            "label": "spot-dependent defense",
            "tone": "conditional",
            "items": [
              "UTG には call under 14%",
              "BTN 相手には SB より much wider",
              "BB vs SB では around 13% 3-bet shell",
              "Kings / Queens without Ace are flatter on BB vs SB"
            ]
          },
          {
            "label": "fold side",
            "tone": "fold",
            "items": [
              "trips",
              "unconnected tri-suit hands",
              "deuce / tray heavy weak connected hands",
              "tight opener 相手の loose OOP flat tail"
            ]
          }
        ],
        "action_bands": [
          {
            "label": "vs UTG",
            "tone": "conditional",
            "range_read": "BB defense は exist するが、call は under 14% で still selective です。",
            "when": "tight opener 相手に OOP で realization が悪く、low-stakes pool では無理な flat が rake で削られやすいためです。",
            "examples": "defend better suited / connected / premium structures only"
          },
          {
            "label": "vs BTN",
            "tone": "conditional",
            "range_read": "SB より多く cold call し、wider defend seat として機能します。",
            "when": "open range が広く closes action もするため、strong-not-premium class を flat side に回しやすいからです。",
            "examples": "wider suited Ace / connected hands / pair+connectivity"
          },
          {
            "label": "vs SB",
            "tone": "attack",
            "range_read": "コール約 52%・3-bet 約 13%。BB vs SB は、defend しても postflop で常にポジションを持てる唯一の blind battle です。",
            "when": "heads-up IP で equity realization が大幅に改善するためです。",
            "examples": "all KK/QQ defense / double-pairs / connected pairs 5+ / almost any suited Ace"
          }
        ],
        "table_columns": [
          "spot",
          "主扱い",
          "補足"
        ],
        "table_rows": [
          [
            "BB vs UTG",
            "call less than 14%",
            "tight opener 相手の OOP defense なので still selective"
          ],
          [
            "BB vs BTN",
            "wider than SB",
            "cold call を多く持てる defense seat"
          ],
          [
            "BB vs SB",
            "call around 52% / 3-bet about 13%",
            "唯一の heads-up IP blind defense; easiest blind battle"
          ]
        ],
        "source_note": "BB は one fixed chart ではなく、opener position で defend semantics が大きく変わります。だから front は『UTG tight / BTN wider / SB widest』の順で読めるようにしています。",
        "collected_rows": [
          {
            "source_ref": "plogenius_blinds",
            "evidence_type": "blind_frequency",
            "range_read": "BB vs SB ではコール約 52%・3-bet 約 13%。BB は defend しながらポジションを持てる唯一の blind battle だと説明する。",
            "notes": "BB widest defense spot の主ソース。"
          },
          {
            "source_ref": "plogenius_blinds",
            "evidence_type": "defense_categories",
            "range_read": "vs SB では KK / QQ を全面防衛に回し、double-paired、connected hand の大半、5 以上の connected pair、ほぼ全ての suited Ace を defend 側へ入れる。",
            "notes": "BB defend family の具体境界。"
          },
          {
            "source_ref": "plogenius_ip_3bet",
            "evidence_type": "bb_ip_3bet_template",
            "range_read": "BB vs SB の 3-bet は up to 13% で、all AAxx、about half AKKx / AQQx / Ace DS rundown、most DS double-paired hands が中心。",
            "notes": "BB attack shell の補強。"
          },
          {
            "source_ref": "plogenius_opening_ranges",
            "evidence_type": "utg_defense_boundary",
            "range_read": "UTG open に対して BB の call frequency は less than 14% と説明される。",
            "notes": "BB vs UTG upper boundary。"
          }
        ]
      },
      "source_refs": [
        "plogenius_blinds",
        "plogenius_ip_3bet",
        "plogenius_opening_ranges"
      ]
    }
  },
  "source_index": {
    "upswing_rfi_pdf": {
      "title": "Upswing Poker: Pot Limit Omaha Preflop Guide For Raising First In (RFI v4)",
      "short_label": "Upswing PDF",
      "url": "https://upswingpoker.com/wp-content/uploads/2020/04/PLO-Preflop-Guide-RFI-v4-UpswingPoker.pdf",
      "source_type": "PDF",
      "weight": "primary_solver_pdf"
    },
    "pokervip_6max_chart": {
      "title": "PokerVIP: 6-Max PLO Basic Starting Hand Chart",
      "short_label": "PokerVIP",
      "url": "https://www.pokervip.com/strategy-articles/pot-limit-omaha-plo/6-max-plo-basic-starting-hand-chart",
      "source_type": "HTML",
      "weight": "conservative_public_chart"
    },
    "plogenius_opening_ranges": {
      "title": "PLO Genius Blog: How Wide Can You Open Preflop in PLO?",
      "short_label": "PLO Genius Open",
      "url": "https://content-blog.plogenius.com/taking-a-closer-look-at-opening-ranges/",
      "source_type": "HTML",
      "weight": "primary_solver_article"
    },
    "plogenius_small_blind": {
      "title": "PLO Genius Blog: Navigating the Small Blind Preflop in Pot Limit Omaha",
      "short_label": "PLO Genius SB",
      "url": "https://content-blog.plogenius.com/taking-a-closer-look-at-small-blind/",
      "source_type": "HTML",
      "weight": "primary_solver_article"
    },
    "plogenius_blinds": {
      "title": "PLO Genius Blog: Cold Calling the Small Blind and the Big Blind",
      "short_label": "PLO Genius Blinds",
      "url": "https://content-blog.plogenius.com/coldcalling-in-sb-and-bb/",
      "source_type": "HTML",
      "weight": "primary_solver_article"
    },
    "plomastermind_calling_preflop": {
      "title": "PLO Mastermind: Calling Preflop - When Should You Cold-Call in PLO?",
      "short_label": "PLO Mastermind",
      "url": "https://plomastermind.com/calling-preflop/",
      "source_type": "HTML",
      "weight": "cold_call_article"
    },
    "plogenius_ip_3bet": {
      "title": "PLO Genius Blog: 3-Betting IP in PLO: Ranges, Logic, Adjustments",
      "short_label": "PLO Genius IP 3bet",
      "url": "https://content-blog.plogenius.com/3-betting-ip-in-plo-ranges-logic-adjustments/",
      "source_type": "HTML",
      "weight": "supporting_solver_article"
    },
    "plogenius_oop_3bet": {
      "title": "PLO Genius Blog: Out of Position 3-Bets in PLO: When and How to Apply Pressure",
      "short_label": "PLO Genius OOP 3bet",
      "url": "https://content-blog.plogenius.com/out-of-position-3-bets-in-plo-when-and-how-to-apply-pressure/",
      "source_type": "HTML",
      "weight": "supporting_solver_article"
    }
  },
  "verification": {
    "checked_on": "2026-04-18",
    "method": "リンク先 HTML と Upswing PDF を確認し、position 別の open_first_in / versus_open surface へ再分解して整形",
    "confirmed_source_refs": [
      "upswing_rfi_pdf",
      "pokervip_6max_chart",
      "plogenius_opening_ranges",
      "plogenius_small_blind",
      "plogenius_blinds",
      "plomastermind_calling_preflop",
      "plogenius_ip_3bet",
      "plogenius_oop_3bet"
    ]
  }
}
;

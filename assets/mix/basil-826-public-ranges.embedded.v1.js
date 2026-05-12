window.__BASIL_826_PUBLIC_RANGES_V1 = {
   "collection_notes" : [
      "2026-04-18 に ぞにきの公開 note 本文、記事埋め込みの #826ルールブック画像、FL826TD 有料 note の preview、PokerGuild のイベント告知ページを再確認して組み直しました。",
      "公開で確認できる exact frequency chart / combo table は未発見です。今回は source-backed な hand class を position ごとに core / 条件付き / まだ見送る帯へ分解しています。",
      "FL826TD は 8♣ / 2♣ / A♣ の singleton anchor、picture(KQJ) discard、A-high triple-club half-lock、3way sandwich risk を軸に整理しました。",
      "NL826SD は 1チェンジ参加、two-of-826 one-draw、single-anchor の役なしリスク、no-limit の chop pressure を軸に整理しました。",
      "standalone PDF / CSV の 826 レンジ表は公開範囲で未発見です。note 本文 HTML と検索導線も再確認しましたが、公開 authority は記事本文と rule image が中心でした。",
      "UTG / HJ / CO は paywalled preview が示す UTG-CO raise frame と整合します。BTN / SB は同じ公開ヒューリスティックから late-position に延長した practical baseline で、推定成分がやや強いです。"
   ],
   "dataset_id" : "basil_826_public_position_ranges_v2",
   "global_source_refs" : [
      "zoniki_overview_note",
      "zoniki_rulebook_image",
      "yamamoto_fl826_preview",
      "pokerguild_fl826_event"
   ],
   "position_order" : [
      "UTG",
      "HJ",
      "CO",
      "BTN",
      "SB"
   ],
   "scope" : {
      "defense_actor" : "BB",
      "game" : "basil_826_mix",
      "phase" : "before_first_draw",
      "position_button_meaning" : "6-max を前提にした UTG / HJ / CO / BTN / SB。BB は first-in open 行ではなく defense actor として open に対するコール帯を表示する。",
      "position_buttons" : [
         "UTG",
         "HJ",
         "CO",
         "BTN",
         "SB"
      ],
      "primary_views" : [
         "first_in_open",
         "bb_defense_vs_open"
      ],
      "reconstruction_method" : "ぞにきの公開 note 本文と埋め込みルールブック画像を主根拠にし、有料 note preview が示す UTG-CO raise / BB defense の枠組みで position ごとに practical range へ再構築",
      "variants" : [
         "FL826TD",
         "NL826SD"
      ]
   },
   "source_index" : {
      "pokerguild_fl826_event" : {
         "short_label" : "PokerGuild Event",
         "source_type" : "HTML",
         "title" : "PokerGuild: ☘【ぞにき考案ドローゲーム】FL 826 Triple Draw ☘",
         "url" : "https://archive.pokerguild.jp/tourneys/330039",
         "weight" : "supporting"
      },
      "yamamoto_fl826_preview" : {
         "short_label" : "FL826 Preview",
         "source_type" : "HTML",
         "title" : "山本重國: FL826TDプリドロー完全攻略",
         "url" : "https://note.com/rich_swan32/n/n65c7eeb16211",
         "weight" : "preview"
      },
      "zoniki_overview_note" : {
         "short_label" : "ぞにき note",
         "source_type" : "HTML",
         "title" : "ぞにき: [初心者向け]826(バジル)ポーカーの概要とゲームセオリー",
         "url" : "https://note.com/zoniki/n/n3143c1508eeb",
         "weight" : "primary"
      },
      "zoniki_rulebook_image" : {
         "short_label" : "Rule Image",
         "source_type" : "IMAGE",
         "title" : "#826ルールブック 埋め込み画像",
         "url" : "https://assets.st-note.com/img/1708459170656-IgXrX1Qtu8.jpg?width=1200",
         "weight" : "rules"
      }
   },
   "variant_order" : [
      "FL826TD",
      "NL826SD"
   ],
   "variants" : {
      "FL826TD" : {
         "label" : "FL826TD",
         "positions" : {
            "BTN" : {
               "at_a_glance" : {
                  "open_core" : "CO core + widest singleton anchor + more picture-rich engine。",
                  "position_add" : "selected 26x with blockers、weaker triple club、blocker-heavy single-anchor steal。",
                  "snap_fold" : "naked 26、non-club 6、role / blocker / picture のどれも薄い trash。",
                  "vs_complete" : "BB では widest blocker-heavy anchor と most supported catch hand を defend に回せる。"
               },
               "caution_note" : "BTN は preview の直接席外です。ここは public note の strong-card logic を late position に延長した baseline なので、exact chart ではありません。",
               "confidence_label" : "低め: late-position inference",
               "label" : "BTN",
               "open_complete" : {
                  "anchor_profile" : "late-position inference / BTN steal baseline",
                  "collected_rows" : [
                     {
                        "evidence_type" : "late_extension",
                        "notes" : "BTN practical baseline",
                        "range_read" : "anchor、picture、A高トリクラ、blocker 的な 8♣ / A♣ の強さを late steal に延長",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "authority_gap",
                        "notes" : "BTN は lower-confidence 表示",
                        "range_read" : "preview の公開範囲は UTG-CO までで BTN exact row は不明",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "BTN は CO よりさらに広く、widest singleton anchor、more picture-rich engine、selected 26x with blockers、weaker triple club までを steal 帯に入れる practical baseline です。",
                  "range_groups" : [
                     {
                        "items" : [
                           "CO core",
                           "widest singleton anchor",
                           "more picture-rich engine",
                           "broader supported 82x / 86x"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "selected 26x with blockers",
                           "weaker triple club",
                           "blocker-heavy 8♣ / A♣ steal"
                        ],
                        "label" : "BTNで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "naked 26",
                           "non-club 6",
                           "薄い garbage"
                        ],
                        "label" : "late seatでも切る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "BTN row は public note の anchor / picture / 3way risk を late steal に延長したものです。exact BTN chart は公開されていないため、source overlap が強い class だけを widen 側へ残しています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "CO core 全体 + widest singleton anchor + more picture-rich engine",
                        "BTN から標準オープン"
                     ],
                     [
                        "この位置で追加",
                        "selected 26x with blockers、weaker triple club、blocker-heavy 8♣ / A♣ steal",
                        "blind が overfold する時に practical"
                     ],
                     [
                        "まだ見送る",
                        "naked 26、non-club 6、role / blocker / picture のどれも薄い garbage",
                        "late seat でも無差別には開かない"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "selected 26x with blockers、weaker triple club、blocker-heavy 8♣ / A♣ steals。",
                  "open_identity" : "widest singleton anchor、widest anchor+picture、supported 82x / 86x、picture-heavy engine が主体。",
                  "seat_trigger" : "blind two seats だけが後ろに残る steal seat。",
                  "still_avoid" : "naked 26、非クラブ6単体、role も blocker も薄い pure trash。"
               },
               "position_summary" : "公開ソースに exact BTN row はありませんが、late steal 席として most singleton anchor、supported catch hand、picture-heavy engine をさらに広げる practical seat です。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image",
                  "yamamoto_fl826_preview"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "8♣QJ / 2♣KQ / A♣K♣Q♣ / 82x",
                        "label" : "安定 defend",
                        "range_read" : "premium anchor、anchor+picture、KQJ、A高トリクラ、強い82x は BTN 相手でも自然に defend します。",
                        "tone" : "attack",
                        "when" : "public note の strong-card overlap が濃い帯。"
                     },
                     {
                        "examples" : "8♣xy / weak triple club with blocker / 26x with club blocker",
                        "label" : "BTN相手で最大化",
                        "range_read" : "widest blocker-heavy anchor、most supported catch hand、more weak triple club、selected single-anchor start を追加します。",
                        "tone" : "conditional",
                        "when" : "steal 幅が最も広く、BB が close the action を持つ時。"
                     },
                     {
                        "examples" : "26 rainbow / lone 6x / no-blocker weak catch",
                        "label" : "ここは切る",
                        "range_read" : "naked 26、non-club 6、role / blocker が薄い catch hand は BTN 相手でも defend の外です。",
                        "tone" : "fold",
                        "when" : "late seat でも realization が足りない時。"
                     }
                  ],
                  "anchor_profile" : "late-position inference / BB defend vs BTN",
                  "collected_rows" : [
                     {
                        "evidence_type" : "late_extension",
                        "notes" : "BTN vs BB practical call row",
                        "range_read" : "8♣ / A♣ の blocker 性、picture、weak catch の危険を BTN steal / BB defend に延長",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "authority_gap",
                        "notes" : "信頼度は UTG-CO より低い",
                        "range_read" : "preview 公開範囲外のため BTN defend は late-position inference",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "BTN open に対する BB call は widest blocker-heavy anchor、most supported catch hand、more weak triple club、selected single-anchor start まで practical に増やします。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "BTN defend row も公開 exact chart ではありません。BB の close-the-action を加味して widens していますが、public note に反する裸 catch hand は切っています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "premium anchor / picture / A高トリクラ / 強い82x",
                        "そのまま defend"
                     ],
                     [
                        "この相手に増える",
                        "widest blocker-heavy anchor、most supported catch hand、more weak triple club、selected single-anchor start",
                        "BTN open の steal 幅に合わせて widen"
                     ],
                     [
                        "フォールド寄り",
                        "naked 26、non-club 6、role / blocker が薄い catch hand",
                        "BB でも底の garbage は残さない"
                     ]
                  ]
               }
            },
            "CO" : {
               "at_a_glance" : {
                  "open_core" : "UTG/HJ core + most live singleton anchor + broader supported 82x / 86x。",
                  "position_add" : "selected 26x with club support、blocker 付き weak triple club、picture-heavy steals。",
                  "snap_fold" : "裸26、非クラブ6単体、support の薄い weak triple club。",
                  "vs_complete" : "BB では picture-rich engine と club-backed 86x / 26x をかなり増やせる。"
               },
               "caution_note" : "CO は widen できるが、FL なので 3way で trapped になりやすい hand を無差別に入れるとすぐ逆噴射します。",
               "confidence_label" : "中程度: preview-backed の最後の open seat",
               "label" : "CO",
               "open_complete" : {
                  "anchor_profile" : "public-source reconstruction / widest preview-backed FL open seat",
                  "collected_rows" : [
                     {
                        "evidence_type" : "direct_heuristic",
                        "notes" : "CO widen の上限を決める",
                        "range_read" : "anchor、picture、A高トリクラが強く、26 と weak triple club は 3way で危険",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "position_frame",
                        "notes" : "CO を直接含む preview",
                        "range_read" : "UTG-CO raise 可否の ladder",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "CO は most live singleton anchor、broader supported 82x / 86x、selected 26x with club support、blocker 付き weak triple club まで practical に広げる seat です。",
                  "range_groups" : [
                     {
                        "items" : [
                           "UTG/HJ core",
                           "most live singleton anchor",
                           "broader supported 82x / 86x"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "selected 26x with club support",
                           "weaker triple club with blockers",
                           "picture-heavy non-anchor opens"
                        ],
                        "label" : "COで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "裸26",
                           "非クラブ6単体",
                           "support の薄い weak triple club"
                        ],
                        "label" : "まだ切る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "CO は preview が直接含む最後の open seat なので、public note の anchor / picture / 6価値 / 3way risk を少し緩めて widen しています。late steal 専用の極端な garbage はまだ入れていません。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "UTG/HJ core、most live singleton anchor、broader supported 82x / 86x",
                        "CO から標準オープン"
                     ],
                     [
                        "この位置で追加",
                        "selected 26x with club support、weaker triple club with blockers、picture-heavy non-anchor opens",
                        "blind が受け身なら practical に使う"
                     ],
                     [
                        "まだ見送る",
                        "裸26、非クラブ6単体、support の薄い weak triple club",
                        "FL の trapped risk が残る"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "selected 26x with club support、weaker triple club with blockers、picture-heavy non-anchor opens。",
                  "open_identity" : "most live singleton anchor、anchor+picture、picture3、supported 82x / 86x が open の主体。",
                  "seat_trigger" : "late seat に入り始めるが、まだ blind two seats から十分 punish される位置。",
                  "still_avoid" : "裸26、非クラブ6単体、quarter risk だけ高い weak catch hand。"
               },
               "position_summary" : "公開 preview が直接含む最後の raise seat です。single anchor と supported catch hand を一段広げつつも、裸26や弱い catch は残しません。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image",
                  "yamamoto_fl826_preview"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "8♣QJ / A♣K♣Q♣ / 82x with backup",
                        "label" : "しっかり守る帯",
                        "range_read" : "premium anchor、anchor+picture、KQJ、A高トリクラ、強い82x は CO 相手でもコールの主力です。",
                        "tone" : "attack",
                        "when" : "source overlap が最も大きい class。"
                     },
                     {
                        "examples" : "86x with club / 26x with club / blocker weak triple club",
                        "label" : "CO相手で広げる帯",
                        "range_read" : "picture-rich engine、club-backed 86x / 26x、selected weak triple club、blocker-heavy single anchor を practical に追加します。",
                        "tone" : "conditional",
                        "when" : "opener が明らかに late 化している時。"
                     },
                     {
                        "examples" : "26 rainbow / lone 6x / naked catch",
                        "label" : "依然として切る帯",
                        "range_read" : "裸26、非クラブ6単体、support のない catch hand は defend の下端に入れません。",
                        "tone" : "fold",
                        "when" : "BB でも post-draw realization が悪過ぎる時。"
                     }
                  ],
                  "anchor_profile" : "public-source reconstruction / BB defend vs CO",
                  "collected_rows" : [
                     {
                        "evidence_type" : "strength_axis",
                        "notes" : "CO defend の widen / trim 軸",
                        "range_read" : "anchor と picture は強く、26 / weak triple club は trapped になると脆い",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "bb_defense_frame",
                        "notes" : "BB call section の外形",
                        "range_read" : "BB defense keep の ladder が別に存在する",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "CO open に対する BB call は picture-rich engine、broader club-backed 86x / 26x、selected weak triple club、blocker-heavy single anchor まで practical に増やします。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "CO 相手の BB defend は public exact chart がないため、anchor / picture / weak catch の価値差を基準に widen しています。UTG/HJ よりは広いが、無条件で 26 を守る row ではありません。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "premium anchor / picture / A高トリクラ / 強い82x",
                        "常時 defend"
                     ],
                     [
                        "この相手に増える",
                        "broader picture engine、club-backed 86x / 26x、selected weak triple club、blocker-heavy single anchor",
                        "CO open の widen に合わせて追加"
                     ],
                     [
                        "フォールド寄り",
                        "裸26、非クラブ6単体、support のない catch hand",
                        "BB でも底辺は守り過ぎない"
                     ]
                  ]
               }
            },
            "HJ" : {
               "at_a_glance" : {
                  "open_core" : "UTG core 全体 + single anchor の単体参加が増える。",
                  "position_add" : "86x / 26x は club or picture support が見える時だけ足す。",
                  "snap_fold" : "裸26、非クラブ6単体、弱い triple club の投げ込み。",
                  "vs_complete" : "BB では UTG相手より一段広く、single anchor と supported 82/86 を残せる。"
               },
               "caution_note" : "公開ソースは HJ cutoffs を直接書き下ろしていません。HJ は UTG の tight core と CO の widen をつなぐ practical row です。",
               "confidence_label" : "中程度: UTG-CO frame の中間再構成",
               "label" : "HJ",
               "open_complete" : {
                  "anchor_profile" : "public-source reconstruction / bridge seat",
                  "collected_rows" : [
                     {
                        "evidence_type" : "direct_heuristic",
                        "notes" : "HJ widen と cut line を同時に与える",
                        "range_read" : "TD では anchor 単体でも強く、86 / 26 は受け身になりやすい catch hand",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "position_frame",
                        "notes" : "HJ を独立 seat として扱う根拠",
                        "range_read" : "UTG-CO raise ladder の存在",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "HJ は UTG の core を保ったまま、most singleton anchor、supported 82x、club-backed 86x / 26x、picture-rich two-picture starts を少しだけ足す席です。",
                  "range_groups" : [
                     {
                        "items" : [
                           "UTG core",
                           "most singleton 8♣ / 2♣ / A♣",
                           "supported 82x"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "club-backed 86x",
                           "club-backed 26x",
                           "picture-rich two-picture starts"
                        ],
                        "label" : "HJで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "裸26",
                           "非クラブ6単体",
                           "weak triple club"
                        ],
                        "label" : "まだ見送る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "strong-card 論理そのものは UTG と同じですが、preview が UTG-CO の positional ladder を示すため、HJ では single anchor と supported catch hand を一段だけ widen しています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "UTG core 全体",
                        "そのまま継続"
                     ],
                     [
                        "この位置で追加",
                        "most singleton 8♣ / 2♣ / A♣、supported 82x、club-backed 86x / 26x、two-picture engine",
                        "HJ から practical に widen"
                     ],
                     [
                        "まだ見送る",
                        "裸26、非クラブ6単体、弱い triple club",
                        "まだ multiway 被弾が重い"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "most singleton 8♣ / 2♣ / A♣、supported 82x、club-backed 86x / 26x、picture-rich two-picture starts。",
                  "open_identity" : "UTG core を残しながら、single anchor の単体参加と supported catch hand を少しだけ広げる席。",
                  "seat_trigger" : "まだ steal ではないが、UTG よりは punish されにくい中間席。",
                  "still_avoid" : "裸26、非クラブ6単体、弱い triple club を無差別に足すこと。"
               },
               "position_summary" : "UTG shell を保ちつつ、single anchor の単体参加や supported 86x / 26x を少し増やせる遷移席です。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image",
                  "yamamoto_fl826_preview"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "8♣QJ / 2♣KQ / A♣K♣Q♣ / 82x",
                        "label" : "基本 defend",
                        "range_read" : "premium anchor、anchor+picture、KQJ、A高トリクラ、強い82x は HJ open 相手でも最優先で残します。",
                        "tone" : "attack",
                        "when" : "公開 note が強いと明示した class そのもの。"
                     },
                     {
                        "examples" : "8♣xy / 86x with picture / 26x with club",
                        "label" : "HJ相手でだけ増やす",
                        "range_read" : "single anchor 単体、supported 82x / 86x、club-backed 26x、blocker のある weak triple club を一段だけ増やします。",
                        "tone" : "conditional",
                        "when" : "UTG より opener が広いと読める時。"
                     },
                     {
                        "examples" : "26 rainbow / lone 6x / weak triple club no blocker",
                        "label" : "依然として切る帯",
                        "range_read" : "裸26、非クラブ6単体、support の薄い weak triple club はまだ defend 過多です。",
                        "tone" : "fold",
                        "when" : "open が中間席でも reverse implied odds が消えない時。"
                     }
                  ],
                  "anchor_profile" : "public-source reconstruction / BB defend vs HJ",
                  "collected_rows" : [
                     {
                        "evidence_type" : "strength_axis",
                        "notes" : "BB defend の widen / trim 軸",
                        "range_read" : "anchor 単体の強さと、26 / weak triple club の苦しさ",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "bb_defense_frame",
                        "notes" : "call row の外形",
                        "range_read" : "BBディフェンスでキープできるかという枠組み",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "HJ open に対する BB call は UTG 相手より一段広く、single anchor、supported 82x / 86x、club-backed 26x を少し増やせます。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "public note は BB defend exact rows を出しませんが、strong anchor と weak catch hand の差は明確です。HJ 相手では UTG より一段だけ widen させています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "UTG 相手で残す premium anchor / picture / A高トリクラ / 強い82x",
                        "そのまま defend"
                     ],
                     [
                        "この相手に増える",
                        "more singleton anchor、supported 82x / 86x、club-backed 26x、selected weak triple club with blockers",
                        "HJ open の widen に合わせて追加"
                     ],
                     [
                        "フォールド寄り",
                        "裸26、非クラブ6単体、support の薄い weak triple club",
                        "まだ BB でも残し過ぎない"
                     ]
                  ]
               }
            },
            "SB" : {
               "at_a_glance" : {
                  "open_core" : "premium anchor+picture、premium club lock、supported 86x、selected 26x with support。",
                  "position_add" : "selected blocker-heavy single-anchor steal、selected weaker club-backed catch hand。",
                  "snap_fold" : "naked 26、non-club 6、no-role blind-battle trash。",
                  "vs_complete" : "BB defend は SB open 相手で最も広くなり、single-anchor blocker や thin catch も一部残せる。"
               },
               "caution_note" : "ただし FL なので、BB が強く defend してくる相手なら裸26や non-club 6 を増やし過ぎると簡単に損失化します。",
               "confidence_label" : "低め: heads-up inference",
               "label" : "SB",
               "open_complete" : {
                  "anchor_profile" : "heads-up inference / SB steal baseline",
                  "collected_rows" : [
                     {
                        "evidence_type" : "heads_up_extension",
                        "notes" : "SB practical open row",
                        "range_read" : "anchor と A高トリクラの half-lock 性、8♣ / A♣ の blocker 性を blind battle に延長",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "authority_gap",
                        "notes" : "SB は lower-confidence 表示",
                        "range_read" : "public preview は UTG-CO を直接示し、SB exact row は公開されていない",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "SB は premium anchor+picture、premium club lock、supported 86x、selected 26x with support を土台に、selected blocker-heavy single-anchor steal と weaker club-backed catch まで practical に広げます。",
                  "range_groups" : [
                     {
                        "items" : [
                           "premium anchor + picture",
                           "premium club lock",
                           "supported 86x",
                           "selected 26x with support"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "selected blocker-heavy single-anchor steal",
                           "selected weaker club-backed catch hand"
                        ],
                        "label" : "SBで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "naked 26",
                           "non-club 6",
                           "薄い blind-battle trash"
                        ],
                        "label" : "blind battleでも切る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "SB row は heads-up realization の高さを使った practical 延長です。anchor と club lock を強く押し出す一方、public note に反する裸 catch hand は維持していません。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "premium anchor+picture、premium club lock、supported 86x、selected 26x with support",
                        "SB から標準オープン"
                     ],
                     [
                        "この位置で追加",
                        "selected blocker-heavy single-anchor steal、selected weaker club-backed catch hand",
                        "BB が受け身なら practical に使う"
                     ],
                     [
                        "まだ見送る",
                        "naked 26、non-club 6、role / blocker のない blind-battle trash",
                        "heads-up でも下限は切る"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "selected blocker-heavy single-anchor steal、selected weaker club-backed catch hand。",
                  "open_identity" : "premium anchor+picture、premium club lock、supported 86x、selected 26x with support が主体。",
                  "seat_trigger" : "heads-up 前提が最も強い blind battle seat。",
                  "still_avoid" : "naked 26、non-club 6、role も blocker もない blind-battle trash。"
               },
               "position_summary" : "SB は BB と heads-up になりやすいため、premium anchor と club lock の realization が最も高く、selected catch hand まで practical に開ける席です。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image",
                  "yamamoto_fl826_preview"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "8♣QJ / A♣K♣Q♣ / 82x",
                        "label" : "安定 defend",
                        "range_read" : "premium anchor、anchor+picture、KQJ、A高トリクラ、強い82x は SB open 相手でも最優先で残します。",
                        "tone" : "attack",
                        "when" : "source overlap が最も濃い帯。"
                     },
                     {
                        "examples" : "8♣xy / A♣xy / 86x with support / thin club-backed catch",
                        "label" : "SB相手で最大化",
                        "range_read" : "most live singleton anchor、selected single-anchor blocker、selected thin club-backed catch hand、supported 86x / 26x を practical に追加します。",
                        "tone" : "conditional",
                        "when" : "blind battle で opener が最も広い時。"
                     },
                     {
                        "examples" : "26 rainbow / lone 6x / dead trash",
                        "label" : "依然として切る帯",
                        "range_read" : "naked 26、non-club 6、no-role blind-battle trash は SB 相手でも defend 過多です。",
                        "tone" : "fold",
                        "when" : "heads-up でも role か blocker のどちらも見えない時。"
                     }
                  ],
                  "anchor_profile" : "heads-up inference / BB defend vs SB",
                  "collected_rows" : [
                     {
                        "evidence_type" : "heads_up_extension",
                        "notes" : "BB defend vs SB の practical frame",
                        "range_read" : "anchor の realization と blocker 性を blind battle 実戦に延長",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "authority_gap",
                        "notes" : "lower-confidence 表示",
                        "range_read" : "SB exact defend row は preview の公開範囲外",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "SB open に対する BB call は FL826TD の中で最も広く、most live singleton anchor、selected single-anchor blocker、selected thin club-backed catch hand まで practical に defend します。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "SB vs BB も public exact chart ではありません。blind battle で widens していますが、public note が危険とする裸 catch hand は守り過ぎない row に留めています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "premium anchor / picture / A高トリクラ / 強い82x",
                        "安定 defend"
                     ],
                     [
                        "この相手に増える",
                        "most live singleton anchor、selected single-anchor blocker、selected thin club-backed catch hand、supported 86x / 26x",
                        "SB steal 幅に対して practical に追加"
                     ],
                     [
                        "フォールド寄り",
                        "naked 26、non-club 6、no-role blind-battle trash",
                        "heads-up でも下限は守り過ぎない"
                     ]
                  ]
               }
            },
            "UTG" : {
               "at_a_glance" : {
                  "open_core" : "8♣ / 2♣ / A♣ を含む premium anchor、anchor+picture、KQJ、A高トリクラ、82x 上位。",
                  "position_add" : "86x は club or picture backup がある時だけ足し、26x はほぼ見送ります。",
                  "snap_fold" : "非クラブ6単体、裸86 / 26、弱い triple club、3wayで quarter されやすい catch hand。",
                  "vs_complete" : "BB で UTG open を受けた時は premium anchor、anchor+picture、KQJ、A高トリクラ、強い82x が残ります。"
               },
               "caution_note" : "公開ソースが直接示すのは hand の価値軸であって exact combo 境界ではありません。UTG row はその交差部分だけで組んだ practical baseline です。",
               "confidence_label" : "中程度: public note + preview-backed UTG-CO frame",
               "label" : "UTG",
               "open_complete" : {
                  "anchor_profile" : "public-source reconstruction / tightest FL seat",
                  "collected_rows" : [
                     {
                        "evidence_type" : "direct_heuristic",
                        "notes" : "UTG open core の主根拠",
                        "range_read" : "TD では 8♣ / 2♣ / A♣ が1枚あるだけでも強く、anchor + picture と picture3 が強い",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "position_frame",
                        "notes" : "UTG-CO frame を補強",
                        "range_read" : "UTG-CO でレイズ可能か、BBディフェンスでキープできるかを基準にした FL826TD predraw ladder が存在する",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "UTG は 8♣ / 2♣ / A♣ の single anchor、anchor+picture、picture3、A高トリクラ、強い82x を中核にし、86x は club or picture backup 付きまでに止める席です。",
                  "range_groups" : [
                     {
                        "items" : [
                           "8♣ / 2♣ / A♣ strong anchor",
                           "anchor + picture",
                           "KQJ / picture3",
                           "A-high triple club",
                           "82x with club or picture backup"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "8♣A♣x / 8♣2♣x",
                           "club-backed 86x",
                           "picture-backed 86x"
                        ],
                        "label" : "条件付きで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "裸26",
                           "非クラブ6単体",
                           "weak triple club",
                           "club も picture も薄い catch hand"
                        ],
                        "label" : "UTGではまだ出さない",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "ぞにき記事は TD で 8♣ / 2♣ / A♣ が単体でも強いこと、picture の価値が高いこと、6の価値は SD より低いこと、26 と weak triple club は 3way で苦しいことを明示しています。preview は UTG-CO raise frame の存在だけを補強します。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "8♣ / 2♣ / A♣ を含む strong anchor、anchor+picture、KQJ、A高トリクラ、82x 上位",
                        "UTG から常時オープン"
                     ],
                     [
                        "条件付きで足す",
                        "8♣A♣x / 8♣2♣x、club-backed 86x、picture-backed 86x",
                        "multiway が重くなり過ぎない時だけ"
                     ],
                     [
                        "まだ見送る",
                        "裸26、非クラブ6単体、weak triple club、picture なしの catch hand",
                        "reverse implied odds と 3way risk が強過ぎる"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "8♣A♣x / 8♣2♣x の half-lock 寄り double-club と、club or picture backup 付き 86x まで。",
                  "open_identity" : "single club anchor + picture、picture3、A-high triple club、強い82x が open の軸です。",
                  "seat_trigger" : "後ろに4人残り、3way sandwich risk と quarter risk が最も重い席。",
                  "still_avoid" : "非クラブ6単体、裸26、弱い triple club、picture も club も薄い catch hand。"
               },
               "position_summary" : "最も締める席です。8♣ / 2♣ / A♣、anchor+picture、picture3、A高トリクラ、強い82系が open の主軸になります。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image",
                  "yamamoto_fl826_preview"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "8♣QJ / 2♣KQ / A♣K♣Q♣ / 82x with backup",
                        "label" : "素直にコールする帯",
                        "range_read" : "premium anchor、anchor+picture、KQJ、A高トリクラ、強い82x は UTG open に対して BB defend の核です。",
                        "tone" : "attack",
                        "when" : "公開記事の strong-card 論理をそのまま使える場面。"
                     },
                     {
                        "examples" : "8♣6x with picture / A♣6x with club backup",
                        "label" : "close the action でだけ残す",
                        "range_read" : "86x は club or picture backup がある時だけ残し、blocker-heavy 8♣ / A♣ start も BB だからこそ一部 keep します。",
                        "tone" : "conditional",
                        "when" : "後ろから squeeze されない BB 固有の条件がある時。"
                     },
                     {
                        "examples" : "26 rainbow / weak triple club / lone 6x catch",
                        "label" : "UTG相手には落とす",
                        "range_read" : "裸26、弱い triple club、非クラブ6単体は reverse implied odds が強過ぎるため defend の外へ置きます。",
                        "tone" : "fold",
                        "when" : "相手の open が最も強い UTG 帯の時。"
                     }
                  ],
                  "anchor_profile" : "public-source reconstruction / BB defend vs UTG",
                  "collected_rows" : [
                     {
                        "evidence_type" : "direct_heuristic",
                        "notes" : "BB defend の残す帯 / 切る帯の主根拠",
                        "range_read" : "26 と weak triple club は 3way で苦しく、8♣ / A♣ は blocker と scoop chance を持つ",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "position_frame",
                        "notes" : "BB call section の枠組み",
                        "range_read" : "BBディフェンスでキープできるか、という public preview の明示",
                        "source_ref" : "yamamoto_fl826_preview"
                     }
                  ],
                  "public_range_read" : "UTG open に対する BB call は premium anchor、anchor+picture、KQJ、A高トリクラ、強い82x が中心で、裸26 と弱い catch hand はかなり落ちます。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "preview が BB defense の枝を示し、ぞにき記事が premium anchor、picture、A高トリクラ、26 と weak triple club の危険を与えます。BB row はその overlap だけを defend 帯にしています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "premium club anchor、anchor+picture、KQJ、A高トリクラ、82x 上位",
                        "標準 defend 帯"
                     ],
                     [
                        "条件付きで残す",
                        "club-backed 86x、blocker-heavy 8♣ / A♣ start",
                        "close the action の恩恵がある時だけ"
                     ],
                     [
                        "フォールド寄り",
                        "裸26、weak triple club、非クラブ6単体",
                        "sandwich / quarter risk が大きい"
                     ]
                  ]
               }
            }
         },
         "variant_summary" : "3回の draw と picture discard があるため、8♣ / 2♣ / A♣ の single anchor と picture engine の価値が高い variant です。",
         "variant_warning" : "86 と 26 は catch hand として残る一方、非クラブ6や weak triple club は multiway で大きく痛みやすく、3way sandwich risk を常に意識します。"
      },
      "NL826SD" : {
         "label" : "NL826SD",
         "positions" : {
            "BTN" : {
               "at_a_glance" : {
                  "open_core" : "CO core + widest one-change numeric / club core + safest blocker-heavy pressure hand。",
                  "position_add" : "broader blocker-driven two-of-826 one-draw、selected single-anchor + structure open。",
                  "snap_fold" : "single anchor only、multi-change start、no-role steal garbage。",
                  "vs_complete" : "BB では widest one-change and blocker-heavy pressure hand、selected thin pressure keep まで defend に回せる。"
               },
               "caution_note" : "ただし BTN でも naked single anchor は依然弱く、club / blocker / structure が乗らない hand は open / call の主軸にしません。",
               "confidence_label" : "低め: late SD steal inference",
               "label" : "BTN",
               "open_complete" : {
                  "anchor_profile" : "late SD steal inference / BTN",
                  "collected_rows" : [
                     {
                        "evidence_type" : "chop_pressure",
                        "notes" : "BTN pressure add",
                        "range_read" : "片側確保からの強いベッティングが利益的",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "BTNでも naked anchor を切る",
                        "range_read" : "single anchor の相対価値低下",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "BTN は widest one-change numeric / club core、safest blocker-heavy pressure hand、broader blocker-driven two-of-826 one-draw、selected single-anchor + structure open を practical に採ります。",
                  "range_groups" : [
                     {
                        "items" : [
                           "CO core",
                           "widest one-change numeric / club core",
                           "safest blocker-heavy pressure hand"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "broader blocker-driven two-of-826 one-draw",
                           "selected single-anchor + structure open"
                        ],
                        "label" : "BTNで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "single anchor only",
                           "multi-change start",
                           "no-role steal garbage"
                        ],
                        "label" : "まだ切る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "BTN row は public note の one-change priority と no-limit chop pressure を late steal に延長したものです。structure と blocker がある single-anchor 派生だけを部分採用し、naked anchor は依然 cut しています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "CO core 全体 + widest one-change numeric / club core + safest blocker-heavy pressure hand",
                        "BTN から標準オープン"
                     ],
                     [
                        "この位置で追加",
                        "broader blocker-driven two-of-826 one-draw、selected single-anchor + structure open",
                        "steal seat として practical に追加"
                     ],
                     [
                        "まだ見送る",
                        "single anchor only、multi-change start、no-role steal garbage",
                        "late seatでも切る"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "broader blocker-driven two-of-826 one-draw、selected single-anchor + structure open。",
                  "open_identity" : "widest one-change core と blocker-heavy pressure hand が主体。",
                  "seat_trigger" : "blind two seats だけが後ろに残る steal seat。",
                  "still_avoid" : "single anchor only、multi-change start、no-role steal garbage。"
               },
               "position_summary" : "BTN は CO よりさらに late で、widest one-change core、safest blocker-heavy pressure hand、broader blocker-driven two-of-826 one-draw、selected single-anchor + structure open を practical に使える席です。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "82x one-change / A-high triple club / premium two-of-826",
                        "label" : "安定 defend",
                        "range_read" : "one-change / half-lock / best two-of-826 one-draw は BTN 相手でも守りの核です。",
                        "tone" : "attack",
                        "when" : "公開 note の one-change / half-lock logic に一致する時。"
                     },
                     {
                        "examples" : "blocker-heavy 86x / thin pressure keep / two-of-826 with blocker",
                        "label" : "BTN相手で最大化",
                        "range_read" : "widest one-change and blocker-heavy pressure hand、selected thin pressure keep、broader two-of-826 with blockers を practical に追加します。",
                        "tone" : "conditional",
                        "when" : "BTN が最も広い steal seatで、BB が close the action を持つ時。"
                     },
                     {
                        "examples" : "8♣xy only / no-role start",
                        "label" : "まだ切る",
                        "range_read" : "single anchor only、multi-change start、no-role steal garbage は BTN 相手でも defend の外です。",
                        "tone" : "fold",
                        "when" : "role か pressure のどちらも見えない時。"
                     }
                  ],
                  "anchor_profile" : "late SD steal inference / BB defend vs BTN",
                  "collected_rows" : [
                     {
                        "evidence_type" : "chop_pressure",
                        "notes" : "BTN defend widen",
                        "range_read" : "ノーリミットで marginal chop hand を降ろす発想",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "まだ切る帯",
                        "range_read" : "single strong card の価値低下",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "BTN open に対する BB call は widest one-change and blocker-heavy pressure hand、selected thin pressure keep、broader two-of-826 with blockers まで practical に増やせます。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "BTN defend は late steal 最大化の row ですが、中心はなお one-change と blocker pressure です。naked anchor は BB でも主軸化しません。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "one-change / half-lock / best two-of-826 one-draw",
                        "安定 defend"
                     ],
                     [
                        "この相手に増える",
                        "widest one-change and blocker-heavy pressure hand、selected thin pressure keep、broader two-of-826 with blockers",
                        "BTN steal に対して最大化"
                     ],
                     [
                        "フォールド寄り",
                        "single anchor only、multi-change start、no-role steal garbage",
                        "BB でも下限は cut"
                     ]
                  ]
               }
            },
            "CO" : {
               "at_a_glance" : {
                  "open_core" : "HJ core + more one-change numeric / club core + stable 82x half-lock。",
                  "position_add" : "broader two-of-826 one-draw、selected single-anchor + structure hand、more chop-pressure hand。",
                  "snap_fold" : "single anchor only、multi-change start、pure no-role risk hand。",
                  "vs_complete" : "BB では blocker-heavy one-change numeric / club core と selected single-anchor + structure hand を増やせる。"
               },
               "caution_note" : "それでも naked single anchor は依然弱く、club / blocker / structure が付かない限り open の主軸にはしません。",
               "confidence_label" : "低〜中: late SD practical baseline",
               "label" : "CO",
               "open_complete" : {
                  "anchor_profile" : "late SD practical baseline / CO",
                  "collected_rows" : [
                     {
                        "evidence_type" : "chop_pressure",
                        "notes" : "CO late-seat add の根拠",
                        "range_read" : "SD では片側確保からの強いベッティングで chop hand を降ろすことが利益的",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "CO でもまだ切る帯を残す",
                        "range_read" : "single anchor の価値は TD より低い",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "CO は more one-change numeric / club core、more stable 82x half-lock、broader two-of-826 one-draw、selected single-anchor + structure hand、more chop-pressure hand を practical に足す seat です。",
                  "range_groups" : [
                     {
                        "items" : [
                           "HJ core",
                           "more one-change numeric / club core",
                           "stable 82x half-lock"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "broader two-of-826 one-draw",
                           "selected single-anchor + structure hand",
                           "more chop-pressure hand"
                        ],
                        "label" : "COで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "single anchor only",
                           "multi-change start",
                           "pure no-role risk hand"
                        ],
                        "label" : "まだ切る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "CO では no-limit の chop pressure を活かせるため structure 付きの thin hand を少し増やしますが、public note に反する naked anchor は切り続けます。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "HJ core 全体 + more one-change numeric / club core + stable 82x half-lock",
                        "CO から標準オープン"
                     ],
                     [
                        "この位置で追加",
                        "broader two-of-826 one-draw、selected single-anchor + structure hand、more chop-pressure hand",
                        "late seat として practical に追加"
                     ],
                     [
                        "まだ見送る",
                        "single anchor only、multi-change start、pure no-role risk hand",
                        "1ドロー miss をまだ嫌う"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "broader two-of-826 one-draw、selected single-anchor + structure hand、more chop-pressure hand。",
                  "open_identity" : "one-change numeric / club core と stable 82x half-lock が主体。",
                  "seat_trigger" : "steal に入り始める late seat。",
                  "still_avoid" : "single anchor only、multi-change start、pure no-role risk hand。"
               },
               "position_summary" : "CO は one-change core を保ちながら、more one-change numeric / club core、more stable 82x half-lock、broader two-of-826 one-draw、selected single-anchor + structure hand を practical に足せる seat です。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "82x one-change / A-high triple club / premium two-of-826",
                        "label" : "安定 defend",
                        "range_read" : "one-change / half-lock / best two-of-826 one-draw は CO 相手でも中心です。",
                        "tone" : "attack",
                        "when" : "公開 note の one-change / half-lock 論理にそのまま乗る時。"
                     },
                     {
                        "examples" : "blocker 86x one-change / single-anchor + structure",
                        "label" : "CO相手で増やす",
                        "range_read" : "blocker-heavy one-change numeric / club core、selected single-anchor + structure hand、broader two-of-826 with blockers を practical に追加します。",
                        "tone" : "conditional",
                        "when" : "late-seat pressureを BB が受け止める時。"
                     },
                     {
                        "examples" : "8♣xy only / 2♣xy only / no-role start",
                        "label" : "まだ切る",
                        "range_read" : "single anchor only、multi-change start、pure no-role risk hand は CO 相手でも残し過ぎません。",
                        "tone" : "fold",
                        "when" : "structure と blocker の両方が弱い時。"
                     }
                  ],
                  "anchor_profile" : "late SD practical baseline / BB defend vs CO",
                  "collected_rows" : [
                     {
                        "evidence_type" : "chop_pressure",
                        "notes" : "late defend widen の根拠",
                        "range_read" : "片側確保からのノーリミット pressure",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "まだ切る帯",
                        "range_read" : "single anchor は SD で弱くなりやすい",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "CO open に対する BB call は blocker-heavy one-change numeric / club core、selected single-anchor + structure hand、broader two-of-826 one-draw with blockers を practical に足せます。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "CO defend は late-position pressure を使って少し widen しますが、主役はあくまで one-change と half-lock です。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "one-change / half-lock / best two-of-826 one-draw",
                        "安定 defend"
                     ],
                     [
                        "この相手に増える",
                        "blocker-heavy one-change numeric / club core、selected single-anchor + structure hand、broader two-of-826 with blockers",
                        "CO open の late 化に応じて追加"
                     ],
                     [
                        "フォールド寄り",
                        "single anchor only、multi-change start、pure no-role risk hand",
                        "BB でも下限は守り過ぎない"
                     ]
                  ]
               }
            },
            "HJ" : {
               "at_a_glance" : {
                  "open_core" : "UTG core + broader one-change club / numeric core。",
                  "position_add" : "more two-of-826 one-draw、more blocker-heavy club core、selected chop-pressure hand。",
                  "snap_fold" : "single anchor only、multi-change start、role-miss hand。",
                  "vs_complete" : "BB では broader two-of-826 one-draw と broader one-change club core を増やせる。"
               },
               "caution_note" : "それでも naked single anchor は SD ではまだ弱く、HJ でも open / call の土台にはしません。",
               "confidence_label" : "低〜中: one-change core の中間再構成",
               "label" : "HJ",
               "open_complete" : {
                  "anchor_profile" : "public-source reconstruction / bridge SD seat",
                  "collected_rows" : [
                     {
                        "evidence_type" : "one_change_priority",
                        "notes" : "HJ row の軸",
                        "range_read" : "SD では 1チェンジ参加が大切",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "two_of_826_value",
                        "notes" : "premium widen class",
                        "range_read" : "two-of-826 one-draw は hard to finish でも完成時の半分確保力が高い",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "HJ は UTG core を保ったまま、broader one-change club / numeric core、more two-of-826 one-draw、more blocker-heavy club core、selected chop-pressure hand を一段足す席です。",
                  "range_groups" : [
                     {
                        "items" : [
                           "UTG core",
                           "broader one-change club / numeric core"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "more two-of-826 one-draw",
                           "more blocker-heavy club core",
                           "selected chop-pressure hand"
                        ],
                        "label" : "HJで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "single anchor only",
                           "multi-change start",
                           "no-role risk hand"
                        ],
                        "label" : "まだ切る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "HJ でも最優先は one-change です。widen するのは premium one-draw と blocker を持つ class に限り、single anchor only はなお切っています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "UTG core 全体 + broader one-change club / numeric core",
                        "HJ から標準オープン"
                     ],
                     [
                        "この位置で追加",
                        "more two-of-826 one-draw、more blocker-heavy club core、selected chop-pressure hand",
                        "HJ widen として practical"
                     ],
                     [
                        "まだ見送る",
                        "single anchor only、multi-change start、no-role risk hand",
                        "SD なので依然 cut"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "more two-of-826 one-draw、more blocker-heavy club core、selected chop-pressure hand。",
                  "open_identity" : "UTG core を残しつつ broader one-change club / numeric core を足す seat。",
                  "seat_trigger" : "まだ steal ではないが、UTG よりは one-change widen を許しやすい席。",
                  "still_avoid" : "single anchor only、multi-change start、no-role risk hand。"
               },
               "position_summary" : "UTG の one-change core を保ちつつ、broader one-change club core、broader 82x / 86x / 26x、more two-of-826 one-draw を一段足せる席です。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "82x one-change / A-high triple club / premium two-of-826",
                        "label" : "基本 defend",
                        "range_read" : "one-change / half-lock / best two-of-826 one-draw は HJ 相手でも自然に残します。",
                        "tone" : "attack",
                        "when" : "公開 note の one-change priority を満たす時。"
                     },
                     {
                        "examples" : "thin two-of-826 / blocker club shell",
                        "label" : "HJ相手で足す",
                        "range_read" : "broader two-of-826 one-draw、broader one-change club core、selected blocker-heavy club shell を practical に追加します。",
                        "tone" : "conditional",
                        "when" : "UTG より opener が広い時。"
                     },
                     {
                        "examples" : "8♣xy only / no-role start",
                        "label" : "依然 cut",
                        "range_read" : "single anchor only、multi-change start、naked role-miss hand は HJ 相手でも defend の外です。",
                        "tone" : "fold",
                        "when" : "1ドロー miss がまだ痛い時。"
                     }
                  ],
                  "anchor_profile" : "public-source reconstruction / BB defend vs HJ in SD",
                  "collected_rows" : [
                     {
                        "evidence_type" : "one_change_priority",
                        "notes" : "BB defend core",
                        "range_read" : "1チェンジ参加が大切",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "まだ切る帯",
                        "range_read" : "single strong card の価値は TD より低い",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "HJ open に対する BB call は UTG 相手の core を維持しつつ、broader two-of-826 one-draw、broader one-change club core、selected blocker-heavy club shell を追加します。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "HJ defend も one-change と half-lock が主役です。public note が弱いとする single anchor only は BB でも守り過ぎない row にしています。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "UTG 相手で残す one-change / half-lock / best two-of-826 one-draw",
                        "そのまま defend"
                     ],
                     [
                        "この相手に増える",
                        "broader two-of-826 one-draw、broader one-change club core、selected blocker-heavy club shell",
                        "HJ open の widen に応じて追加"
                     ],
                     [
                        "フォールド寄り",
                        "single anchor only、multi-change start、naked role-miss hand",
                        "SD では依然 cut"
                     ]
                  ]
               }
            },
            "SB" : {
               "at_a_glance" : {
                  "open_core" : "widest one-change numeric / club core、later-street pressure hand、blocker-heavy half-lock。",
                  "position_add" : "selected blocker singleton with live side structure、selected thin chop-pressure hand、more heads-up one-change open。",
                  "snap_fold" : "single anchor only、multi-change start、no-role blind-battle garbage。",
                  "vs_complete" : "BB defend は most live one-change keep、strong blocker-heavy club core、selected single-anchor blocker まで practical に増やせる。"
               },
               "caution_note" : "それでも blind battle だからといって naked single anchor や multi-change garbage を混ぜると、SD の role-miss で一気に崩れます。",
               "confidence_label" : "低め: blind-battle SD inference",
               "label" : "SB",
               "open_complete" : {
                  "anchor_profile" : "blind-battle SD inference / SB",
                  "collected_rows" : [
                     {
                        "evidence_type" : "chop_pressure",
                        "notes" : "SB add の根拠",
                        "range_read" : "片側確保からのベット圧で marginal chop hand を降ろす",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "blind battle でもまだ切る",
                        "range_read" : "single anchor は SD で role を作れないことがある",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "SB は widest one-change core と later-street pressure hand を基礎に、selected blocker singleton with live side structure、selected thin chop-pressure hand、more heads-up one-change open を practical に追加します。",
                  "range_groups" : [
                     {
                        "items" : [
                           "widest one-change numeric / club core",
                           "later-street pressure hand",
                           "blocker-heavy half-lock"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "selected blocker singleton with live side structure",
                           "selected thin chop-pressure hand",
                           "more heads-up one-change open"
                        ],
                        "label" : "SBで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "single anchor only",
                           "multi-change start",
                           "no-role blind-battle garbage"
                        ],
                        "label" : "blind battleでも切る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "SB row は no-limit の pressure を strongest に使える seat として widening しています。ただし public note が弱いとする single-anchor only は blind battle でも中心にしていません。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "widest one-change numeric / club core、later-street pressure hand、blocker-heavy half-lock",
                        "SB から標準オープン"
                     ],
                     [
                        "この位置で追加",
                        "selected blocker singleton with live side structure、selected thin chop-pressure hand、more heads-up one-change open",
                        "blind battle で practical に追加"
                     ],
                     [
                        "まだ見送る",
                        "single anchor only、multi-change start、no-role blind-battle garbage",
                        "heads-up でも role-miss が重い"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "selected blocker singleton with live side structure、selected thin chop-pressure hand、more heads-up one-change open。",
                  "open_identity" : "one-change core と later-street pressure をかけやすい hand が主体。",
                  "seat_trigger" : "heads-up 前提が最も強い no-limit blind battle seat。",
                  "still_avoid" : "single anchor only、multi-change start、no-role blind-battle garbage。"
               },
               "position_summary" : "SB は blind battle なので、one-change numeric / club core that can pressure later streets、selected blocker singleton with live side structure、selected thin chop-pressure hand まで practical に開ける席です。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "82x one-change / A-high triple club / premium two-of-826",
                        "label" : "安定 defend",
                        "range_read" : "one-change / half-lock / best two-of-826 one-draw は SB 相手でも守りの主軸です。",
                        "tone" : "attack",
                        "when" : "公開 note の one-change priority と half-lock logic に沿う時。"
                     },
                     {
                        "examples" : "blocker-heavy one-change / single-anchor blocker + structure",
                        "label" : "SB相手で最大化",
                        "range_read" : "most live one-change keep、strong blocker-heavy club core、selected single-anchor blocker、selected thin chop-pressure hand を practical に追加します。",
                        "tone" : "conditional",
                        "when" : "blind battle で opener が最も広い時。"
                     },
                     {
                        "examples" : "8♣xy only / no-role start",
                        "label" : "まだ切る",
                        "range_read" : "single anchor only、multi-change start、no-role blind-battle garbage は SB 相手でも defend しません。",
                        "tone" : "fold",
                        "when" : "role / blocker / structure のいずれも薄い時。"
                     }
                  ],
                  "anchor_profile" : "blind-battle SD inference / BB defend vs SB",
                  "collected_rows" : [
                     {
                        "evidence_type" : "chop_pressure",
                        "notes" : "SB defend widen",
                        "range_read" : "ノーリミットで marginal chop hand を降ろす発想",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "まだ切る帯",
                        "range_read" : "single anchor の価値低下",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "SB open に対する BB call は most live one-change keep、most strong blocker-heavy club core、selected single-anchor blocker、selected thin chop-pressure hand まで practical に増やします。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "SB defend は blind battle の late-pressure row ですが、主軸はあくまで one-change / half-lock / blocker pressure です。naked anchor はここでも中心化しません。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "one-change / half-lock / best two-of-826 one-draw",
                        "安定 defend"
                     ],
                     [
                        "この相手に増える",
                        "most live one-change keep、strong blocker-heavy club core、selected single-anchor blocker、selected thin chop-pressure hand",
                        "SB steal に対して最大化"
                     ],
                     [
                        "フォールド寄り",
                        "single anchor only、multi-change start、no-role blind-battle garbage",
                        "heads-up でも下限は cut"
                     ]
                  ]
               }
            },
            "UTG" : {
               "at_a_glance" : {
                  "open_core" : "all 82x one-change core、strong 86x / 26x one-change、strong double-club one-change、made half-lock。",
                  "position_add" : "premium two-of-826 one-draw と blocker-heavy club core まで。",
                  "snap_fold" : "single anchor only、multi-change numeric、no-role risk start。",
                  "vs_complete" : "BB では one-change 82/86/26、strong double-club、made half-lock、best two-of-826 one-draw を守る。"
               },
               "caution_note" : "公開 note は SD の価値軸を示すのみで、UTG exact row はありません。UTG はそのヒューリスティックを最も厳しく適用した row です。",
               "confidence_label" : "低〜中: public one-change heuristic の最上流再構成",
               "label" : "UTG",
               "open_complete" : {
                  "anchor_profile" : "public-source reconstruction / tightest SD seat",
                  "collected_rows" : [
                     {
                        "evidence_type" : "direct_heuristic",
                        "notes" : "UTG open の主根拠",
                        "range_read" : "SD では 1チェンジ参加が重要で、single 8♣ / 2♣ / A♣ の価値は相対的に低い",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "direct_heuristic",
                        "notes" : "premium one-draw class の根拠",
                        "range_read" : "two-of-826 one-draw は hard to finish でも完成82がかなり捲られづらい",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "UTG は role-miss を最も嫌うため、1チェンジ numeric core、strong double-club one-change、made half-lock、premium two-of-826 one-draw だけを open の中心に置きます。",
                  "range_groups" : [
                     {
                        "items" : [
                           "1チェンジ 82x / 86x / 26x",
                           "strong double-club one-change",
                           "made half-lock"
                        ],
                        "label" : "Open core",
                        "tone" : "attack"
                     },
                     {
                        "items" : [
                           "premium two-of-826 one-draw",
                           "blocker-heavy club core"
                        ],
                        "label" : "条件付きで足す",
                        "tone" : "conditional"
                     },
                     {
                        "items" : [
                           "single anchor only",
                           "multi-change start",
                           "no-role risk hand"
                        ],
                        "label" : "UTGでは見送る",
                        "tone" : "fold"
                     }
                  ],
                  "section_label" : "Open / Raise",
                  "source_note" : "ぞにき記事は SD で 1チェンジ参加が大切で、two-of-826 one-draw は hard to finish でも強力、single strong card の価値は TD より低いと明示しています。UTG row はその最も厳しい適用です。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "Open core",
                        "1チェンジ 82x / 86x / 26x、strong double-club one-change、made half-lock",
                        "UTG から常時オープン"
                     ],
                     [
                        "条件付きで足す",
                        "premium two-of-826 one-draw、blocker-heavy club core",
                        "live kicker と blocker が揃う時だけ"
                     ],
                     [
                        "まだ見送る",
                        "single anchor only、multi-change start、no-role risk hand",
                        "1ドローでは未完成リスクが大き過ぎる"
                     ]
                  ]
               },
               "overview" : {
                  "adds_here" : "blocker-heavy club core と live kicker 付き two-of-826 one-draw まで。",
                  "open_identity" : "1チェンジ numeric core、strong double-club one-change、made half-lock、premium two-of-826 one-draw が土台。",
                  "seat_trigger" : "後ろに4人残り、1ドローしかないため role-miss が最も痛い席。",
                  "still_avoid" : "single anchor only、multi-change start、naked role-miss risk hand。"
               },
               "position_summary" : "最も role-miss を嫌う席です。1チェンジ numeric core、strong double-club one-change、made half-lock、premium two-of-826 one-draw が open の中心になります。",
               "source_refs" : [
                  "zoniki_overview_note",
                  "zoniki_rulebook_image"
               ],
               "versus_complete" : {
                  "action_bands" : [
                     {
                        "examples" : "82x one-change / A-high triple club / premium two-of-826",
                        "label" : "自然に defend",
                        "range_read" : "one-change 82x / 86x / 26x、strong double-club one-change、made half-lock、best two-of-826 one-draw は UTG 相手でも defend の中核です。",
                        "tone" : "attack",
                        "when" : "公開 note の one-change priority を満たす時。"
                     },
                     {
                        "examples" : "blocker club shell / thin 86x one-draw",
                        "label" : "UTG相手では薄く残す",
                        "range_read" : "blocker-heavy club shell と thin 82x / 86x one-draw は BB の close-the-action を使う時だけ残します。",
                        "tone" : "conditional",
                        "when" : "UTG でも open がやや広いと読める時に限定。"
                     },
                     {
                        "examples" : "8♣xy only / 2♣xy only / no-role trash",
                        "label" : "基本 cut",
                        "range_read" : "single anchor only、multi-change start、no-role risk hand は defend から外します。",
                        "tone" : "fold",
                        "when" : "1ドローで役なし終了のリスクが高い時。"
                     }
                  ],
                  "anchor_profile" : "public-source reconstruction / BB defend vs UTG in SD",
                  "collected_rows" : [
                     {
                        "evidence_type" : "one_change_priority",
                        "notes" : "BB call core の基準",
                        "range_read" : "SD では 1チェンジ参加が大切",
                        "source_ref" : "zoniki_overview_note"
                     },
                     {
                        "evidence_type" : "single_anchor_downgrade",
                        "notes" : "single anchor only を切る根拠",
                        "range_read" : "TD と違い SD では strong single card が role を作れないことがある",
                        "source_ref" : "zoniki_overview_note"
                     }
                  ],
                  "public_range_read" : "UTG open に対する BB call は one-change 82x / 86x / 26x、strong double-club one-change、made half-lock、best two-of-826 one-draw が中心で、single anchor only は基本 cut です。",
                  "section_label" : "BB Call vs Open",
                  "source_note" : "SD の defend でも優先順位は同じで、1チェンジか half-lock が見える hand を残し、single anchor only は強く削ります。",
                  "table_columns" : [
                     "区分",
                     "代表 hand / class",
                     "扱い"
                  ],
                  "table_rows" : [
                     [
                        "BB call core",
                        "one-change 82x / 86x / 26x、strong double-club one-change、made half-lock、best two-of-826 one-draw",
                        "標準 defend 帯"
                     ],
                     [
                        "条件付きで残す",
                        "blocker-heavy club shell、thin 82x / 86x one-draw",
                        "UTG 相手ではかなり慎重"
                     ],
                     [
                        "フォールド寄り",
                        "single anchor only、multi-change start、no-role risk hand",
                        "1ドローの miss が痛過ぎる"
                     ]
                  ]
               }
            }
         },
         "variant_summary" : "1ドローしかないため、1チェンジで参加できる structure、two-of-826 one-draw、made half-lock 寄りの hand が前に来ます。",
         "variant_warning" : "TD と違って single 8♣ / 2♣ / A♣ の価値は下がり、役なしミスが現実的です。naked anchor を open / call に回し過ぎないことが重要です。"
      }
   },
   "verification" : {
      "checked_on" : "2026-04-18",
      "confirmed_source_refs" : [
         "zoniki_overview_note",
         "zoniki_rulebook_image",
         "yamamoto_fl826_preview",
         "pokerguild_fl826_event"
      ],
      "method" : "2026-04-18 に note 公開本文、埋め込みルールブック画像 URL、FL826TD preview、PokerGuild 告知を再確認。併せて standalone PDF / CSV chart の公開導線も再確認したが 826 固有の公開レンジ PDF は未発見。"
   },
   "version" : 2
}
;

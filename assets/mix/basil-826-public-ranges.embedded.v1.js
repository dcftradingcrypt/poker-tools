window.__BASIL_826_PUBLIC_RANGES_V1 = {
  "dataset_id": "basil_826_public_archetypes_v2",
  "version": 2,
  "game": "basil_826",
  "scope": {
    "game_label": "826 / Basil",
    "primary_view": "source_confirmed_archetypes",
    "variants": [
      "FL826TD",
      "NL826SD"
    ],
    "position_model": "not_available_from_public_sources",
    "source_boundary": "Public sources support role hierarchy, variant-specific archetypes, pot-share risks, and pressure overlays. They do not support an exact UTG/HJ/CO/BTN/SB range matrix or exact BB defense matrix."
  },
  "collection_notes": [
    "The accessible zoniki note and embedded rule image are the public authority for the role system, TD/SD split, picture discard mechanic, and strategic risk themes.",
    "The paywalled preview only confirms that a deeper FL826TD positional framework exists around UTG-CO raise and BB defense. It does not reveal enough detail to publish exact public thresholds.",
    "This asset therefore exposes source-confirmed archetypes and risk overlays only. It intentionally does not publish position-specific open or call ranges."
  ],
  "source_index": {
    "zoniki_note": {
      "title": "[初心者向け]826(バジル)ポーカーの概要とゲームセオリー",
      "weight": "primary",
      "source_type": "HTML",
      "url": "https://note.com/zoniki/n/n3143c1508eeb"
    },
    "zoniki_rule_image": {
      "title": "826 rulebook image embedded in the zoniki note",
      "weight": "primary_rules",
      "source_type": "embedded_image",
      "url": "https://note.com/zoniki/n/n3143c1508eeb"
    },
    "rich_swan_preview": {
      "title": "FL826TD positional framework preview",
      "weight": "limited_preview",
      "source_type": "paywalled_preview",
      "url": "https://note.com/rich_swan32/n/n65c7eeb16211"
    }
  },
  "source_extracts": {
    "zoniki_note": {
      "scope": "variant split, picture discard mechanic, TD/SD strategic difference, role-miss risk, root theory, and no-limit chop pressure",
      "notes": [
        "826 alternates Fixed-Limit 826 Triple Draw and No-Limit 826 Single Draw every five hands.",
        "Discarding K/Q/J face-up grants one extra draw card.",
        "In Triple Draw, 8c, 2c, and Ac single-card anchors are stronger because repeated draws and picture conversion improve realization.",
        "In Single Draw, entering with one-change structure is important because single anchors can still fail to make a role.",
        "No-limit pressure can make otherwise split-prone hands profitable by folding out marginal chop candidates."
      ]
    },
    "zoniki_rule_image": {
      "scope": "role definitions and rank order",
      "notes": [
        "Number role order is 826, then 82, then 86, then 26.",
        "Club role is ordered by club count first, then card strength.",
        "8c2c6c is Royal Basil and is treated as the exceptional top holding."
      ]
    },
    "rich_swan_preview": {
      "scope": "limited proof of deeper FL826TD positional work",
      "notes": [
        "The visible preview supports that UTG-CO raise and BB defense thresholds exist in a deeper framework.",
        "The preview does not expose exact thresholds or exact public hand-class cutoffs."
      ]
    }
  },
  "source_coverage": [
    {
      "source_ref": "zoniki_note",
      "used_for": "variant split, picture discard mechanic, triple-draw versus single-draw strategy difference, role-miss risk, and no-limit pressure themes",
      "views": [
        "FL826TD.archetypes",
        "FL826TD.risk_overlays",
        "NL826SD.archetypes",
        "NL826SD.risk_overlays"
      ]
    },
    {
      "source_ref": "zoniki_rule_image",
      "used_for": "role definitions, role order, club count ordering, and Royal Basil exception",
      "views": [
        "FL826TD.archetypes",
        "FL826TD.risk_overlays",
        "NL826SD.archetypes",
        "NL826SD.risk_overlays"
      ]
    },
    {
      "source_ref": "rich_swan_preview",
      "used_for": "limited proof that deeper FL826TD positional work exists, without enough public detail to publish exact thresholds",
      "views": [
        "scope_boundary"
      ]
    }
  ],
  "hand_ranges": {
    "FL826TD": {
      "archetypes": {
        "SOURCE_CONFIRMED": [
          "8c / 2c / Ac の単独アンカー。TD では 3 回のドローとピクチャードローにより実現率が高くなる。",
          "8c / 2c / Ac と K/Q/J の組み合わせ。ピクチャーを表にして捨てることで追加カードを得られるため、選択肢が増える。",
          "KQJ などのピクチャー濃度が高いスタート。追加ドローの仕組みを使いやすい。",
          "82 / 86 / 26 のような数役をすでに持つ catch hand。ただし片側だけで受け身になりやすく、無条件の強レンジではない。",
          "トリプルクラブ、とくに A high のクラブ構造。クラブ側の半分を取りやすいが Royal Basil 例外を残す。",
          "クラブ支援のない弱い 6 系や、26 / 弱いトリプルクラブのような三者ポットで挟まれやすいハンドは、公開資料上は警戒対象。"
        ]
      },
      "risk_overlays": {
        "SOURCE_CONFIRMED": [
          "Royal Basil: 8c2c6c は通常の 826 やトリプルクラブより上に置かれる例外。",
          "るーと理論: 8cAc を含む一部の完成形は、ヘッズアップで少なくとも半分を取りやすい。",
          "クォーターリスク: 826 側が完成しても、もう片側で分けられると取り分が大きく落ちる。",
          "三者ポットの挟まれリスク: 片側だけの marginal hand は、強い半分同士に挟まれると苦しくなる。",
          "公開資料は position 別の exact open / BB defense 閾値を出していないため、この画面では positional range を表示しない。"
        ]
      }
    },
    "NL826SD": {
      "archetypes": {
        "SOURCE_CONFIRMED": [
          "1 チェンジで数役を作れる構造。SD では役なしリスクを下げるため、1 チェンジで参加できることが重要。",
          "1 チェンジでクラブ側を作れる構造。すぐに半分を主張できる可能性がある。",
          "8/2/6 のうち 2 枚を持つ one-draw 構造。1 ドローで完成させるのは難しいが、完成時はまくられにくい。",
          "8c / 2c / Ac の単独アンカー。TD より価値は下がり、支援がなければ役なしで終わるリスクが残る。",
          "半分を確保しやすい made half-lock 型。ノーリミットの圧力と組み合わせて利益化しやすい。",
          "役なしリスクが高いスタートは、SD では TD より大きく減点する。"
        ]
      },
      "risk_overlays": {
        "SOURCE_CONFIRMED": [
          "SD は 1 回しか引けないため、単独アンカーより one-change 構造を優先する。",
          "ノーリミットでは、少なくとも片側を取りやすい状態から強く打って、マージナルなチョップ候補を降ろせる。",
          "82 完成は 1 チェンジ同士ではまくられにくく、少なくとも半分を取りやすい。",
          "TD と同じハンドでも、SD では役なしで終わるリスクが大きくなるため、同じレンジとして扱わない。",
          "公開資料は exact position matrix を示していないため、ここでは役・構造・圧力モデルだけを表示する。"
        ]
      }
    }
  }
};

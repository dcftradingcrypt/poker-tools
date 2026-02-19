# CLAUDE.md

## 実装ルール
1. 変更前に `rg` / `sed` で該当箇所を特定し、根拠行を確認する。
2. 最小差分で修正し、既存行を残したままの重複追記をしない。
3. HTMLの `id` を重複させない。
4. 「式を触らない」指定タスクでは、計算式・関数構造・イベント接続を変更しない。
5. 修正後は必ず検証コマンドを実行し、結果を確認する。
6. ユーザーへ python3/rg/sed/curl 等のコマンド実行を依頼しない。依頼できるのは `git push` と結果確認（目視）だけ。検証・修正・コミット・ログ採取はCODEXが実行し、ログを添えて報告する。

## チェックリスト（毎回）
### 手動確認（ブラウザ）
1. A-1（必須不足でno-opしない）: EV電卓Aで `相手ベット後ポット` と `コール額` を空欄のまま `コールEV更新` を押す。期待結果は `evcall-error` に `ポット額とコール額を入力` が出て、`evcall-pot-after` へfocus。根拠は `index.html:2009` `index.html:2010` `index.html:2011` `index.html:4386`。
2. A-2（reqはE不要）: EV電卓Aで `P_after` と `C` を入力、`R` と `E` は空欄で `コールEV更新`。期待結果は `R` が 0 扱いで `evcall-req` が更新され、`evcall-ev` と `evcall-gap` は `--` のまま。根拠は `index.html:2023` `index.html:2040` `index.html:2041` `index.html:2043` `index.html:2044` `index.html:2045`。
3. B-1（MDFのみ表示）: EV電卓Bで `P` `B` を入力して `ベット更新`。期待結果は `evbet-mdf` のみ更新される。根拠は `index.html:1149` `index.html:2059` `index.html:2060` `index.html:2064` `index.html:2089` `index.html:4399`。
4. B-2（クイックベットの必須誘導）: EV電卓Bで `P` 空欄のまま `1/2P` などを押す。期待結果は `evbet-error` に `先にPを入力` が出て `evbet-pot` へfocus。根拠は `index.html:2096` `index.html:2097` `index.html:2098` `index.html:4395`。
5. C-1（outs未入力でno-opしない）: EV電卓Cで `outs` 空欄のまま `Outs更新` を押す。期待結果は `evouts-error` に `outsを入力` が出て `evouts-count` へfocus。根拠は `index.html:2178` `index.html:2179` `index.html:2180` `index.html:4451`。
6. C-2（正常入力で部分結果更新）: EV電卓Cで `outs=9`、`draws=1`、`unseen=47` を入力して `Outs更新`。期待結果は `evouts-exact` と `evouts-approx` が `%` 表示で更新される。根拠は `index.html:2201` `index.html:2202` `index.html:2203` `index.html:2204`。
7. T-1（練習/鍛錬の切替）: トレーナーで `進行モード` を `練習` と `鍛錬` で切り替える。期待結果は問題状態がリセットされ、`残り時間` 表示が初期化される。根拠は `index.html:1500` `index.html:3218` `index.html:3261` `index.html:4633` `index.html:4639`。
8. T-2（鍛錬TIMEOUT）: `進行モード=鍛錬` で出題し、制限秒数を超えるまで待つ。期待結果は `TIMEOUT` 表示と `得点 0.0点` が出て問題終了し、`正答` と `解法`（式+途中値）が表示され履歴へ保存される。根拠は `index.html:1506` `index.html:3327` `index.html:3335` `index.html:3340` `index.html:3425`。
9. T-3（解法表示）: req/MDF それぞれで回答する。期待結果は `trainer-feedback` に `解法`（req: `req=C/(P_after+C-R)`、MDF: `MDF=P/(P+B)`）と数値代入の途中値が表示される。根拠は `index.html:3304` `index.html:3311` `index.html:3316` `index.html:3492` `index.html:3497`。
10. T-4（得点内訳と統計）: 鍛錬で回答したとき、`得点内訳: accuracy/speed/合成` が表示される。あわせて履歴と `req平均得点` / `MDF平均得点` が更新される。根拠は `index.html:3283` `index.html:3495` `index.html:3185` `index.html:3215` `index.html:3324`。
11. セルフテスト（13件）: 設定タブで `EV電卓セルフテスト` を押す。期待結果は `セルフテスト: 13/13 PASS`。根拠は `index.html:1548` `index.html:2289` `index.html:4694`。

## 修正ログ

### 2026-02-13 19:57:19 KST
- 対象: `index.html`
- 目的: EV電卓中心の運用に合わせて UI と文言を整理し、1アクションEV(A/B/C)を追加。
- 実施:
  - `EV電卓` タブを追加し、初期表示タブを `EV電卓` に変更。
  - 機能A `コールEV（フォールド=0）` を追加（req / EV_call / E-req / 判定）。
  - 機能B `ベット損益分岐（1ストリート / Fold・Call 2択）` を追加。
    - 前提文を明記（Fold/Callのみ、Raiseなし、将来ストリート無視、チェック時期待値は自動計算しない）。
    - `1/3P, 1/2P, 2/3P, 1.0P` ボタンでB自動入力。
    - ベット単体EV式の定義コメントをJS内に明記。
  - 機能C `Outs → ヒット率` を追加（組合せ式の正確値 + 2/4近似）。
  - 下部ナビを5タブ化（EV電卓/プリフロップ/ICM/トレーナー/設定）。
  - 主要計算ボタン行を sticky 化（モバイル操作性向上）。
- 検証:
  - 重複ID検査、禁止語句残骸、主要ID出現を確認。

### 2026-02-13 20:09:00 KST
- ミス: 機能Bを「Bet vs Check」等と誤表記して誤認を誘発した
- ミス: ラベル修正なのに追記して二重化/重複idを作る危険があった
- ミス: 未導入コマンド(rg/node)前提で検証ログを書いた
- 再発防止: grep/python3のみで必須検証を固定し、実行ログをそのまま貼る

### 2026-02-13 21:51:04 KST
- ミス: 機能Bを「Bet vs Check」と表記し、チェックEVを計算しているように誤解させた
- ミス: 機能Bの前提（Fold/Callのみ・将来ストリート無視・E_called固定）をUIに固定表示せず、一般のベットEVに見せた
- ミス: ラベル修正時に“置換”ではなく“追記”して見出し/ラベルが二重化するリスクを作った
- 再発防止: コミット前に「禁止語rg 0件」+「duplicate idチェック OK」を必須化（このログをCLAUDE.mdに毎回残す）

### 2026-02-14 00:49:32 KST
- ミス: 機能Bの注意書き文言が指定の固定文と一致せず、前提解釈に揺れが出る状態を残した
- ミス: 機能Bの出力ラベルで「必要フォールド率 F_be」の表記統一を崩した
- ミス: ベット単体EVのF_be算出を EV_bet=0 導出式で固定せず、仕様との差分を残した
- 再発防止: 機能B修正時は「固定文言一致」「ラベル一致」「EV_bet/F_be式一致」を rg と該当行確認で必須化する

### 2026-02-14 01:24:53 KST
- ミス: 機能Bの嘘ラベル（比較EVに見える表現）を残し、ベット単体EVの前提を曖昧にした
- ミス: ラベル修正時に置換ではなく追記へ流れ、見出し二重化と重複IDの再発リスクを作った
- ミス: 実在しないPR番号を決め打ちで記載する捏造リスクを許容した
- 再発防止: 機能B修正時は「固定文言一致」「禁止語0件」「重複ID0件」「PR番号は実コマンド結果のみ」を必須チェックに固定する

### 2026-02-14 06:19:57 KST
- ミス: EV電卓の式を監査・固定テストで担保せず、表示が正しくても将来の式破壊を検知できない状態を許容した
- ミス: 機能Bの F_be 条件（calledEV>=0 なら 0%）をコードで明示せず、仕様差分を残すリスクがあった
- ミス: 数式検証を手動目視だけに依存し、再実行可能な固定ケース検証を持たなかった
- 再発防止: EVの式はテストがないと信用ゼロとして、固定ケースのセルフテスト（A/B/C）をSettingsから毎回実行して結果を確認する

### 2026-02-14 06:29:07 KST
- ミス: EV電卓の式を更新処理とセルフテストで二重実装し、将来差分で不一致が起きる構造を残していた
- ミス: 機能Bの損益分岐条件（calledEV>=0 なら F_be=0）を固定テストで継続監視していなかった
- ミス: 機能Cの確率式を表示処理側で再計算し、純関数を通さない経路が残っていた
- 再発防止: A/B/Cは純関数を単一ソースに固定し、Settingsのセルフテストを純関数呼び出しのみで実行して式の乖離を常時検出する

### 2026-02-14 23:14:29 KST
- ミス: 機能B入力検証で `bet=0` を許可し、ベット損益分岐の前提（ベット額>0）を満たしていなかった
- ミス: `updateBetEvDecision` が `bet<=0` を検知しないまま `P+B` のみを判定していた
- ミス: F_be の範囲外警告が仕様外表示として残る可能性を残していた
- 再発防止: 機能B修正時は `bet<=0` エラーハンドリング、`calledEv>=0` の `F_be=0` 表示、不要警告の除去を同一関数前後行で根拠化し、検証ログ（重複ID/禁止語/差分）を保存する

### 2026-02-15 00:03:26 KST
- ミス: 機能Bセルフテスト前の固定ケースを1ストリート式で固定化するログ整備が不明瞭だった
- ミス: セルフテストが13件固定でもPASS/FAILの実行結果を必須として明記しない運用が続いた
- ミス: 「Bet vs Check」等の文言混在防止を最終チェックで確実化していなかった
- 再発防止: `runEvCalculatorSelfTests` を pure 関数3つのみで実装し、`git grep` 禁止語検査と 13/13 PASS を必須ログ化する

### 2026-02-15 04:07:00 KST
- ミス: どの index.html を開いているかを目視で確認する手段が Settings になく、popker_backup / DO_NOT_USE の見分けが曖昧だった
- ミス: 設定情報の表示面で URL/ファイル同定を運用ログに含めず、混線時の原因切り分けが遅くなりやすかった
- ミス: 変更検証を Settings 起点の手順として固定化していなかった
- 再発防止: Settings に window.location.href 表示を追加し、起動時に DOM 初期化で反映する。必要時に `settings-current-url` を確認する運用を追加


### 2026-02-15 06:02:13 KST
- ミス: Settings 画面で現在ファイルを視覚的に確認できず、`popker_backup` / `DO_NOT_USE` 利用時の判定が実運用でできていなかった
- ミス: URLベースのワークスペース誤開封時警告を Settings に実装せず、混線時に早期検知ができない状態を放置した
- ミス: `window.location.href` と `settings-current-url` の表示確認を設定導線に固定していなかった
- 再発防止: `settings-current-url` + `workspace-warning` を Settings 初期化時に反映し、`popker_backup|DO_NOT_USE` 判定で赤字警告を出す運用を追加。`workspace-warning` ID の有無と表示状態を確認コマンドに固定

### 2026-02-15 06:20:11 KST
- ミス: 既存のworkspace警告条件が OneDrive を含まず、OneDrive 配下の誤開封を見逃す可能性を残した
- ミス: 構成確認ログに OneDrive 条件の明示がなく、監査時に再確認が漏れていた
- ミス: 同一指摘で混線対策の有効性判定を「1回の実行」に依存せず運用に固定しきれなかった
- 再発防止: `workspace-warning` 条件を `OneDrive|popker_backup|DO_NOT_USE` へ固定化し、`git grep` 監査と `settings-current-url`/`workspace-warning` の表示確認を固定コマンド化する

### 2026-02-15 06:40:00 KST
- ミス: ワークスペース警告条件が ARCHIVE を含まず、3系統判定（OneDrive / popker_backup / DO_NOT_USE）との整合を欠いた
- ミス: 警告文が `C:\repos\popker を開け` 固定だったため、正規環境誘導を明文化しきれていなかった
- ミス: ARCHIVE 含有時の判定結果を固定コマンド（findstr）での運用手順に繋げていなかった
- 再発防止: `ARCHIVE` をワークスペース警告正規表現へ追加し、警告文を `それはバックアップ/隔離コピー。正規は C:\repos\popker を開け` に固定。対象確認は既存grepコマンドに固定化

### 2026-02-15 10:26:00 KST

- ミス: ポットオッズの手入力パスがなく、手計算エクイティが無い状態でEV差/判定に進めなかった

- ミス: lastCalculatedEquity と入力値の優先順位を明文化しないままポットオッズ更新を運用していた

- ミス: pot-equity-input の入力イベントを追加しないと、入力内容が画面に即反映されない状態が残っていた

- 再発防止: pot-equity-input を追加し、updatePotOddsDecision のエクイティ選択順（手入力優先→未入力時はlastCalculatedEquity）を固定。変更後は  と id 重複検査を必須化


### 2026-02-15 10:26:00 KST
- ミス: ポットオッズの手入力経路がなく、手計算エクイティが無い状態でEV差/判定を表示できなかった
- ミス: lastCalculatedEquity のみ参照する前提で手入力優先を見落としていた
- ミス: pot-equity-input の入力イベントを追加しないと入力値が即時反映されない導線が残っていた
- 再発防止: ポットオッズで pot-equity-input を追加し、updatePotOddsDecision を「手入力(0-100)優先→未入力時は lastCalculatedEquity」で固定。

### 2026-02-15 10:39:10 KST
- ミス: 更新対象 `pot-equity-input` の優先順位が未定義だったため、lastCalculatedEquity と手入力の衝突時の挙動が運用不明だった
- ミス: ポットオッズの `input` イベント接続で `pot-equity-input` を含めず、編集しても即時更新されない状態が残っていた
- ミス: 限定タスクなのに Settings/警告追加差分と混在し、差分起点が広くなっていた
- 再発防止: 今回から対象変更行は `equity-ev-panel` / `updatePotOddsDecision` / 該当 `addEventListener` のみで扱い、`git diff` と禁止語・重複id監査を同時に必須化する

### 2026-02-15 21:06:45 KST
- ミス: ポットオッズ/EV判断をEV電卓Aへ一本化する編集で、`updateBetEvDecision` の関数定義を壊す変更を混入した
- ミス: `equity-ev-panel` 関連の混線経路を整理しながら `updatePotOddsDecision` 側参照の残存チェックを遅らせた
- ミス: 構文エラー修正後の最終監査を省き、差分提出の直前までJS構文状態を確認しきれていなかった
- 再発防止: `updateBetEvDecision` のシグネチャとポットオッズ旧ID(`pot-size-input`等)を `rg` で固定監査し、禁止語・重複IDチェックを必須ログとして毎回実行する

### 2026-02-15 22:12:10 KST
- ミス: プリフロップ残骸（`equity-ev-panel`）と旧ポット計算ルートが残っており、監査しやすい構造ではなかった
- ミス: `updatePotOddsDecision` 参照除去後、残骸の最終検査を固定しなかった
- ミス: 既存UI整理中に `equity-ev-panel` のCSS名残が 1 箇所残ったままで grep 想定とズレた
- 再発防止: `equity-ev-panel/updatePotOddsDecision/required-equity-output` の 3系統 grep を毎回実行し、`function updateCallEvDecision` と `evcall-req` の表示仕様のみを維持する運用に固定

### 2026-02-16 01:25:30 KST
- ミス: `equity-ev-panel`・`updatePotOddsDecision` 相当の旧フローが残っていないかの最終確認を、`updateCallEvDecision` の `req` 単独表示要件と紐付けて証跡化していなかった
- ミス: 同一検査で `ev-diff` 系（`assumed-ev-diff`）が混在し、grep パターン誤差で旧パネル残骸監査と混線する可能性があった
- ミス: 既存 `updateCallEvDecision` の `if (pAfter === null || call === null || returned === null) return;` の意味を確認せずに、「req未入力表示」の成立条件を断定しがちだった
- 再発防止: タスク受け入れ時は必ず `equity-ev-panel|updatePotOddsDecision|pot-size-input|call-size-input|required-equity-output|ev-status` grep、`function updateCallEvDecision` 行番号、`if (pAfter === null` 行の3点を最小証跡として記録し、差分を index/CLAUDE のみで閉じる

### 2026-02-16 04:56:06 KST
- ミス: プリフロップ（HU）タブの"ポットオッズ / EV判断"固定文が残り、運用上"何を見ればよいか"が曖昧な状態を放置した
- ミス: 要件どおり "見出し/案内文"の置換ではなく、従来行のまま混在させる変更に依存しうる状態を残した
- ミス: 変更対象を winrate-tab に限定しながら、"更新確認"だけで終わるため監査ログ残しが不足していた
- 再発防止: 変更前後で"ポットオッズ / EV判断"文字列の有無を明示確認し、"winrate-tab"以外の監査対象で"updatePotOddsDecision"等旧参照0件を前提に作業を終了

### 2026-02-16 06:22:06 KST
- ミス: プリフロップ（HU）タブの旧ポットオッズ/EV判断残骸が残ると混線が再発する運用リスクを残した
- ミス: 旧導線の監査条件（`equity-ev-panel` 系ID/関数）を固定してゼロ確認していなかった
- ミス: タスク対象（winrate-tab）とその他機能（ワークスペース警告など）との差分境界を明示してログ化しきれていなかった
- 再発防止: 作業前後で `equity-ev-panel|updatePotOddsDecision|pot-size-input|call-size-input|required-equity-output|current-equity-output|ev-status|ev-diff(旧呼称)` を0ヒット監査し、`updateCallEvDecision` における `req=calcCallEv(...,0)` と `if (equityPct === null)` の存在を必須確認

### 2026-02-16 19:01:23 KST
- ミス: updateCallEvDecision で P_after/C のいずれか欠落時、共通returnでreq表示まで止めていた
- ミス: updateBetEvDecision で F が空欄でもベットEV/GAPの表示を抑え、F_beのみ見せる仕様が未対応だった
- ミス: setEvBetByPotRatio とアウト入力不足でエラー文を出さずに return しており、ボタンが無反応に見えた
- 再発防止: 4関数は「必須不足=ev...-error表示」「R空欄=0」「F空欄ならF_be表示のみ」を固定仕様にし、編集後は git diff・重複ID・対象関数 grep を必須監査ログに記録する

### 2026-02-16 23:56:50 KST
- ミス: EV電卓B/Outsの入力不足時に黙って return する仕様が残り、ボタン押下時にUI変化が起きず"無反応"状態が発生していた
- ミス: 機能BのF未入力時にF_beを先に提示しないため、ベット判定まで進められない経路を残した
- ミス: クイックベットやアウト計算の未入力時に具体的エラーメッセージ表示が不足し、原因切り分けが遅くなった
- 再発防止: 更新対象3関数は入力不足でも error/部分値を必ず更新し、毎回"重複IDチェック"+"禁止語チェック"+対象関数grepを必須ログ化する

### 2026-02-17 01:43:59 KST
- ミス: EV電卓B/Outsの入力不足時に黙ってreturnしていた既存フローを最終手順で固定していなかった
- ミス: 無反応状態を回避するための手動確認をタスク完了条件として固定していなかった
- ミス: R未入力時の req 表示要件を運用監査しないままの遷移があり得た
- 再発防止: 対象3関数は「必須不足=error/部分表示」「R空欄=0」「F空欄でもF_be表示」を毎回の仕様監査チェック項目に固定し、手動確認を実施したログを残す

### 2026-02-17 02:55:12 KST
- ミス: updateCallEvDecision で P_after/C 未入力時に黙って return し、どこに入力不足かが分からなかった
- ミス: updateBetEvDecision が F 未入力時に F_be の表示を残しつつ導線文言が不足し、ユーザーが次手順を迷う状態だった
- ミス: updateOutsHitRate が outs 未入力時にエラー表示のみで停止し、フォーカス誘導がなかった
- 再発防止: 対象4関数は「必須不足はエラー表示＋誘導」「F未入力時はF_beのみ表示」「outs未入力はfocus」「P_after/C不足はfocus」を固定し、diffと重複ID監査を併記する

### 2026-02-17 07:48:25 KST
- ミス: no-op を防ぐ仕様整理中、入力不足時の return 処理を他導線でも再確認しなければ誤って残しうる運用状態だった
- ミス: クイックベット押下時の P 未入力で focus や error 表示がないと「ボタン壊れ」体感が続く状態が残る
- ミス: updateBetEvDecision を F 必須扱いしたままでは、F_be が出せる条件での判断が遅延する混線が起きる
- 再発防止: 対象4関数は「必須不足は明示エラー＋誘導」「必要値は必ず表示」「未入力 F は部分表示で継続」を1セットで監査し、毎回禁止語とID整合を必須ログ化する

### 2026-02-17 09:06:21 KST
- ミス: 実装後に手動確認のログが残っておらず、P未入力のクイックベット/outs未入力の無反応が残りうる運用監査を見落とした
- ミス: 前回差分では P_after/C/R と F 未入力時の表示導線を一度で固定し、停止条件（req/F_be更新）を再検証しきれていなかった
- ミス: no-op排除と合わせて、`updateCallEvDecision`/`updateBetEvDecision`/`setEvBetByPotRatio`/`updateOutsHitRate` の更新条件を最終的に差分ログへ固定化していなかった
- 再発防止: 今回より、上記4関数のエラー表示・focus・部分更新を必須ログとして `git diff` と `DUP_IDS/MISSING_IDS` と禁止語0件を毎回残し、対象機能の結果確認を完了条件に組み込む

### 2026-02-17 10:27:47 KST
- ミス: no-op 監査前に4関数の要件を静的diffだけで終えた場合、P_after/C欠落・outs欠落・F欠落の「何か起きる更新」保証を見逃す危険があった。
- ミス: 1/3P/1/2Pなどのクイックベットで P 未入力時に evbet-error と focus 導線がないと、ボタン無反応と見誤る運用が残る余地があった。
- ミス: エラー表示が出た際も focus 導線を検証せずに完了扱いすると、入力不足の原因切り分けが遅延する再発可能性があった。
- 再発防止: 対象4関数のno-op条件を4点（evcall/evbet/setEvBetByPotRatio/outs）で必須監査し、`git grep`, `DUP_IDS/MISSING_IDS`, 禁止語0件を同一バッチで毎回ログ化する

### 2026-02-17 18:53:19 KST
- ミス: A/B/C 4関数の no-op 監査を終えてから再度静的差分へ戻る運用だと、req/F_be/エラー導線の成立を取り違える再発リスクがあった
- ミス: クイックベットやouts未入力時のエラー表示のみで、focus導線を停止条件へ固定していなかった
- ミス: P_after/C または E 未入力時に求める「部分結果」が出ているか、手順が固定されていなかった
- 再発防止: 指定4関数を1回の監査コマンドセット（4関数grep・イベントID確認・禁止語0件・DUP_IDS/MISSING_IDS）で固定し、停止条件「req/F_be必出」「state遷移必須」を必ず記録する

### 2026-02-17 18:54:45 KST
- ミス: 再実施時に 4 関数の no-op 監査を完了前に簡易確認を流し込むと、停止条件（req/F_be表示・focus）を見逃しやすい
- ミス: 監査時のコマンド実行で python が無く python3 で置換する追加確認が必要だった
- ミス: index の既存差分が大きく、no-op 差分だけを視覚的に抽出しづらい状態だった
- 再発防止: setEvBetByPotRatio/updateCallEvDecision/updateBetEvDecision/updateOutsHitRate の4関数を毎回監査し、禁止語・DUP_IDS/MISSING_IDS 0を完了条件として固定する

### 2026-02-17 22:20:06 KST
- ミス: manifest.json が single quote 形式の不正JSONで、読み込み時にパース失敗する状態を残した
- ミス: 作業ルートが `/mnt/c/Users/fujit/OneDrive/Desktop/popker` と `/mnt/c/repos/popker` で混線し、引継ぎ起点が不明確だった
- ミス: 引継ぎに必要な現状要約（正規パス/未解決/次アクション）を CLAUDE.md に固定化していなかった
- 再発防止: manifest.json は `python3 -m json.tool` で毎回検証し、CLAUDE.md 末尾に引継ぎサマリを更新してから完了とする

### 2026-02-17 23:50:46 KST
- 対象: `index.html` の `workspaceWarningEl.textContent`（`index.html:4358`）
- 根拠: `nl -ba index.html | sed -n '4348,4362p'` の実行ログで `C:\repos\popker` が JS 文字列に未エスケープで埋め込まれていた（`\r` が改行扱いになりうる）。
- diff要約: 警告文のパス表記を `C:\repos\popker` から `C:\\repos\\popker` に最小1行変更し、表示文字列の崩れを防止。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `nl -ba index.html | sed -n '4348,4362p'` / `rg -n \"equity-ev-panel|updatePotOddsDecision|pot-size-input|call-size-input|required-equity-output|current-equity-output|ev-status\" index.html` / `rg -n \"Bet vs Check|ベットEV（HU）|checkEV|Bet vs\" index.html` / `python3 -m json.tool manifest.json >/tmp/manifest_check.out` / `python3` で A/B/C 13 ケース再計算。
- テスト結果: 旧混線経路0件・禁止語0件・重複ID0件・`manifest.json` 構文OK。純関数式の再計算は `13/13 PASS`。
- 再発防止: Windowsパスを JS 文字列へ直書きする場合はバックスラッシュを必ず二重化し、`rg -n \"C:\\repos\\popker|C:\\\\repos\\\\popker\" index.html` で未エスケープ混入を監査する。

### 2026-02-18 02:58:40 KST
- 対象: `git push origin main` の失敗要因確定（DNS/疎通/認証の切り分け）
- 根拠:
  - サンドボックス内: `GIT_TRACE=1 GIT_CURL_VERBOSE=1 git push origin main` が `Could not resolve host: github.com` で停止
  - 昇格実行: 同コマンドで `Host github.com:443 was resolved` / `Connected to github.com` / `HTTP/2 401` の後、`fatal: could not read Username for 'https://github.com': No such device or address`
  - 追加確認: 昇格 `python3` DNSで `github.com -> 20.27.177.113`、昇格 `curl -I https://github.com` で `HTTP/2 200`
- diff要約: コード変更なし。運用ログとして push 失敗の事実と判定条件を追記。
- 実行コマンド: `pwd` / `git status -sb` / `git remote -v` / `git config --show-origin -l | rg ...` / `env | rg ...` / `cat /etc/resolv.conf` / `python3` DNS / `curl -I` / `GIT_TRACE=1 GIT_CURL_VERBOSE=1 git push origin main`
- テスト結果: DNS/疎通は昇格実行で成立、push停止点は認証（HTTPS username/password入力経路）で確定。`git status -sb` は `ahead 3` のまま。
- 再発防止:
  - push失敗時は必ず `GIT_TRACE=1 GIT_CURL_VERBOSE=1 git push origin main` を保存し、`Could not resolve host` か `HTTP 401 + could not read Username` かをログで分類する。
  - HTTPS運用を継続する場合は `git config --global credential.helper manager-core`（または同等helper）を有効化して非対話でも資格情報を供給できる状態を先に確認する。
  - 認証を単純化する場合は SSHへ統一し、`git remote set-url origin git@github.com:dcftradingcrypt/poker-tools.git` と `ssh -T git@github.com` 成功後に push する。

### 2026-02-18 19:06:25 KST
- 対象: `CLAUDE.md` の `チェックリスト（毎回）` に `手動確認（ブラウザ）` を追加し、EV電卓A/B/Cの no-op 監査手順を固定化
- 根拠:
  - 未解決起点: `CLAUDE.md` の `既知の未解決: ブラウザ手動確認（EV電卓A/B/Cの入力不足時表示遷移）は未実施`
  - A/B/C根拠行: `index.html:1986` `index.html:2058` `index.html:2131` `index.html:2158` `index.html:2011` `index.html:2012` `index.html:2033` `index.html:2036` `index.html:2119` `index.html:2136` `index.html:2137` `index.html:2173` `index.html:2174`
  - ボタン接続根拠: `index.html:4421` `index.html:4425` `index.html:4426` `index.html:4427`
- diff要約: `CLAUDE.md` にブラウザ手動確認7項目（A必須不足、A reqのみ、B F_beのみ、クイックベットfocus、outs focus、Outs正常更新、Settingsセルフテスト）を最小追記。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `rg -n \"既知の未解決|ブラウザ手動確認|引継ぎサマリ\" CLAUDE.md` / `nl -ba CLAUDE.md | sed -n '1,60p'` / `nl -ba CLAUDE.md | sed -n '230,290p'` / `rg -n \"function (updateCallEvDecision|updateBetEvDecision|setEvBetByPotRatio|updateOutsHitRate)\" index.html` / `nl -ba index.html | sed -n '1978,2210p'` / `nl -ba index.html | sed -n '4402,4432p'` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n \"Bet vs Check|ベットEV（HU）|checkEV|Bet vs\" index.html` / `rg -n \"equity-ev-panel|updatePotOddsDecision|pot-size-input|call-size-input|required-equity-output|current-equity-output|ev-status\" index.html` / `python3 -m json.tool manifest.json`
- テスト結果: 静的監査は `DUP_IDS []` / 禁止語0件 / 旧混線0件 / `manifest.json` 構文OK。ブラウザ目視結果はユーザー確認待ち。
- 再発防止: no-op確認は `手動確認（ブラウザ）` 7項目を毎回実施し、PASS/FAILとFAIL時のエラー文言・focus先をCLAUDE.mdへ転記してから完了扱いにする。

### 2026-02-18 23:39:52 KST
- 対象: `index.html`（EV電卓Bの純ブラフ再定義 / トレーナーに req・F_be・outs ドリル追加）
- 根拠:
  - B再定義: `index.html:1133`（純ブラフ前提文）`index.html:1153`（MDF表示）`index.html:1957`（`calcBetEv` を純ブラフ式へ変更）`index.html:2065`（`updateBetEvDecision` で `E_called` 依存を除去）
  - no-op抑止: `index.html:2091`（`P と B を入力`）`index.html:2093` `index.html:2094`（focus）`index.html:2123` `index.html:2124`（F未入力でも F_be/MDF 表示）
  - トレーナー拡張: `index.html:1501`（モード切替UI）`index.html:3210`（`buildTrainerQuestion`）`index.html:3250`（モード別出題）`index.html:3260`（即答判定）
  - イベント接続: `index.html:4436`（B入力監視から `evbet-equity-called` 除去）`index.html:4456`（モード変更ハンドラ）
- diff要約:
  - 機能Bから `E_called` 入力を削除し、`F_be` と `MDF` を常時表示する純ブラフモデルへ変更。
  - 機能Bの式を `EV_bluff = F*P + (1-F)*(-B)` / `F_be=B/(P+B)` / `MDF=P/(P+B)` に固定。
  - トレーナーをモード切替式（`req` / `F_be` / `outs`）の一意正答ドリルへ置換。
  - Settingsセルフテストは13件のまま維持し、Bケースだけ純ブラフ仕様へ差し替え（`B1 MDF` を追加、件数は固定）。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `rg -n \"機能B|E_called|updateBetEvDecision|calcBetEv|evbet-\" index.html` / `nl -ba index.html | sed -n '1124,1188p'` / `nl -ba index.html | sed -n '1938,2275p'` / `nl -ba index.html | sed -n '1492,1538p'` / `nl -ba index.html | sed -n '3170,3275p'` / `nl -ba index.html | sed -n '4398,4438p'` / `rg -n \"Bet vs Check|checkEV|Bet vs|ベットEV（HU）\" index.html || true` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n \"equity-ev-panel|updatePotOddsDecision|pot-size-input|call-size-input|required-equity-output|current-equity-output|ev-status\" index.html || true` / `python3 -m json.tool manifest.json >/dev/null` / `python3` で13ケース再計算
- テスト結果:
  - 静的監査: 禁止語0件 / 重複ID0件 / 旧混線経路0件 / `manifest.json` 妥当性OK
  - 数式再計算: `セルフテスト(式再計算): 13/13 PASS`
  - ブラウザ目視（B画面挙動・トレーナー操作・Settingsセルフテスト表示）はユーザー確認待ち
- 再発防止:
  - 機能B修正時は `E_called` 文字列の残存を `rg -n \"E_called|evbet-equity-called\" index.html` でゼロ確認してから完了扱いにする。
  - トレーナー修正時は「モードUI (`trainer-mode-select`)」「出題関数 (`buildTrainerQuestion`)」「判定関数 (`checkTrainerAnswer`)」の3点を同一差分で監査し、正答一意性を崩す非決定要素（シミュレーション依存）を入れない。

### 2026-02-19 05:05:12 KST
- 対象: `index.html`（EV電卓BをMDF表示専用へ整理）、`CLAUDE.md`（手動確認項目を現仕様へ更新）
- 根拠:
  - UI根拠: `index.html:1149` が `MDF` 表示のみ。`ベット更新` ボタン接続は `index.html:4399`。
  - 計算導線根拠: `updateBetEvDecision` は `index.html:2058` で `P/B` を読み、`index.html:2089` で `evbet-mdf` を更新。
  - 自動更新停止根拠: `rg -n "updateBetEvDecision" index.html` が定義行と `click` ハンドラ行のみ（input連動なし）。
- diff要約:
  - EV電卓B出力から `必要フォールド率` / `ベット単体EV` / `F - F_be` を削除し、`MDF` のみ表示に固定。
  - EV電卓Bの手動確認項目を `MDFのみ表示` と `クイックベットのfocus誘導` に更新。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `rg -n "必要フォールド率" index.html` / `rg -n "F - F_be|ベット単体EV" index.html` / `rg -o 'id="[^"]+"' index.html | sort | uniq -d` / `rg -n "Bet vs Check|checkEV|Bet vs|ベットEV（HU）" index.html || true` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算
- テスト結果:
  - `必要フォールド率` 0件、`F - F_be|ベット単体EV` 0件、重複ID 0件、禁止語 0件、`MANIFEST_OK`
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - EV電卓BのUI変更時は `rg -n "必要フォールド率|F - F_be|ベット単体EV" index.html` をコミット前ゲートに固定する。
  - 計算トリガー変更時は `rg -n "updateBetEvDecision" index.html` で input連動が混入していないことを必ず確認する。

### 2026-02-19 05:39:28 KST
- 対象: `index.html`（トレーナーを `req/MDF` 2ドリルへ固定、outs/F_beドリル撤去、EV電卓Bラベル明確化）、`CLAUDE.md`（手動確認T-2更新）
- 根拠:
  - トレーナーUI: `index.html:1491`（`req / MDF`）`index.html:1497`（`value="mdf"`）で2択化。
  - トレーナー出題ロジック: `index.html:3163`（`mode==='mdf'` のみ分岐）`index.html:3174`（req問題文を日本語状況説明へ変更）`index.html:3185`（MDF問題文）。
  - EV電卓Bラベル: `index.html:1149`（`最小防衛頻度（MDF）`）。
- diff要約:
  - トレーナーのモード選択を `req` / `MDF` の2択へ変更し、`outs` と `F_be` ドリル表記・分岐を削除。
  - reqドリル問題文を `P_after` 変数名中心の文言から、日本語の状況説明文へ置換。
  - EV電卓Bの表示ラベルを `最小防衛頻度（MDF）` に変更（計算式は未変更）。
  - `CLAUDE.md` の手動確認 `T-2` を `MDFドリル` に更新。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `git remote -v` / `rg -n "トレーナー|trainer-mode-select|buildTrainerQuestion|checkTrainerAnswer" index.html` / `rg -n "outs（ヒット率）|outsドリル|value=\"outs\"|value=\"fbe\"|F_be" index.html` / `rg -n "最小防衛頻度（MDF）|trainer-mode-select|value=\"mdf\"|reqドリル: 相手のベット後ポット|MDFドリル（純ブラフ）|buildTrainerQuestion" index.html`
- テスト結果:
  - トレーナーから `outsドリル|value="outs"|value="fbe"` を撤去できる状態。
  - EV電卓Bラベルは `最小防衛頻度（MDF）` へ更新済み。
  - 追加ゲート（禁止語/重複ID/manifest/13ケース再計算）はコミット前に実行して記録。
- 再発防止:
  - トレーナー変更時は `rg -n "value=\"outs\"|value=\"fbe\"|outsドリル" index.html` をゼロ確認してから完了扱いにする。
  - 問題文変更時は `rg -n "P_after=.*reqドリル|reqドリル: P_after" index.html` を実行し、変数名直書き文言の再混入を防ぐ。

### 2026-02-19 05:42:13 KST
- 対象: `index.html`（トレーナー履歴から `outs/F_be` 旧モード記録を除外）
- 根拠:
  - 履歴ロード関数: `index.html:3122` `loadTrainerHistory`
  - モード限定フィルタ: `index.html:3134`（`mode === 'req' || mode === 'MDF'`）
- diff要約:
  - `loadTrainerHistory` にモード判定を追加し、`req/MDF` 以外の履歴行（旧 `outs` / `F_be`）を表示対象から除外。
- 実行コマンド: `date` / `rg -n "function loadTrainerHistory|supportedMode|mode === 'req'|mode === 'MDF'" index.html` / `nl -ba index.html | sed -n '3120,3140p'`
- テスト結果:
  - 旧モード履歴は `loadTrainerHistory` で読み込み対象外となり、トレーナー履歴表示は `req/MDF` のみ。
- 再発防止:
  - トレーナーモード変更時は `loadTrainerHistory` の許可モード集合を同時更新し、旧モード履歴が残らないことをレビュー項目に固定する。

### 2026-02-19 08:54:11 KST
- 対象: `index.html`（EV電卓A/トレーナー文言の日本語統一、トレーナー統計の req/MDF 分割表示）、`CLAUDE.md`（手動確認文言更新）
- 根拠:
  - EV電卓A表示: `index.html:1107`（見出し）`index.html:1109` `index.html:1112` `index.html:1115` `index.html:1118`（入力ラベル）`index.html:1123` `index.html:1124` `index.html:1125`（出力ラベル）
  - EV電卓Aエラー表示: `index.html:2010`（必須不足文言）`index.html:2017` `index.html:2023` `index.html:2028` `index.html:2041`（入力エラー文言）
  - トレーナー統計分割: `index.html:1509`（初期表示）`index.html:3158` `index.html:3169`（req/MDF別集計表示）
  - トレーナー問題文: `index.html:3184`（req）`index.html:3195`（MDF）
- diff要約:
  - EV電卓Aをプレイヤー視点の日本語文言へ変更（変数名主体の表示を縮小）。
  - トレーナー問題文をプレイヤー視点の状況説明に統一。
  - トレーナー統計を `req平均誤差` / `MDF平均誤差` の2行表示に分割。
  - 計算式・純関数・セルフテスト対象式は未変更。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `rg -n "P_after\\s*\\(|P_after=|reqドリル" index.html` / `rg -n "平均誤差" index.html` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n "Bet vs Check|checkEV|Bet vs|ベットEV（HU）" index.html || true` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算
- テスト結果:
  - 旧表記チェック: `P_after\\s*\\(|P_after=|reqドリル` は 0件
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - 文言変更時は「UIラベル」「エラー文言」「手動確認チェックリスト」の3点を同一コミットで同期し、文言ドリフトを防ぐ。
  - トレーナー統計変更時は `renderTrainerStats` のモード分割条件（`req` / `MDF`）を `loadTrainerHistory` の許可モードと同時に確認する。

### 2026-02-19 19:24:56 KST
- 対象: `index.html`（トレーナーへ練習/鍛錬モード・タイマー・時間得点を追加）、`CLAUDE.md`（手動確認にTIMEOUT/得点確認を追加）
- 根拠:
  - UI追加: `index.html:1500`（進行モード）`index.html:1506`（制限秒数）`index.html:1517`（残り時間表示）
  - タイマー制御: `index.html:3229`（`stopTrainerTimer`）`index.html:3261`（モード変更時リセット）`index.html:3382`（鍛錬タイマー開始）`index.html:3291`（TIMEOUT処理）
  - 得点処理: `index.html:3275`（得点式）`index.html:3446`（回答時に得点/回答時間表示）`index.html:3185`（履歴に得点表示）`index.html:3215`（req/MDF平均得点）
  - 切替イベント: `index.html:4631` `index.html:4635` `index.html:4639`（切替時に `resetTrainerSessionState`）
- diff要約:
  - トレーナーに `練習`（時間無制限）/`鍛錬`（デフォルト8秒）を追加。
  - 鍛錬では残り時間を表示し、時間切れ時は `TIMEOUT` と 0点で問題終了・履歴保存。
  - 回答時に `回答時間` と `得点(0-100)` を表示し、履歴保存。
  - 統計を req/MDF別の `平均得点（直近20）` 表示へ拡張（平均誤差も併記）。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `git remote -v` / `rg -n "trainer-mode-select|drawTrainerQuestion|checkTrainerAnswer|renderTrainerStats|trainerHistory" index.html` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n "Bet vs Check|checkEV|Bet vs|ベットEV（HU）" index.html || true` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算
- テスト結果:
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - 進行モード変更時は `resetTrainerSessionState` で `clearInterval` とUI初期化が呼ばれていることを必須確認する。
  - 新規トレーナー機能追加時は `load/save/render/統計` の4点（永続化・表示・集計）を同時監査し、片落ちを防ぐ。

### 2026-02-19 20:58:11 KST
- 対象: `index.html`（答え合わせ時の解法表示・鍛錬得点内訳表示・TIMEOUT時の正答/解法表示）、`CLAUDE.md`（手動確認T項目を更新）
- 根拠:
  - 解法生成: `index.html:3304` `buildTrainerSolutionHtml`（req/MDFの式・途中値・代入計算）
  - 回答時表示: `index.html:3492`（解法組み立て）`index.html:3495`（鍛錬のaccuracy/speed/合成）`index.html:3497`（feedbackへ出力）
  - TIMEOUT表示: `index.html:3335`（0点理由 + 正答 + 解法 + 内訳）
  - 数値保持: `index.html:3364` `index.html:3370` `index.html:3388`（req/MDFの途中値を問題オブジェクトへ保持）
- diff要約:
  - 答え合わせで req/MDF 両方に「解法（式＋途中値＋数値代入）」を必ず表示。
  - 鍛錬モードでは得点内訳（accuracy/speed/合成）を表示。
  - TIMEOUTでも `正答` と `解法` を表示し、0点理由を残す。
  - 計算式・純関数・EVセルフテスト13件の式は変更なし。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `rg -n "computeTrainerScore|checkTrainerAnswer|handleTrainerTimeout|renderTrainerStats|trainer-feedback|trainer-history" index.html` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算 / `git diff`
- テスト結果:
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - トレーナー結果表示変更時は `checkTrainerAnswer` と `handleTrainerTimeout` の両方で `正答+解法` が出ることを必須確認する。
  - 速度加点導入時は `accuracy/speed/合成` の各値を同一feedbackで確認し、TIMEOUT時は0点内訳へ固定する。

## 引継ぎサマリ（最新）
- 正規リポジトリ: `/mnt/c/repos/popker`
- 正規リポジトリ（Windows）: `C:\repos\popker`
- 現在の未コミット変更: `index.html`, `CLAUDE.md`
- 静的監査: `DUP_IDS []`, `MISSING_IDS []`, 禁止語（Bet vs Check / ベットEV（HU） / checkEV / Bet vs）0件
- 既知の未解決: ブラウザ目視確認（EV電卓BのMDF表示 / トレーナーreq・MDFの2モード / Settingsの `セルフテスト: 13/13 PASS` 表示）が未回収
- 次アクション: ユーザー目視結果（PASS/FAIL）を転記し、未解決をクローズ後にコミット・push

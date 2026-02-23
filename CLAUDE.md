# CLAUDE.md

## 実装ルール
1. 変更前に `rg` / `sed` で該当箇所を特定し、根拠行を確認する。
2. 最小差分で修正し、既存行を残したままの重複追記をしない。
3. HTMLの `id` を重複させない。
4. 「式を触らない」指定タスクでは、計算式・関数構造・イベント接続を変更しない。
5. 修正後は必ず検証コマンドを実行し、結果を確認する。
6. ユーザーへ python3/rg/sed/curl 等のコマンド実行を依頼しない。依頼できるのは `git push` と結果確認（目視）だけ。検証・修正・コミット・ログ採取はCODEXが実行し、ログを添えて報告する。
7. 同じ概念（例: ICMの行動順）は導線ごとに別ロジックを作らず、共通関数（`getIcmPreAllInActionRank` / `canIcmPlayerActBeforeAllIn`）を必ず再利用する。候補表示だけ整列しても、`残り全員フォールド` など別導線が座席順のままだと再発する。
8. ICMの新スポット追加時は、問題文（prompt）・アクション行（DOM）・計算結果（`call-amount`）の3点を必ず同時に監査する。どれか1つだけ満たしても完了扱いにしない。
9. モバイル表示不具合の再発防止として、`switchTab('icm-tab')` 直後の `renderIcmTableVisual()` 呼び出し有無と、`#icm-table-visual[data-seat-count]` がプレイヤー数と一致するかを毎回確認する。
10. 混合出題は「存在する」だけでなく偏り監査を行う。`lastIcmDrillSpotType` により `raiseShove`/`directShove` の優先順を交互にし、片側のみ連続固定化する経路を残さない。

## チェックリスト（毎回）
### 手動確認（ブラウザ）
1. B-1（MDF更新）: EV電卓で `P` `B` を入力して `ベット更新` を押す。期待結果は `evbet-mdf` が更新される。根拠は `index.html:1114` `index.html:2002` `index.html:4522`。
2. B-2（クイックベット誘導）: EV電卓で `P` 空欄のまま `1/2P` などを押す。期待結果は `evbet-error` に `先にPを入力` が出て `evbet-pot` へfocus。根拠は `index.html:2036` `index.html:2041` `index.html:4517`。
3. T-1（MDF固定）: トレーナー見出しに `即答ドリル（MDF）` が表示され、`req` の選択UIが存在しない。根拠は `index.html:1431` `index.html:1464` `index.html:3245`。
4. T-2（練習/鍛錬の切替）: `進行モード` を切り替えると問題状態がリセットされる。根拠は `index.html:1434` `index.html:3155` `index.html:4528`。
5. T-3（用語の意味主語化）: MDF問題文/解法で `ポット` `ベット額` `合計ポット` が表示される。根拠は `index.html:3204` `index.html:3265` `index.html:3266`。
6. T-4（鍛錬TIMEOUT）: `進行モード=鍛錬` で時間切れ時に `TIMEOUT` と `得点 0.0点`、正答/解法/得点内訳が表示される。根拠は `index.html:3215` `index.html:3223` `index.html:3312`。
7. T-5（統計）: 統計表示が `MDF平均得点` / `MDF平均誤差` のみで更新される。根拠は `index.html:1489` `index.html:3096` `index.html:3109`。
8. I-1（空欄でも計算開始）: ICM計算時に未入力の非参加者が自動でフォールド行に追加され、空欄起因の赤エラーが出ない。根拠は `index.html:3640` `index.html:4223` `index.html:4230`。
9. I-2（オールイン相手はdisabled表示）: `+ アクション追加` のプレイヤー選択でオールイン相手が `（オールイン相手/自動）` の disabled 表示になる。根拠は `index.html:3485` `index.html:3491` `index.html:3492` `index.html:3493`。
10. セルフテスト（13件）: 設定タブで `EV電卓セルフテスト` を押す。期待結果は `セルフテスト: 13/13 PASS`。根拠は `index.html:1498` `index.html:2045` `index.html:4533`。
11. I-3（表示専用の自動反映）: ICMタブの `想定勝率(%)` は入力欄ではなく表示のみで、プリフロップの `エクイティ計算` 完了時に更新される。根拠は `index.html:1367` `index.html:1369` `index.html:2437` `index.html:2481`。
12. I-4（未設定時の明示エラー）: プリフロップ未計算のまま `ICM計算` を押すと `先にプリフロップでエクイティ計算...` が `icm-error` に表示される。根拠は `index.html:4199` `index.html:4202` `index.html:4203`。
13. I-5（ヒーローハンド表示）: ICMタブに `ヒーロー` 表示があり、プリフロップ計算済みハンド（例: `AsKs`）が反映される。根拠は `index.html:1368` `index.html:2439` `index.html:2455` `index.html:2481`。
14. I-6（ICM卓ビュー）: ICMタブに楕円卓が表示され、席ごとに `P番号/ポジション/スタック/手札/アクション` が表示される。ヒーロー席は強調され、`BTN/SB/BB` はバッジ色で識別できる。根拠は `index.html:1492` `index.html:1494` `index.html:3591` `index.html:3608` `index.html:3617` `index.html:3627`。
15. I-7（ICMドリル答え非表示）: `出題` 直後は ICM結果ブロック（必要勝率/想定EV差）が非表示で、問題文にも必要勝率が出ない。根拠は `index.html:1044` `index.html:3954` `index.html:4075` `index.html:4077`。
16. I-8（ICMドリル回答時の根拠表示）: `コール/フォールド` 回答後にだけ `必要勝率 / foldEV / callEV / EV差` が表示される。未出題回答では `先に「出題」を押してください。` が表示される。根拠は `index.html:4080` `index.html:4082` `index.html:4093`。
17. I-9（複数ポジション出題）: ICMドリル生成時の `allinIndex` と `heroIndex` は、行動順 `getIcmPreAllInActionRank` で `allin < hero` を満たす組からランダム選定し、`SB` / `BB` 固定はしない。根拠は `index.html:3993` `index.html:4007` `index.html:4010` `index.html:4019` `index.html:4024` `index.html:4026` `index.html:4030` `index.html:4032` `index.html:4033` `index.html:4036` `index.html:4041`。
18. I-10（オールイン前候補制限）: `+ アクション追加` のプレイヤー候補はオールイン相手より前に行動する座席のみを表示し、行動順（UTG→…）で並ぶ。根拠は `index.html:3727` `index.html:3732` `index.html:3736` `index.html:3738` `index.html:1515`。
19. I-11（自動フォールド追加順）: `残り全員フォールド` で追加される行は、`i !== hero/allin` かつ `canIcmPlayerActBeforeAllIn(i, allinIndex)` の対象のみを `getIcmPreAllInActionRank(i)` の昇順で追加し、`UTG→…→BTN` 方向で並ぶ。根拠は `index.html:3923` `index.html:3943` `index.html:3947` `index.html:3948` `index.html:3949` `index.html:3954` `index.html:3955`。
20. I-12（残り全員フォールドのno-op明示）: `残り全員フォールド` で追加対象が0人のときは、何も起きない状態にせず `icm-error` に明示メッセージを表示する。根拠は `index.html:3959` `index.html:3960`。
21. I-13（レイズ→オールイン混合出題）: ICMドリルは `raiseShove` と `directShove` を混合し、`raiseShove` のときは `raiseTo` を `2.0` / `2.5` からのみ選び、問題文に `レイズto` を明記する。根拠は `index.html:4128` `index.html:4152` `index.html:4218` `index.html:4219`。
22. I-14（追加コール額の成立条件）: ICMドリル問題は `call-amount > 0` を満たすケースのみ採用し、0以下は再抽選する。根拠は `index.html:4172` `index.html:4174` `index.html:5014`。
23. I-15（iPhone卓ビュー表示ゲート）: `switchTab('icm-tab')` で `renderIcmTableVisual()` を再実行し、`[ICM_TAB_OPEN] seats=<n>` と `#icm-table-visual[data-seat-count]` が確認できる。小画面では `@media (max-width: 430px)` で席カードを縮小する。根拠は `index.html:1015` `index.html:2365` `index.html:2374` `index.html:2377` `index.html:3712` `index.html:3713`。
24. I-16（混合出題の交互優先）: 直前スポットと反対のスポットを優先して抽選し、成立しないときのみフォールバックする。根拠は `index.html:1688` `index.html:4133` `index.html:4135` `index.html:4221`。
25. I-17（iPhone代替DOM証拠）: `renderIcmTableVisual` 実行時に `data-seat-count` `data-table-rect` `data-table-display` を更新し、`[ICM_TABLE]` ログに `size/display` を含める。根拠は `index.html:3716` `index.html:3717` `index.html:3718` `index.html:3719`。
26. I-18（初期タブ固定表示）: `?tab=icm-tab` を受け取ったときに初期表示をICMタブへ切り替える。根拠は `index.html:5192` `index.html:5193`。

## 修正ログ

### 2026-02-23 19:55:00 JST
- 対象: `index.html`（ICM混合出題の交互優先、iPhone代替DOM証拠拡張、初期タブ切替）, `CLAUDE.md`（再発防止・チェック項目・実行ログ追記）
- 根拠:
  - 交互優先状態: `index.html:1688`
  - 混合出題の優先順: `index.html:4133` `index.html:4134` `index.html:4135`
  - 出題確定時の状態更新: `index.html:4221`
  - iPhone代替DOM証拠: `index.html:3716` `index.html:3717` `index.html:3718` `index.html:3719`
  - 初期ICMタブ切替: `index.html:5192` `index.html:5193`
  - マルチウェイ前提維持（第三者オールイン明示エラー）: `index.html:4930`
- diff要約:
  - `index.html`: spot混合の優先順を交互化（`lastIcmDrillSpotType` 追加）、卓ビューログに `size/display` を追加、`?tab=` で初期タブ切替対応。
  - `CLAUDE.md`: 実装ルール10、I-16〜I-18、本ログを追加。
- 実行コマンドと実行結果:
  - `powershell.exe -NoProfile -Command "Set-Location C:\repos\popker; Get-ChildItem ...; git ..."`
    - 失敗: `UtilBindVsockAnyPort:307: socket failed 1`。
  - `cd /mnt/c/repos/popker && rg -n "function switchTab|function renderIcmTableVisual|function buildIcmDrillQuestion|..." index.html`
  - `cd /mnt/c/repos/popker && nl -ba index.html | sed -n '...'`（該当行採取）
  - `cd /mnt/c/repos/popker && ls -l "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe" 2>/dev/null || echo EDGE_NOT_FOUND`
    - `EDGE_NOT_FOUND`
  - `cd /mnt/c/repos/popker && "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --window-size=390,844 --screenshot="C:\\repos\\popker\\artifacts\\icm_390x844.png" "file:///C:/repos/popker/index.html?tab=icm-tab"`
    - 失敗: `UtilBindVsockAnyPort:307: socket failed 1`
  - `cd /mnt/c/repos/popker && "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --window-size=375,667 --screenshot="C:\\repos\\popker\\artifacts\\icm_375x667.png" "file:///C:/repos/popker/index.html?tab=icm-tab"`
    - 失敗: `UtilBindVsockAnyPort:307: socket failed 1`
  - `cd /mnt/c/repos/popker && ls -l artifacts`
    - `total 0`
  - `cd /mnt/c/repos/popker && echo "[DUP_ID]" && (rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d) && echo "[FORBIDDEN]" && (rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true) && echo "[MANIFEST]" && python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
    - `[DUP_ID]` 出力なし
    - `[FORBIDDEN]` 出力なし
    - `MANIFEST_OK`
- 再発防止:
  - 混合spotは乱数任せにせず、前回spotの反対を優先することで「直オールインしか出ない」偏り再発を抑える。
  - iPhone検証ではスクショ不可時でも `data-seat-count/rect/display` と `ICM_TABLE` ログを必ず残し、DOMが生成済みか・不可視かを切り分ける。

### 2026-02-23 02:56:00 JST
- 対象: `index.html`（iPhone卓ビュー再描画/レスポンシブ化、ICMドリル raise→shove 混合生成）, `CLAUDE.md`（チェックリスト・再発防止・実行ログ追記）
- 根本原因:
  - iPhone卓ビュー: `switchTab` がタブ切替時に `renderIcmTableVisual` を呼ばない実装で、ICMタブ表示直後の再描画トリガーが無かった。根拠: 変更前 `index.html:2334` 付近（再描画呼び出しなし）。
  - ドリル直オールイン固定: `buildIcmDrillQuestion` は `allinRank < heroRank` の組のみ抽選し、`clearIcmActionRows(); addIcmFoldOthers();` だけで、`raiseTo` 挿入経路が存在しなかった。根拠: 変更前 `index.html:4034` `index.html:4043` `index.html:4066` `index.html:4067`。
- 変更内容:
  - `switchTab('icm-tab')` 直後に `requestAnimationFrame` で `renderIcmTableVisual()` を必ず実行し、`[ICM_TAB_OPEN] seats=<n>` をログ出力。
  - `renderIcmTableVisual` で `data-seat-count` を設定し、`[ICM_TABLE] seats=<n> players=<n>` をログ出力。
  - `@media (max-width: 430px)` を追加し、`.icm-seat` 幅・フォント・バッジを縮小。
  - `buildIcmDrillQuestion` を `raiseShove` / `directShove` の混合生成に変更。
  - `raiseShove` では `raiseTo` を `2.0` / `2.5` からのみ選び、ヒーローの `raiseTo` 行をオールイン前アクションに注入。
  - 問題採用条件に `call-amount > 0` を追加。
  - 問題文にスポット種別を表示（`【レイズto x.xx】...` / `【直オールイン】...`）。
- 根拠行:
  - 小画面CSS: `index.html:1015`
  - ICMタブ再描画: `index.html:2365` `index.html:2372` `index.html:2374`
  - seat数ログ: `index.html:3712` `index.html:3713` `index.html:3714`
  - raise/direct 候補抽選: `index.html:4053` `index.html:4062` `index.html:4064`
  - pre-allin注入（raiseTo 2.0/2.5固定）: `index.html:4072` `index.html:4079` `index.html:4096` `index.html:4128` `index.html:4152`
  - call-amount > 0 条件: `index.html:4172` `index.html:4174`
  - 問題文のスポット明記: `index.html:4218` `index.html:4219` `index.html:4221`
  - 2人ショーダウン前提維持（第三者オールイン明示エラー）: `index.html:4929` `index.html:4930`
- 実行コマンドと結果:
  - `powershell.exe -NoProfile -Command "Set-Location C:\repos\popker; git rev-parse --show-toplevel"`
    - 失敗: `git` が `CommandNotFoundException`。
  - `powershell.exe -NoProfile -Command "$candidates = @('C:\Program Files\Git\cmd\git.exe', ... )"`
    - 失敗: `UtilBindVsockAnyPort:307: socket failed 1`（PowerShell不安定）。
  - 以降は切替（bash）:
  - `cd /mnt/c/repos/popker && rg -n "function switchTab|function renderIcmTableVisual|function buildIcmDrillQuestion|function startIcmDrillQuestion|function submitIcmDrillAnswer|function calculateICM|function readIcmPreAllInActions|function addIcmActionRow|ICM_PRE_ALLIN_ACTION_ORDER|getIcmPreAllInActionRank|canIcmPlayerActBeforeAllIn|raiseTo|callTo|2人ショーダウン" index.html`
  - `cd /mnt/c/repos/popker && nl -ba index.html | sed -n '2280,2395p;3555,3675p;3990,4165p;4510,4865p'`
  - `cd /mnt/c/repos/popker && rg -n "\\.icm-seat|#icm-table-visual|@media \\(max-width: 430px\\)" index.html`
  - `cd /mnt/c/repos/popker && nl -ba index.html | sed -n '940,1165p;2550,2640p;5050,5190p'`
  - `cd /mnt/c/repos/popker && node -e "try{require('playwright');console.log('PLAYWRIGHT_OK')}catch(e){console.log('PLAYWRIGHT_MISSING')}"`
    - `/bin/bash: node: command not found`
  - `cd /mnt/c/repos/popker && python3 - <<'PY' ...`
    - `PLAYWRIGHT_PY_MISSING`
  - `cd /mnt/c/repos/popker && echo "[DUP_ID]" && (rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d) && echo "[FORBIDDEN]" && (rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true) && echo "[MANIFEST]" && python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
    - `[DUP_ID]` 出力なし
    - `[FORBIDDEN]` 出力なし
    - `MANIFEST_OK`
- 再発防止:
  - ICMドリル改修時は `buildIcmDrillQuestion` で `spotType` と `raiseTo` の両方を返し、`startIcmDrillQuestion` の prompt に同じ値を表示して、生成内容と表示内容の不一致を防ぐ。
  - `raiseShove` 生成では `applyIcmDrillPreAllInActions` 経由でのみ pre-allin 行を作り、`raiseTo` が `2.0/2.5` 以外になる経路を作らない。
  - iPhone表示監査は、`switchTab('icm-tab')` 実行時ログ (`[ICM_TAB_OPEN]`) と `#icm-table-visual[data-seat-count]` の一致確認を必須化する。

### 2026-02-22 22:56:00 JST
- 対象: `index.html`（`addIcmFoldOthers` no-op明示追加）, `CLAUDE.md`（再発防止ルール・実行ログ追記）
- 根拠:
  - 行動順定義: `index.html:3566`
  - オールイン前判定: `index.html:3606`
  - 候補表示の行動順ソート: `index.html:3727` `index.html:3732` `index.html:3742`
  - 自動フォールド追加順（rankソート）: `index.html:3923` `index.html:3947` `index.html:3954`
  - no-op明示追加: `index.html:3959` `index.html:3960`
  - ドリル抽選（SB/BB固定解除）: `index.html:4011` `index.html:4034` `index.html:4043`
  - 2人ショーダウン前提の明示エラー（第三者オールイン）: `index.html:4828` `index.html:4829`
- diff要約:
  - `index.html`: `addIcmFoldOthers` に「追加対象0件」の明示エラー分岐を追加（silent no-op防止）。
  - `CLAUDE.md`: 実装ルール7、チェックリストI-12、今回の実行ログを追記。
- 実行コマンドと実行結果:
  - `powershell.exe -NoProfile -Command "Set-Location C:\repos\popker; git rev-parse --show-toplevel; git status -sb; git log -1 --oneline; git show -1 --stat"`
    - `git` が `PowerShell` で解決できず失敗（`CommandNotFoundException`）。
  - `cd /mnt/c/repos/popker && git rev-parse --show-toplevel && git status -sb && git log -1 --oneline && git show -1 --stat`
    - `/mnt/c/repos/popker`
    - `## main...origin/main [ahead 7]`
    - `759b405 fix icm action order and multi-position drill generation`
  - `cd /mnt/c/repos/popker && git grep -n "function addIcmFoldOthers" -- index.html && git grep -n "function appendIcmActionPlayerOptions" -- index.html && git grep -n "ICM_PRE_ALLIN_ACTION_ORDER" -- index.html && git grep -n "function getIcmPreAllInActionRank" -- index.html && git grep -n "function canIcmPlayerActBeforeAllIn" -- index.html && git grep -n "function buildIcmDrillQuestion" -- index.html && git grep -n "function calculateICM" -- index.html && git grep -n "indexOf('sb')" -- index.html && git grep -n "indexOf('bb')" -- index.html`
    - `addIcmFoldOthers`: `index.html:3923`
    - `appendIcmActionPlayerOptions`: `index.html:3727`
    - `buildIcmDrillQuestion`: `index.html:4011`
    - `calculateICM`: `index.html:4610`
    - `indexOf('sb')` / `indexOf('bb')`: `index.html:4575` `index.html:4576`（`renderIcmPlayerActionSummary` 内）
  - `cd /mnt/c/repos/popker && nl -ba index.html | sed -n '3718,3765p;3920,3972p;4011,4060p;4818,4840p'`
    - 行動順ソート・no-op明示・multi-position抽選・第三者オールイン明示エラーを確認。
  - `powershell.exe -NoProfile -Command "Set-Location C:\repos\popker; (Select-String -Path .\index.html -Pattern 'id=\"[^\"]+\"' -AllMatches).Matches.Value | Sort-Object | Group-Object | Where-Object { $_.Count -gt 1 } | Select-Object -ExpandProperty Name"`
    - WSL側エラーで失敗（`UtilBindVsockAnyPort: socket failed 1`）。
  - `cd /mnt/c/repos/popker && echo "[DUP_ID]" && (rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d) && echo "[FORBIDDEN]" && (rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true) && echo "[MANIFEST]" && (python -c "import json; json.load(open('manifest.json','r',encoding='utf-8')); print('MANIFEST_OK')" 2>/tmp/manifest_err.log || (cat /tmp/manifest_err.log && python3 -c "import json; json.load(open('manifest.json','r',encoding='utf-8')); print('MANIFEST_OK')"))`
    - `[DUP_ID]` 出力なし（重複IDなし）
    - `[FORBIDDEN]` 出力なし（禁止語ヒットなし）
    - `[MANIFEST]` `python: command not found` 後、`python3` で `MANIFEST_OK`
- 再発防止:
  - `appendIcmActionPlayerOptions` が行動順で整列していても、`addIcmFoldOthers` が座席順追加だと順序不整合が再発する。必ず両導線で `rank` ソートを監査する。
  - `残り全員フォールド` ボタンは no-op を許容しない。追加対象が0件なら `icm-error` で明示し、ユーザーが「押したが変化なし」と誤解しない導線を維持する。

### 2026-02-22 22:23:34 JST
- 対象: `index.html`（addIcmFoldOthers / buildIcmDrillQuestion / calculateICM / ICM表記）, `CLAUDE.md`（チェックリスト・再発防止更新）
- 根拠:
  - 行動順定義: `index.html:3566`
  - 行動順rank取得: `index.html:3599`
  - オールイン前判定: `index.html:3606`
  - addIcmFoldOthers: `index.html:3923` `index.html:3943` `index.html:3945` `index.html:3947` `index.html:3948` `index.html:3954` `index.html:3955`
  - ドリル抽選: `index.html:3993` `index.html:4007` `index.html:4007` `index.html:4019` `index.html:4030` `index.html:4034` `index.html:4046`
  - calculateICM: `index.html:4774` `index.html:4807` `index.html:4813` `index.html:4819` `index.html:4824` `index.html:4831`
- diff要約:
  - `index.html`: `addIcmFoldOthers` の残り全員フォールド追加順を行動順rankソートへ変更、`calculateICM` をオールイン後プレイヤー自動フォールド化へ変更、`buildIcmDrillQuestion` を SB/BB固定から複数ポジション抽選へ変更、`アクション(オールイン前)`文言更新。
  - `CLAUDE.md`: I-9を複数ポジションへ更新、I-11追加、修正ログ追記。
- 実行コマンドと実行結果:
  - `cd /mnt/c/repos/popker && git rev-parse --show-toplevel`
    - `/mnt/c/repos/popker`
  - `cd /mnt/c/repos/popker && git status -sb`
    - `## main...origin/main [ahead 6]`
    - ` M CLAUDE.md`
    - ` M index.html`
  - `cd /mnt/c/repos/popker && git log -1 --oneline`
    - `7bb7698 docs: finalize handoff summary HEAD alignment`
  - `cd /mnt/c/repos/popker && rg -n "function addIcmFoldOthers|function buildIcmDrillQuestion|function calculateICM|function getIcmDrillPositionOrder|ICM_PRE_ALLIN_ACTION_ORDER" index.html`
    - `3566:	    const ICM_PRE_ALLIN_ACTION_ORDER = {`
    - `3601:	      return Object.prototype.hasOwnProperty.call(ICM_PRE_ALLIN_ACTION_ORDER, posValue)`
    - `3602:	        ? ICM_PRE_ALLIN_ACTION_ORDER[posValue]`
    - `3923:	    function addIcmFoldOthers()`
    - `3992:	    function getIcmDrillPositionOrder(n)`
    - `4007:	    function buildIcmDrillQuestion()`
    - `4606:	    function calculateICM()`
  - `cd /mnt/c/repos/popker && nl -ba index.html | sed -n '3920,3965p'`
    - `addIcmFoldOthers`: フォールド追加対象の抽出・`canIcmPlayerActBeforeAllIn` 判定・`rank` 昇順ソート・`fold`追加の順序で更新済み
  - `cd /mnt/c/repos/popker && nl -ba index.html | sed -n '3978,4060p'`
    - `buildIcmDrillQuestion`: `candidatePairs` で `allin < hero` のランク条件からランダム抽選
  - `cd /mnt/c/repos/popker && rg -n "フォールドしていません \\(このツールは" index.html`
    - `（0 件）`
  - `cd /mnt/c/repos/popker && rg -o "id=\"[^\"]+\"" index.html | sort | uniq -d`
    - `（0 件）`
  - `cd /mnt/c/repos/popker && rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true`
    - `（0 件）`
  - `cd /mnt/c/repos/popker && python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
    - `MANIFEST_OK`
  - `cd /mnt/c/repos/popker && git diff --stat -- index.html CLAUDE.md`
    - ` CLAUDE.md  |  57 +++++++++++++++++++++++++++++++-`
    - ` index.html | 108 +++++++++++++++++++++++++++++++++++++++++--------------------`
    - ` 2 files changed, 129 insertions(+), 36 deletions(-)`
- 追加検証結果:
  - `calculateICM` で「オールイン後に未フォールドの3rdパーティ」は自動フォールド対象化され、`preToAllIn.remaining[i] <= eps` だけをエラー化。
  - 「フォールドしていません ...」の明示エラーは撤去。
  - `2人ショーダウン前提` の文言は `アクション(オールイン前)` で明文化。
- 再発防止:
  - `残り全員フォールド` は `hero/allin` 除外・`canIcmPlayerActBeforeAllIn` で事前対象絞り込み・`getIcmPreAllInActionRank` ソートが同時に効いているかを毎回確認する。
  - ICMドリルの出題抽選は必ず `allin < hero` の行動順ランク条件チェックを通しているかを記録し、SB/BB固定にならないことを同時監査する。
  - `calculateICM` の `preToAllIn` と `pre` の差分作用を把握し、第三者が既にオールイン前状態 (`preToAllIn.remaining[i] <= eps`) の場合のみエラーにし、他は自動フォールド扱いとする前提を崩さない。

### 2026-02-22 20:45:30 KST
- 対象: `index.html`（I-10根拠の再監査）、`CLAUDE.md`（Max作業ログと再発防止追記）
- 根拠:
  - 行動順定義: `index.html:3566`
  - 行動順rank取得: `index.html:3599`
  - 後続席除外判定: `index.html:3606` `index.html:3732`
  - 候補行動順ソート: `index.html:3742`
  - オールイン相手disabled表示: `index.html:3749` `index.html:3750`
  - 追加不能時の明示エラー: `index.html:3845` `index.html:3851`
- diff要約:
  - `index.html`: 追加修正なし（I-10実装が差分上で維持されていることを再確認）。
  - `CLAUDE.md`: 今回のMax作業の実行コマンドと実出力、監査観点の再発防止を追記。
- 実行コマンドと実出力:
  - `pwd`
    - `/mnt/c/repos/popker`
  - `git rev-parse --show-toplevel`
    - `/mnt/c/repos/popker`
  - `git status -sb`
    - `## main...origin/main`
    - ` M CLAUDE.md`
    - ` M index.html`
  - `git diff --name-only`
    - `CLAUDE.md`
    - `index.html`
  - `git diff --stat -- index.html CLAUDE.md`
    - `CLAUDE.md  | 167 +++++++++++++++-`
    - `index.html | 666 ++++++++++++++++++++++++++++++++++++++++++++++++++++---------`
    - `2 files changed, 739 insertions(+), 94 deletions(-)`
  - `rg -n "ICM_PRE_ALLIN_ACTION_ORDER|getIcmPreAllInActionRank|canIcmPlayerActBeforeAllIn|appendIcmActionPlayerOptions|addIcmActionRow" index.html`
    - `3566:	    const ICM_PRE_ALLIN_ACTION_ORDER = {`
    - `3599:	    function getIcmPreAllInActionRank(playerIndex) {`
    - `3606:	    function canIcmPlayerActBeforeAllIn(playerIndex, allinIndex) {`
    - `3727:    function appendIcmActionPlayerOptions(selectEl, n) {`
    - `3732:        if (Number.isFinite(allinIndex) && i !== allinIndex && !canIcmPlayerActBeforeAllIn(i, allinIndex)) {`
    - `3742:      options.sort((a, b) => a.rank - b.rank);`
    - `3838:			    function addIcmActionRow(preset = {}) {`
  - `nl -ba index.html | sed -n '3550,3770p'`
    - `ICM_PRE_ALLIN_ACTION_ORDER` / `getIcmPreAllInActionRank` / `canIcmPlayerActBeforeAllIn` / `appendIcmActionPlayerOptions` の実装を確認。
  - `nl -ba index.html | sed -n '3835,3860p'`
    - `addIcmActionRow` で無候補時に `setIcmError` を出して停止することを確認。
  - `rg -o 'id="[^\"]+"' index.html | sort | uniq -d`
    - 出力なし
  - `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true`
    - 出力なし
  - `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
    - `MANIFEST_OK`
  - `rg -n "icm-trainer-start-btn|buildIcmTrainerQuestion|submitIcmTrainerAnswer" index.html CLAUDE.md || true`
    - `CLAUDE.md:145:  - \`rg -n "icm-trainer-start-btn|buildIcmTrainerQuestion|submitIcmTrainerAnswer" index.html\``
    - `CLAUDE.md:156:  - 旧試作名 (\`icm-trainer*\`) の再混入を防ぐため、毎回 \`rg -n "icm-trainer-start-btn|buildIcmTrainerQuestion|submitIcmTrainerAnswer" index.html\` をゲート化する。`
  - `rg -n "icm-trainer-start-btn|buildIcmTrainerQuestion|submitIcmTrainerAnswer" index.html || true`
    - 出力なし
  - `rg --files | rg '(^|/)(package\.json|playwright\.config\.|cypress\.config\.|vite\.config\.|webpack\.config\.|Makefile|pytest\.ini|tox\.ini)$' || true`
    - 出力なし
  - `git diff --stat -- index.html CLAUDE.md`（ログ追記後の再確認）
    - `CLAUDE.md  | 233 ++++++++++++++++++++-`
    - `index.html | 666 ++++++++++++++++++++++++++++++++++++++++++++++++++++---------`
    - `2 files changed, 805 insertions(+), 94 deletions(-)`
- テスト結果:
  - I-10要件（行動順ソート + 後続席除外 + allin disabled表示）はコード上で成立。
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`。
  - 旧試作キーワードは `index.html` 0件（`CLAUDE.md` は過去ログ由来の記録のみ）。
  - lint/build/E2E 相当の設定ファイルは検出されず（追加自動検証なし）。
- 再発防止:
  - I-10監査は `appendIcmActionPlayerOptions` の `continue` 条件（後続除外）と `options.sort`（行動順）の2点を必ず同時確認する。
  - `ICM_POSITION_OPTIONS` に `none` が含まれる事実（`index.html:3554`）と、rank不明時に `canIcmPlayerActBeforeAllIn` が `true` を返す事実（`index.html:3611` `index.html:3612`）を監査観点として固定し、候補制限異常時は最初にここを確認する。

### 2026-02-21 18:51:47 KST
- 対象: `index.html`（I-10の根拠再確認）、`CLAUDE.md`（実行コマンドと実出力の一致ログ）
- 根拠:
  - 行動順定義: `index.html:3566`
  - 行動順rank取得: `index.html:3599`
  - 後続席除外判定: `index.html:3606` `index.html:3732`
  - 候補行動順ソート: `index.html:3742`
- diff要約:
  - 実装差分は追加せず、I-10が「後続席除外 + 行動順ソート」で成立していることを再検証。
  - `CLAUDE.md` に実行コマンドと実出力をそのまま記録し、ログ矛盾を解消。
- 実行コマンドと実出力:
  - `pwd`
    - `/mnt/c/repos/popker`
  - `git rev-parse --show-toplevel`
    - `/mnt/c/repos/popker`
  - `git status -sb`
    - `## main...origin/main`
    - ` M CLAUDE.md`
    - ` M index.html`
  - `rg -n "appendIcmActionPlayerOptions|canIcmPlayerActBeforeAllIn|getIcmPreAllInActionRank|ICM_PRE_ALLIN_ACTION_ORDER" index.html`
    - `3566: const ICM_PRE_ALLIN_ACTION_ORDER = {`
    - `3599: function getIcmPreAllInActionRank(playerIndex) {`
    - `3606: function canIcmPlayerActBeforeAllIn(playerIndex, allinIndex) {`
    - `3727: function appendIcmActionPlayerOptions(selectEl, n) {`
    - `3732: if (Number.isFinite(allinIndex) && i !== allinIndex && !canIcmPlayerActBeforeAllIn(i, allinIndex)) {`
    - `3742: options.sort((a, b) => a.rank - b.rank);`
  - `nl -ba index.html | sed -n '3560,3765p'`
    - `ICM_PRE_ALLIN_ACTION_ORDER` / `getIcmPreAllInActionRank` / `canIcmPlayerActBeforeAllIn` / `appendIcmActionPlayerOptions` の実装を確認。
  - `rg -o 'id="[^"]+"' index.html | sort | uniq -d`
    - 出力なし
  - `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true`
    - 出力なし
  - `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
    - `MANIFEST_OK`
  - `python3 - <<'PY' ...`（提示スニペット原文）
    - `セルフテスト(式再計算): 13/13 PASS`
  - `git diff --stat -- index.html CLAUDE.md`
    - `CLAUDE.md  | 121 ++++++++++-`
    - `index.html | 666 ++++++++++++++++++++++++++++++++++++++++++++++++++++---------`
    - `2 files changed, 693 insertions(+), 94 deletions(-)`
- テスト結果:
  - I-10の要件（候補の後続席除外 + 行動順ソート）はコード上で成立。
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`、固定13ケース（提示スニペット原文）`13/13 PASS`。
- 再発防止:
  - I-10確認時は `appendIcmActionPlayerOptions` の `continue` 条件（後続除外）と `options.sort`（行動順）を同時に監査し、どちらか一方だけの確認で完了扱いにしない。

### 2026-02-21 09:35:43 KST
- 対象: `index.html`（ICMドリルの答え漏れ防止/SBvsBB固定/候補制限/日本語化）、`CLAUDE.md`（手動確認項目更新）
- 根拠:
  - 出題時の答え非表示: `index.html:1044` `index.html:3954` `index.html:4075` `index.html:4077`
  - 回答後の根拠表示: `index.html:4093`（必要勝率/foldEV/callEV/EV差）
  - SBオールイン vs BB固定: `index.html:4005` `index.html:4006` `index.html:4008` `index.html:4009`
  - オールイン前候補制限: `index.html:3732` `index.html:3733` `index.html:3738` `index.html:1515`
  - 日本語化: `index.html:1506` `index.html:1507` `index.html:3649` `index.html:3667`
- diff要約:
  - ICMドリル出題時は `icm-results` を非表示化し、回答後に再表示するように変更。
  - 出題文から必要勝率を除去し、回答後のfeedbackでのみ必要勝率とEV根拠を表示。
  - ICMドリル生成を `SBオールイン / BB判断` に固定。
  - オールイン前アクション候補を「オールイン相手より前に行動する座席」のみに制限し、後続席は候補表示しないように変更。
  - ICMドリル/卓ビュー文言の `Call/Fold/Hand/Hero/All-in` を日本語へ置換。
- 実行コマンド:
  - `pwd` / `git rev-parse --show-toplevel` / `git status -sb`
  - `rg -n "startIcmDrillQuestion|buildIcmDrillQuestion|submitIcmDrillAnswer|appendIcmActionPlayerOptions|canIcmPlayerActBeforeAllIn" index.html`
  - `rg -n "必要勝率" index.html`
  - `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d`
  - `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true`
  - `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
  - `python3` 固定13ケース再計算
- テスト結果:
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`。
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`。
  - `必要勝率` は回答表示/ICM結果側にのみ残り、出題プロンプト文字列には未使用。
- 再発防止:
  - ICMドリル改修時は `startIcmDrillQuestion` の出題文と `submitIcmDrillAnswer` の結果文を対で監査し、答え漏れを防ぐ。
  - アクション候補変更時は `appendIcmActionPlayerOptions` の除外条件と説明文を同時更新し、UIと挙動の不一致を防ぐ。

### 2026-02-21 18:36:05 KST
- 対象: `index.html`（`appendIcmActionPlayerOptions` 候補ソート順序の固定）
- 根拠:
  - 行動順ソート関数: `index.html:3566` `index.html:3601` `index.html:3606`
  - 候補生成関数: `index.html:3727`
  - no-op時の説明文: `index.html:1515`
- diff要約:
  - `appendIcmActionPlayerOptions` を候補リストとして一度構築し、`ICM_PRE_ALLIN_ACTION_ORDER` の rank 昇順で並べてから `<option>` を追加するよう変更。
- 実行コマンド:
  - `pwd`
  - `git rev-parse --show-toplevel`
  - `git status -sb`
  - `rg -n "appendIcmActionPlayerOptions|canIcmPlayerActBeforeAllIn|ICM_PRE_ALLIN_ACTION_ORDER|getIcmPreAllInActionRank" index.html`
  - `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d`
  - `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true`
  - `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
- テスト結果:
  - 重複ID: 0件、禁止語: 0件、`MANIFEST_OK`
- 再発防止:
  - ICMの「オールイン前」候補は常に `canIcmPlayerActBeforeAllIn` と `appendIcmActionPlayerOptions` の共通ロジックで導出し、order と除外条件を別々に実装しない。

### 2026-02-21 07:41:51 KST
- 対象: `index.html`（ICM卓ビューUIとICMドリル方式1の復活）、`CLAUDE.md`（手動確認項目追加）
- 根拠:
  - ICM卓UI: `index.html:1492` `index.html:1494` `index.html:3591` `index.html:3608` `index.html:3617` `index.html:3627`
  - ICMドリル: `index.html:1497` `index.html:1501` `index.html:3918` `index.html:3959` `index.html:3978` `index.html:4012` `index.html:4022` `index.html:4967`
  - 方式1固定（想定勝率の入力不可・プリフロップ反映）: `index.html:1486` `index.html:1488` `index.html:2572` `index.html:2582` `index.html:2616`
- diff要約:
  - ICMタブに楕円卓ビュー（席・ポジション・スタック・ヒーローハンド・アクション表示、Hero/All-in強調）を追加。
  - ICMドリルパネル（`出題`/`Call`/`Fold`）を追加し、出題時にICM入力自動投入→`calculateICM()`→EV差符号で正答判定する導線を実装。
  - 回答後に `foldEV / callEV / EV差` を必ず表示し、未出題回答時は明示エラー（no-op禁止）にした。
  - 旧 `icm-trainer*` 系のUI/関数名は復活させず、`icm-drill-*` に統一。
- 実行コマンド:
  - `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `git remote -v`
  - `rg -n "ICMドリル|icm-trainer|icm-drill|icm-table-visual|renderIcmTableVisual|buildIcmDrillQuestion|submitIcmDrillAnswer" index.html`
  - `rg -n "icm-trainer-start-btn|buildIcmTrainerQuestion|submitIcmTrainerAnswer" index.html`
  - `rg -o 'id="[^"]+"' index.html | sort | uniq -d`
  - `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true`
  - `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
  - `python3` 固定13ケース再計算
- テスト結果:
  - 旧 `icm-trainer*` 残骸 0件（コマンドは終了コード1・ヒットなし）。
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`。
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`。
- 再発防止:
  - ICMドリル改修時は「正答判定が `calculateICM` のEV差に依存していること」を `buildIcmDrillQuestion` / `submitIcmDrillAnswer` の行番号で必ず確認する。
  - 旧試作名 (`icm-trainer*`) の再混入を防ぐため、毎回 `rg -n "icm-trainer-start-btn|buildIcmTrainerQuestion|submitIcmTrainerAnswer" index.html` をゲート化する。

### 2026-02-21 03:00:49 KST
- 対象: `index.html`（想定勝率の表示専用化、逆流経路削除、ヒーローハンド表示、旧試作ICM UI/関数削除）、`CLAUDE.md`（手動確認更新）
- 根拠:
  - `rg -n "id=\"assumed-winrate\"[^\\n]*type=\"number\"|handleAssumedWinrateInput|assumed-winrate.*addEventListener\\('input'" index.html`
  - `rg -n "旧試作ICM関連キーワード" index.html CLAUDE.md`（0件）
  - `nl -ba index.html | sed -n '1360,1378p'`
  - `nl -ba index.html | sed -n '2412,2492p'`
  - `nl -ba index.html | sed -n '4192,4210p'`
- diff要約:
  - `assumed-winrate` を `type=\"hidden\"` へ変更し、表示専用の `assumed-winrate-display` と `icm-assumed-hero-hand` を追加。
  - `setAssumedWinrateFromPreflop` を追加し、プリフロップ計算完了 (`setCalculatedEquity`) からのみ想定勝率/ヒーローハンドを更新。
  - 手入力経路（`handleAssumedWinrateInput`、手入力判定フラグ、inputイベント、ボタン導線）を削除。
  - ICM計算時に想定勝率未設定なら `先にプリフロップでエクイティ計算...` を明示エラー表示。
  - 旧試作ICM（UI/状態/関数/イベント）を全削除し、想定勝率への副作用経路を除去。
- 実行コマンド:
  - `pwd` / `git rev-parse --show-toplevel` / `git status -sb`
  - `rg -n "旧試作ICM関連キーワード" index.html CLAUDE.md`
  - `rg -n "id=\"assumed-winrate\"[^\\n]*type=\"number\"|handleAssumedWinrateInput|assumed-winrate.*addEventListener\\('input'" index.html`
  - `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d`
  - `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true`
  - `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK`
  - `python3` 固定13ケース再計算
- テスト結果:
  - 旧試作ICM残骸 0件。
  - 想定勝率の入力経路 0件（表示専用化を確認）。
  - 重複ID 0件、禁止語0件、`manifest.json` 構文OK。
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`。
- 再発防止:
  - ICMの想定勝率は `setCalculatedEquity -> setAssumedWinrateFromPreflop` の単方向更新のみ許可し、他導線を追加しない。
  - 廃止機能の削除時は `UI -> 状態 -> 関数 -> イベント -> CLAUDE` の順で `rg` ゼロ確認を必須化する。

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

### 2026-02-19 21:56:12 KST
- 対象: `index.html`（トレーナー出題を標準ベット比率ベースへ変更、解法の途中値を比率前提に統一）、`CLAUDE.md`（手動確認T-5/T-6/T-7を現仕様へ更新）
- 根拠:
  - 比率出題の固定: `index.html:3363` `index.html:3364` `index.html:3365` `index.html:3366` `index.html:3367`
  - 整数出題の固定: `index.html:3370`（`P` を6の倍数）`index.html:3371`（`B` を比率から整数化）
  - 正答取得の純関数利用: `index.html:3376`（`calcCallEv`）`index.html:3392`（`calcBetEv`）
  - 解法の途中値表示: `index.html:3314` `index.html:3320`（`P(ベット前)` / `B(比率)` / `P_after=P+B`）
- diff要約:
  - `buildTrainerQuestion` を `1/3P, 1/2P, 2/3P, 1.0P` からランダム出題する構成へ変更。
  - `P(ベット前)` を6の倍数で生成し、`B` を整数で出題するよう統一。
  - req/MDFの正答は `calcCallEv` / `calcBetEv` から取得し、式重複の計算実装を追加しない形で維持。
  - `buildTrainerSolutionHtml` を比率出題に合わせ、途中値（`P`/`B`/`P_after`）を必ず表示。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `git remote -v` / `rg -n "buildTrainerQuestion|randomInt\\(|buildTrainerSolutionHtml\\(|calcCallEv\\(|calcBetEv\\(" index.html` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算
- テスト結果:
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - トレーナー出題変更時は `ratioOptions` の4比率と `prePot` の6倍数化を同時に確認し、整数暗算前提を崩さない。
  - 正答計算変更時は `buildTrainerQuestion` 内で `calcCallEv` / `calcBetEv` を直接呼んでいることを確認し、独自再実装を入れない。

### 2026-02-19 22:41:04 KST
- 対象: `index.html`（トレーナー出題文の比率ラベル表示を進行モードで出し分け）、`CLAUDE.md`（手動確認にT-8/T-9を追加）
- 根拠:
  - 出題分岐: `index.html:3361`（`buildTrainerQuestion(mode, sessionMode)`）`index.html:3363`（`normalizedSessionMode`）`index.html:3364`（`showRatioLabelInPrompt`）
  - 練習/鍛錬の文言分岐: `index.html:3384` `index.html:3385` `index.html:3386`（req）`index.html:3402` `index.html:3403` `index.html:3404`（MDF）
  - 進行モード連携: `index.html:3419`（`sessionMode`取得）`index.html:3432`（`buildTrainerQuestion(selectedMode, sessionMode)`）
  - 解法維持: `index.html:3304` `index.html:3314` `index.html:3320`（比率ラベル・途中値・代入結果を継続表示）
  - 純関数利用維持: `index.html:3378`（`calcCallEv`）`index.html:3396`（`calcBetEv`）
- diff要約:
  - `buildTrainerQuestion` に `sessionMode` 引数を追加し、`showRatioLabelInPrompt` で出題文のみを条件分岐。
  - 練習モードでは従来どおり比率ラベル（`1/3P` など）を表示。
  - 鍛錬モードでは比率ラベルを非表示にし、`P` と `B` の数値だけを表示。
  - 解法表示・正答計算・得点/TIMEOUT系ロジックは変更なし。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `git remote -v` / `rg -n "buildTrainerQuestion\\(|drawTrainerQuestion\\(|trainerSessionMode|promptHtml|ratioLabel" index.html` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算
- テスト結果:
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - 出題文の仕様変更は `buildTrainerQuestion` に閉じ、`buildTrainerSolutionHtml` の表示仕様と混線させない。
  - 進行モード依存の文言変更時は `drawTrainerQuestion` から `sessionMode` が渡っていることを必須確認し、片側モードのみ反映漏れを防ぐ。

### 2026-02-20 04:00:23 KST
- 対象: `index.html`（EV電卓C撤去、A/B更新ボタン配置変更、A文言簡潔化、プリフロップ見出し変更、ICMアクション制約強化、トレーナーMDF固定）、`CLAUDE.md`（手動確認を現仕様へ更新）
- 根拠:
  - EV電卓C撤去: `rg -n "機能C: Outs|Outs更新|evouts-|calcOuts|updateOuts|combination\\(" index.html` が0件
  - A/Bボタン配置: `index.html:1134`（コールEV更新）`index.html:1160`（ベット更新）`index.html:4561` `index.html:4562`（click接続）
  - A文言簡潔化: `index.html:1108` `index.html:1110` `index.html:1113` `index.html:1121` `index.html:1122` `index.html:1127` `index.html:1128`
  - 入力連動停止（ボタン押下のみ）: `rg -n "addEventListener\\('input', updateCallEvDecision\\)|addEventListener\\('input', updateBetEvDecision\\)|addEventListener\\('change', updateBetEvDecision\\)" index.html` が0件
  - プリフロップ見出し: `index.html:1168`（`対想定レンジ`）
  - ICM制約とエラー文言: `index.html:3485` `index.html:3497` `index.html:3567` `index.html:4261` `index.html:4314` `index.html:4610`
  - トレーナーMDF固定: `index.html:1467`（即答ドリル説明）`index.html:1489`（初期統計）`index.html:3036` `index.html:3096` `index.html:3198` `index.html:3245` `index.html:3274`
  - セルフテスト13件維持: `index.html:2079`（`runEvCalculatorSelfTests`）でOutsケース削除後にA/Bケース追加
- diff要約:
  - EV電卓の機能C（Outs）をUI/ボタン/イベント/関数/セルフテストから削除。
  - `コールEV更新` を機能A直下、`ベット更新` を機能B直下へ移動し、旧横並び更新バーを撤去。
  - 機能Aの入力/出力文言を「ポット」「ベット額（=コール額）」中心に置換し、未マッチ返却を詳細（任意）へ隔離。
  - ICMでオールイン相手をアクション行プレイヤー選択から除外し、該当エラー文言を「何をすべきか」が伝わる文面へ更新。
  - トレーナーのreq導線（UI/ロジック/統計/履歴フィルタ）を撤去し、MDFのみへ固定。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `rg -n "機能C: Outs|Outs更新|evouts-|calcOuts|updateOuts|C-1|C-2" index.html CLAUDE.md` / `rg -n "コールEV更新|ベット更新" index.html` / `rg -n "P_after|未コールで返ってくる|返却" index.html` / `rg -n "プリフロップエクイティ（HU）|対想定レンジ" index.html` / `rg -n "アクション\\(オールイン前\\)|自動オールイン|非対応" index.html` / `rg -n "即答ドリル（req|ドリル種別\\s+req|req平均" index.html` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算 / `git diff -- index.html CLAUDE.md`
- テスト結果:
  - `index.html` 側でOuts関連参照は0件、重複ID 0件、`MANIFEST_OK`
  - 固定ケース再計算: `セルフテスト(式再計算): 13/13 PASS`
  - commit/push は未実施（停止条件どおり）
- 再発防止:
  - 機能削除時は UI → 関数 → イベント → セルフテスト → CLAUDE手動確認 の順で `rg` ゼロ確認を固定し、削除漏れを防ぐ。
  - トレーナーのモード縮退（複数→単一）時は `loadTrainerHistory`・`renderTrainerStats`・`buildTrainerQuestion` の3点を同一修正で合わせ、旧モード文字列を残さない。

### 2026-02-20 05:27:31 KST
- 対象: `index.html`（EV電卓A UI撤去、MDF見出し統一、ICM空欄時の自動フォールド反映、オールイン相手のdisabled表示、MDF問題文/解法の意味主語化）、`CLAUDE.md`（手動確認をA/C/req撤去後の現仕様へ更新）
- 根拠:
  - EV-A UI撤去: `rg -n "機能A:" index.html` が0件、`rg -n "evcalc-calc-call-btn" index.html` が0件
  - MDF見出し: `index.html:1107`（`MDF（最小防衛頻度）`）
  - プリフロップ統一: `index.html:1136`（`対想定レンジ`）
  - トレーナーMDF固定: `rg -n "trainer-mode-select|即答ドリル（req|req（必要勝率）" index.html` が0件
  - MDF用語: `index.html:3172`（解法 `ポット/ベット額/合計ポット`）`index.html:3233` `index.html:3234`（問題文）
  - ICM空欄OK: `index.html:3640`（`addIcmFoldOthers`）`index.html:4223`（計算前自動実行）
  - ICM disabled表示: `index.html:3491`（`（オールイン相手/自動）`）`index.html:3492`（`disabled = true`）
- diff要約:
  - EVタブから機能A UI一式を削除し、MDFブロックのみを残した。
  - MDFブロック見出しを `MDF（最小防衛頻度）` へ統一し、更新ボタンを同ブロック直下に限定。
  - ICM計算で `addIcmFoldOthers` を内部実行し、空欄時も自動でフォールド行を追加して計算継続。
  - `+ アクション追加` のプレイヤー選択肢にオールイン相手を disabled 表示で残し、消失に見えないようにした。
  - トレーナーMDF問題文と解法を `ポット/ベット額/合計ポット` 表現に置換。
- 実行コマンド: `pwd` / `git rev-parse --show-toplevel` / `git status -sb` / `rg -n "機能A:|ベット損益分岐|機能C: Outs|Outs更新|プリフロップエクイティ（HU）|即答ドリル（req|req（必要勝率）" index.html` / `rg -n "アクション\\(オールイン前\\)|残り全員フォールド|ICM計算|自動オールイン" index.html` / `rg -o 'id=\"[^\"]+\"' index.html | sort | uniq -d` / `rg -n "Bet vs Check|checkEV|ベットEV（HU）|Bet vs" index.html || true` / `python3 -m json.tool manifest.json >/dev/null && echo MANIFEST_OK` / `python3` 固定13ケース再計算 / `git diff -- index.html CLAUDE.md`
- テスト結果:
  - 文字列ゲート（`機能A:` / `ベット損益分岐` / `機能C: Outs` / `Outs更新` / `即答ドリル（req` / `req（必要勝率）`）は `index.html` で0件
  - 重複ID 0件、禁止語 0件、`MANIFEST_OK`
  - 固定セルフテスト: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - UI撤去タスクは `id`/ボタン/イベント/文言の4観点で `rg` を分離実行し、`index.html` と `CLAUDE.md` の混在ヒットを誤判定しない。
  - ICMの選択制御変更時は「候補非表示」ではなく「disabled表示」の要件を先に固定し、`appendIcmActionPlayerOptions` と `refreshIcmActionPlayerOptionTexts` を同時更新する。

### 2026-02-20 05:31:52 KST
- 対象: `index.html`（EVセルフテスト表示名のA系ラベル除去）, `CLAUDE.md`（本エントリ追記）
- 根拠:
  - A系表示名の置換箇所: `index.html:2069` `index.html:2070` `index.html:2073` `index.html:2076` `index.html:2077` `index.html:2080`
  - 置換後表示名: `CALL1 req` `CALL1 EV` `CALL2 EV` `CALL3 req` `CALL3 EV` `CALL4 req`
- diff要約:
  - `runEvCalculatorSelfTests` の表示名を `A*` から `CALL*` へ変更し、機能A撤去後のUI表記と整合させた（式・ケース数・判定ロジックは変更なし）。
- 実行コマンド: `rg -n "runEvCalculatorSelfTests|A1 req|A4 req|B5 MDF|セルフテスト" index.html` / `nl -ba index.html | sed -n '2068,2120p'` / `python3` 固定13ケース再計算
- テスト結果:
  - 固定セルフテスト再計算: `セルフテスト(式再計算): 13/13 PASS`
- 再発防止:
  - UI撤去対象の名称がSettings出力に残らないよう、`runEvCalculatorSelfTests` の表示名も `rg` で同時監査する。

## 引継ぎサマリ（最新）
- 正規リポジトリ: `/mnt/c/repos/popker`
- 正規リポジトリ（Windows）: `C:\repos\popker`
- 現在の未コミット変更: なし（ワークツリーはクリーン）
- 最新コミット: `ca4eed9` `docs: set handoff summary to current HEAD`
- 静的監査: `DUP_IDS []`, `MISSING_IDS []`, 禁止語（Bet vs Check / ベットEV（HU） / checkEV / Bet vs）0件
- 既知の未解決: ブラウザ目視確認（I-7: 出題時に答え非表示 / I-8: 回答後の根拠表示 / I-9: SBvsBB固定 / I-10: オールイン前候補制限）が未回収
- 次アクション: push未実行。ユーザーに I-7〜I-10 を目視確認してもらい、PASS/FAIL を転記。FAIL時は表示文言と対象席ラベルを根拠に最小差分で再修正する

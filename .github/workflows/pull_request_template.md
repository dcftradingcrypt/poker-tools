# PR 概要

## 必須チェック（RESPONSE_REVIEW_CHECKLIST）
- [ ] 最新の添付ファイルを再読込みし、該当箇所を `<path>:Lx-Ly` で引用した（現物一致）。
- [ ] 否定検索で既存誤記が残っていないことを確認した（例：`Select-String -Path .\index.html -Pattern "\.flatten\("` がヒット0件）。
- [ ] 正常実装の存在を検索で確認した（例：`out.push(...flatten(v, key))` がヒット1件以上）。
- [ ] 同一主張・同一検証手順の再掲を抑止した。再掲が不可避な場合は「前回提示済み」と明示し、新情報のみを追加した。

## 追加チェック
- [ ] 根拠引用（`<path>:Lx-Ly`、最大5行×複数箇所）を本文または添付に含めた
- [ ] 禁止語なし（`TODO|暫定|一旦|FIXME|@ts-ignore|eslint-disable`）
- [ ] 構文エラー/未定義/未閉じ 0、関係ないリフォーマットなし

## Evidence
- 引用1: `<path>:Lx-Ly`
- 引用2: `<path>:Lx-Ly`

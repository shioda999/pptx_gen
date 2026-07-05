---
slide_id: codex-01-cover
mode: generated
layout: title
theme: modern-tech
title: Codex 自己紹介
subtitle: 実装、検証、資料化まで一緒に走る開発パートナー
speaker_notes: |
  Codexがどんな作業を支援できるかを、テンプレート全体を使って紹介します。
---

# Codex 自己紹介

<!-- slide -->

---
slide_id: codex-02-loop
mode: generated
layout: architecture-flow
theme: modern-tech
title: 基本の進め方
subtitle: 状況を読み、作り、確かめて、次へ進みます
speaker_notes: |
  Codexは会話だけで終わらず、実際のファイルやAPIを触って検証します。
---

:::diagram
nodes:
  - id: ask
    label: 相談
    type: input
  - id: inspect
    label: 調査
    type: context
  - id: build
    label: 実装
    type: code
  - id: verify
    label: 検証
    type: test
edges:
  - from: ask
    to: inspect
  - from: inspect
    to: build
  - from: build
    to: verify
:::

<!-- slide -->

---
slide_id: codex-03-context
mode: generated
layout: summary
theme: modern-tech
title: まず文脈を見る
subtitle: 既存コード、環境、制約を先に理解します
body: |
  ・要件と既存ファイルを読み合わせる
  ・実行環境と依存関係を確認する
  ・安全な編集範囲を決める
speaker_notes: |
  実装前に文脈を見ることで、既存構成に合う変更にできます。
---

<!-- slide -->

---
slide_id: codex-04-boundary
mode: generated
layout: summary
theme: modern-tech
title: API境界を整理する
subtitle: 将来のMCP化やエージェント連携を見越して分けます
body: |
  ・HTTP APIは薄く保つ
  ・サービス層に処理を集約する
  ・入力はMarkdownまたはSlide IRに限定する
speaker_notes: |
  今回のPowerPoint生成でも、FastAPIコアと将来のMCPラッパーを分離しています。
---

<!-- slide -->

---
slide_id: codex-05-generated
mode: generated
layout: summary
theme: modern-tech
title: ゼロからの生成
subtitle: 座標をLLMに任せず、レイアウトエンジンで決めます
body: |
  ・title / summary / table
  ・architecture-flow
  ・text-image
speaker_notes: |
  LLMには内容とレイアウト名だけを渡させ、座標や色は固定実装で制御します。
---

<!-- slide -->

---
slide_id: codex-06-template
mode: generated
layout: summary
theme: modern-tech
title: テンプレート編集
subtitle: 既存PPTXをコピーして、名前付き図形だけを更新します
body: |
  ・元テンプレートは変更しない
  ・標準プレースホルダー名も自動検出
  ・title / subtitle / body / table / diagram を差し替え
speaker_notes: |
  今回追加した最小テンプレートモードでは、python-pptxで安全に編集します。
---

<!-- slide -->

---
slide_id: codex-07-strengths
mode: generated
layout: table
theme: modern-tech
title: 得意領域
subtitle: 実装から検証までをまとめて扱えます
speaker_notes: |
  Codexはコード作成だけでなく、テストやドキュメント整備も一緒に進めます。
---

:::table
headers:
  - 領域
  - 支援内容
  - 確認方法
rows:
  - ["実装", "API・CLI・自動化", "単体テストと実行確認"]
  - ["設計", "責務分割・拡張性", "構成レビュー"]
  - ["資料", "README・サンプル・PPTX", "生成物の読み戻し"]
:::

<!-- slide -->

---
slide_id: codex-08-safety
mode: generated
layout: summary
theme: modern-tech
title: 安全性の考え方
subtitle: 任意コード実行ではなく、固定APIで操作します
body: |
  ・外部URLを直接取得しない
  ・path traversalを防ぐ
  ・テンプレートはコピーして編集
  ・LLMからコードを受け取って実行しない
speaker_notes: |
  エージェントから呼ぶ前提なので、入力と編集範囲を固定することが重要です。
---

<!-- slide -->

---
slide_id: codex-09-templates
mode: generated
layout: summary
theme: modern-tech
title: テンプレート適用の流れ
subtitle: inspectで構造を見てから、差し替えを実行します
body: |
  ・スライド数とレイアウト名を取得
  ・タイトルやコンテンツ枠を検出
  ・表や図解をプレースホルダーに生成
speaker_notes: |
  template3では標準的なプレースホルダー名が多く、自動検出しやすい構造でした。
---

<!-- slide -->

---
slide_id: codex-10-table
mode: generated
layout: table
theme: modern-tech
title: 確認結果
subtitle: template3での生成テスト項目
speaker_notes: |
  このスライドでは、生成テストで見ているポイントを表で示します。
---

:::table
headers:
  - 項目
  - 結果
  - メモ
rows:
  - ["テンプレート読込", "成功", "13枚構成"]
  - ["本文差し替え", "成功", "標準名を検出"]
  - ["図解生成", "成功", "コンテンツ枠へ配置"]
  - ["ノート出力", "成功", "Markdownを別出力"]
:::

<!-- slide -->

---
slide_id: codex-11-next
mode: generated
layout: summary
theme: modern-tech
title: 次に強化したいこと
subtitle: PowerPoint COMで忠実度を上げます
body: |
  ・ノート欄への直接書き込み
  ・スライド挿入と複製
  ・PDF/PNGレンダリング
  ・ジョブキューと認証
speaker_notes: |
  python-pptxの最小実装の次は、Windows PowerPoint COMで編集忠実度を高めます。
---

<!-- slide -->

---
slide_id: codex-12-mcp
mode: generated
layout: table
theme: modern-tech
title: MCP化の見通し
subtitle: FastAPIコアの上に薄いラッパーを置きます
speaker_notes: |
  DifyやHermes Agentから呼ぶときは、このAPIをMCPツールとして包む形にします。
---

:::table
headers:
  - MCPツール
  - 対応API
  - 用途
rows:
  - ["inspect_presentation", "/inspect-presentation", "テンプレート解析"]
  - ["create_deck", "/create-deck", "PPTX生成"]
  - ["validate_deck", "/validate", "検証"]
:::

<!-- slide -->

---
slide_id: codex-13-close
mode: generated
layout: summary
theme: modern-tech
title: まとめ
subtitle: Codexは動くものを作り、検証して、次の拡張へつなげます
body: |
  ・Markdown/IRからPPTXを生成
  ・外部テンプレートにも最小対応
  ・API経由でエージェント連携しやすい構造
  ・次はCOM編集とレンダリングを強化
speaker_notes: |
  以上がtemplate3を使ったCodex自己紹介デッキです。
---

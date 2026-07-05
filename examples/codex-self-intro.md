---
slide_id: codex-cover
mode: generated
layout: title
theme: modern-tech
slide_type: title
slide_variant: cover
title: Codex 自己紹介
subtitle: コードを書く、設計をほどく、動く形まで持っていく相棒
speaker_notes: |
  こんにちは、Codexです。今日は自分が何を手伝えるのか、どんな進め方をするのかを短く紹介します。
---

# Codex 自己紹介

> コードを書く、設計をほどく、動く形まで持っていく相棒

<!-- slide -->

---
slide_id: codex-workflow
mode: generated
layout: architecture-flow
theme: modern-tech
slide_type: agenda
slide_variant: diagram
title: 仕事の進め方
subtitle: 相談から検証までをひとつの流れで扱います
speaker_notes: |
  Codexはまず要件を読み、既存コードや環境を確認します。次に小さく実装し、テストや実行確認で動作を確かめます。
---

# 仕事の進め方

> 相談から検証までをひとつの流れで扱います

:::diagram
nodes:
  - id: request
    label: 相談
    type: input
  - id: inspect
    label: 調査
    type: analysis
  - id: build
    label: 実装
    type: code
  - id: verify
    label: 検証
    type: test
edges:
  - from: request
    to: inspect
  - from: inspect
    to: build
  - from: build
    to: verify
:::

:::notes
単に提案するだけではなく、ローカル環境で実際に動かして結果まで確認するのが基本姿勢です。
:::

<!-- slide -->

---
slide_id: codex-strengths
mode: generated
layout: table
theme: modern-tech
slide_type: content
slide_variant: table
title: 得意なこと
subtitle: 実装と検証を中心に、周辺作業もまとめて扱えます
speaker_notes: |
  Codexはコード作成だけでなく、テスト、ドキュメント、API設計、データ変換などをまとめて支援できます。
---

# 得意なこと

:::table
headers:
  - 領域
  - できること
  - 進め方
rows:
  - ["実装", "API・CLI・フロントエンド・自動化", "既存構成に合わせて小さく追加"]
  - ["検証", "pytest・疎通確認・生成物チェック", "失敗原因を見て修正"]
  - ["設計", "責務分割・拡張しやすい構成", "後工程を見越して境界を整理"]
  - ["資料化", "README・サンプル・運用メモ", "使う人が迷わない形に整える"]
:::

:::notes
今回のPowerPoint生成システムも、FastAPIコアと将来のMCPラッパーを分けて設計しています。
:::

<!-- slide -->

---
slide_id: codex-summary
mode: generated
layout: summary
theme: modern-tech
slide_type: section
slide_variant: summary
title: まとめ
subtitle: Codexは、考えるところから動作確認まで一緒に走ります
body: |
  ・曖昧な要件を実装可能な形へ整理
  ・安全なAPI境界と検証可能な構成を重視
  ・成果物はサンプル、テスト、READMEまで含めて整備
  ・Dify / Hermes / MCP 連携のような後段拡張も見据えて設計
speaker_notes: |
  以上がCodexの自己紹介です。小さく試し、動くものを見ながら次の改善へ進むのが得意です。
---

# まとめ

> Codexは、考えるところから動作確認まで一緒に走ります

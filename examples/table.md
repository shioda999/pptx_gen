---
slide_id: benchmark-results
mode: generated
layout: table
theme: modern-tech
title: 推論性能比較
subtitle: 同時実行数ごとのスループット
---

# 推論性能比較

:::table
headers:
  - 同時実行数
  - 生成速度
  - 備考
rows:
  - ["1", "10 tok/s", "低遅延"]
  - ["4", "38 tok/s", "標準運用"]
  - ["16", "114 tok/s", "高スループット"]
:::

:::notes
同時実行数を上げるとスループットは向上しますが、レイテンシとGPUメモリ使用量も確認が必要です。
:::

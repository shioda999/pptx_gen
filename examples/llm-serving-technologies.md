---
slide_id: serving-system-overview
mode: generated
layout: architecture-flow
theme: modern-tech
slide_type: title
slide_variant: diagram
title: LLMサービングを支える技術
subtitle: APIからGPU実行まで、複数の制御レイヤーが連携する
body: |
  制御プレーン
    - 認証、レート制限、モデル選択
      - テナント別ポリシー
      - SLA別キュー
  データプレーン
    - prefillとdecodeをGPU上で実行
      - KV cacheを保持
      - batchを逐次再編成
  最適化プレーン
    - batching、quantization、routingでコストを下げる
speaker_notes: |
  LLMサービングは単純なHTTPサーバーではなく、入口のAPI制御、GPU実行、メモリ管理、ルーティングが一体で動くシステムです。
---

:::diagram
nodes:
  - id: gateway
    label: API Gateway
    type: auth / quota
  - id: scheduler
    label: Scheduler
    type: batching
  - id: workers
    label: Model Workers
    type: GPU runtime
  - id: cache
    label: KV Cache
    type: memory
  - id: metrics
    label: Metrics
    type: feedback
edges:
  - from: gateway
    to: scheduler
  - from: scheduler
    to: workers
  - from: workers
    to: cache
  - from: workers
    to: metrics
  - from: metrics
    to: scheduler
:::

<!-- slide -->

---
slide_id: continuous-batching
mode: generated
layout: summary
theme: modern-tech
slide_type: content
slide_variant: text
title: Continuous Batching
subtitle: decode中のリクエスト群へ、新しいリクエストを動的に混ぜる
body: |
  目的
    - GPUを空かせない
      - decodeは1 tokenずつ進むため、待ち時間が発生しやすい
      - 完了したリクエストの枠をすぐ新規リクエストへ渡す
    - レイテンシとスループットの両立
      - 固定batchより待ち時間を短くしやすい
  動作イメージ
    - prefill
      - 入力promptをまとめて処理
      - KV cacheを初期化
    - decode
      - 生成中requestを毎step再編成
      - 終了requestを外し、新規requestを追加
  注意点
    - 長文requestが混ざるとGPUメモリを圧迫
    - priority / timeout / fairnessの設計が必要
speaker_notes: |
  Continuous batchingは、LLMサービングのスループットを大きく改善する基本技術です。固定batchではなく、生成中のリクエスト集合を毎ステップ組み替えます。
---

<!-- slide -->

---
slide_id: quantization
mode: generated
layout: table
theme: modern-tech
slide_type: content
slide_variant: table
title: Quantization
subtitle: 精度を少し落として、メモリ帯域とVRAM使用量を下げる
speaker_notes: |
  Quantizationは、重みやKV cacheの表現ビット数を下げることで、より大きなモデルや多くの同時リクエストを扱うための技術です。
---

:::table
headers:
  - 種類
  - 主な対象
  - メリット
  - 注意点
rows:
  - ["Weight-only INT8/INT4", "モデル重み", "VRAM削減、ロード高速化", "精度劣化とkernel対応"]
  - ["AWQ / GPTQ", "重み量子化", "実運用しやすい圧縮", "モデルごとの調整が必要"]
  - ["FP8", "重み/演算", "Hopper以降で高速化しやすい", "対応GPUと実装依存"]
  - ["KV cache quantization", "KV cache", "長文・多同時接続に強い", "生成品質と復元コスト"]
:::

<!-- slide -->

---
slide_id: kv-cache-aware-routing
mode: generated
layout: architecture-flow
theme: modern-tech
slide_type: content
slide_variant: diagram
title: KV Cache Aware Routing
subtitle: キャッシュが残っているworkerへ寄せて、prefillの再計算を避ける
body: |
  何を見てルーティングするか
    - prefix hash
      - system prompt
      - conversation prefix
    - worker状態
      - 空きKV blocks
      - decode負荷
      - GPU memory pressure
  効果
    - 同じprefixの再利用
      - prefill時間を削減
      - Time To First Tokenを改善
    - 長い会話の継続処理に強い
  トレードオフ
    - 局所性を優先しすぎるとworker偏りが起きる
    - cache hit率と負荷分散の重み付けが重要
speaker_notes: |
  KV cache aware routingでは、単に空いているworkerへ送るのではなく、再利用できるKV cacheがあるworkerを優先します。
---

:::diagram
nodes:
  - id: request
    label: Request
    type: prefix hash
  - id: router
    label: Router
    type: cache score
  - id: worker_a
    label: Worker A
    type: cache hit
  - id: worker_b
    label: Worker B
    type: cache miss
  - id: gpu
    label: GPU Memory
    type: KV blocks
edges:
  - from: request
    to: router
  - from: router
    to: worker_a
  - from: router
    to: worker_b
  - from: worker_a
    to: gpu
:::

<!-- slide -->

---
slide_id: serving-design-summary
mode: generated
layout: summary
theme: modern-tech
slide_type: section
slide_variant: summary
title: 設計上のまとめ
subtitle: GPUを速く使うだけでなく、待たせ方とメモリの使い方を設計する
body: |
  性能を決める軸
    - スループット
      - continuous batching
      - paged attention
      - decode step scheduling
    - メモリ効率
      - quantization
      - KV cache管理
      - prefix reuse
    - レイテンシ
      - prefill分離
      - cache aware routing
      - admission control
  運用で見るべき指標
    - TTFT
      - prefill待ち
      - queue待ち
    - tokens/sec
      - GPU utilization
      - batch occupancy
    - cache hit率
      - prefix reuse率
      - eviction頻度
speaker_notes: |
  LLMサービングは、単体最適化の寄せ集めではなく、スケジューラ、メモリ、ルーティングを合わせて設計する必要があります。
---

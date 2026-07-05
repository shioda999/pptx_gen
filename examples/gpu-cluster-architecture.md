---
slide_id: gpu-cluster-overview
mode: generated
layout: architecture-flow
theme: modern-tech
slide_type: title
slide_variant: diagram
title: GPUクラスタ構成を支える技術
subtitle: GPUを並べるだけではなく、計算・通信・保存・運用を一体で設計する
body: |
  クラスタの見方
    - GPU node
      - accelerator, CPU, RAM, local NVMe
      - PCIe / NVLink / NVSwitch
    - network fabric
      - InfiniBand / RoCE
      - leaf-spine topology
    - control plane
      - scheduler, quota, health check
      - observability and alerting
  設計の目的
    - 学習と推論のGPU利用率を上げる
    - 障害時にジョブとデータを守る
speaker_notes: |
  GPUクラスタは、GPUサーバーの集合ではなく、計算資源、通信網、ストレージ、スケジューラ、監視が結びついた分散システムとして見る必要があります。
---

:::diagram
nodes:
  - id: users
    label: Users / Jobs
    type: training, inference
  - id: scheduler
    label: Scheduler
    type: quota, placement
  - id: gpu_nodes
    label: GPU Nodes
    type: compute pool
  - id: fabric
    label: Network Fabric
    type: IB / RoCE
  - id: storage
    label: Storage
    type: dataset, checkpoint
edges:
  - from: users
    to: scheduler
  - from: scheduler
    to: gpu_nodes
  - from: gpu_nodes
    to: fabric
  - from: gpu_nodes
    to: storage
:::

<!-- slide -->

---
slide_id: gpu-node-design
mode: generated
layout: summary
theme: modern-tech
slide_type: content
slide_variant: text
title: GPUノード設計
subtitle: 1台の中のバランスが、クラスタ全体の効率を決める
body: |
  GPUとCPUの比率
    - GPUを待たせないCPU core数が必要
      - data loader
      - tokenization
      - preprocessing
    - host memoryはbatchとdataset cacheに効く
  ノード内通信
    - PCIe
      - 汎用的で構成しやすい
      - GPU間通信はtopology依存
    - NVLink / NVSwitch
      - model parallelやall-reduceに強い
      - 高価だが大規模学習で効く
  ローカルストレージ
    - NVMe scratch
      - dataset shardの一時配置
      - checkpointの書き出しバッファ
    - OS diskとは分けて管理する
speaker_notes: |
  GPUノードでは、GPU枚数だけでなく、CPU、メモリ、ノード内通信、ローカルNVMeのバランスが重要です。GPUだけ強くても、入力パイプラインや通信で詰まるとクラスタ効率は上がりません。
---

<!-- slide -->

---
slide_id: cluster-network
mode: generated
layout: architecture-flow
theme: modern-tech
slide_type: content
slide_variant: diagram
title: ネットワーク構成
subtitle: 分散学習では、GPU間通信が計算性能と同じくらい重要になる
body: |
  通信パターン
    - data parallel
      - gradient all-reduce
      - stepごとの同期が支配的
    - tensor / pipeline parallel
      - layer間やpartition間の通信
      - latencyとbandwidthの両方が効く
  ファブリック設計
    - leaf-spine
      - rack間帯域を読みやすくする
      - oversubscriptionを管理しやすい
    - failure domain
      - rack, switch, power zoneを分ける
      - placement policyと連動させる
  運用上の注意
    - congestionをメトリクスで見る
    - NCCL errorはネットワーク・driver・topologyを横断して調査する
speaker_notes: |
  分散学習ではGPUの演算速度だけでなく、all-reduceやpipeline通信の帯域と遅延が全体性能を左右します。ネットワークは後付けで直しにくいため、初期設計が重要です。
---

:::diagram
nodes:
  - id: rack_a
    label: Rack A
    type: GPU nodes
  - id: leaf_a
    label: Leaf Switch
    type: ToR
  - id: spine
    label: Spine Fabric
    type: non-blocking core
  - id: leaf_b
    label: Leaf Switch
    type: ToR
  - id: rack_b
    label: Rack B
    type: GPU nodes
edges:
  - from: rack_a
    to: leaf_a
  - from: leaf_a
    to: spine
  - from: spine
    to: leaf_b
  - from: leaf_b
    to: rack_b
:::

<!-- slide -->

---
slide_id: scheduling-and-isolation
mode: generated
layout: summary
theme: modern-tech
slide_type: content
slide_variant: text
title: スケジューリングと分離
subtitle: 高価なGPUを公平に、かつ高利用率で使うための制御層
body: |
  配置の判断材料
    - GPU type
      - H100, A100, L40Sなど
      - memory sizeとinterconnectが違う
    - topology
      - 同一ノード内に寄せる
      - 同一rack内に寄せる
      - 通信が薄いjobは分散配置も許す
    - quota and priority
      - team quota
      - preemptible job
      - production inference priority
  分離の仕組み
    - container runtime
      - CUDA driver compatibility
      - image provenance
    - MIG / time slicing
      - 小さい推論jobを詰めやすい
      - 学習jobには不向きな場合がある
    - admission control
      - 不正なresource requestを止める
      - 長時間jobの上限を設定する
speaker_notes: |
  スケジューリングは単なる空きGPU探しではありません。GPU種類、ノード内topology、ネットワーク距離、チームquota、優先度を総合して、効率と公平性のバランスを取ります。
---

<!-- slide -->

---
slide_id: storage-and-data-plane
mode: generated
layout: table
theme: modern-tech
slide_type: content
slide_variant: table
title: ストレージとデータプレーン
subtitle: GPUを止めないためには、データ供給とcheckpoint設計が重要になる
speaker_notes: |
  GPUクラスタでは、データセット読み込みとcheckpoint保存が隠れたボトルネックになりがちです。用途ごとに適したストレージ層を分けると、性能と運用性を両立しやすくなります。
---

:::table
headers:
  - レイヤー
  - 主な用途
  - 設計ポイント
  - 注意点
rows:
  - ["Object Storage", "dataset, artifact", "安価で容量を伸ばしやすい", "小さいファイル大量読み込みに弱い"]
  - ["Shared Filesystem", "共有dataset, home", "既存ワークフローと相性が良い", "metadata負荷が集中しやすい"]
  - ["Local NVMe", "scratch, cache", "GPU近くで高速に読める", "node障害で消える前提にする"]
  - ["Checkpoint Store", "学習途中の保存", "世代管理とresumeを明確にする", "書き込み集中でfabricを圧迫する"]
:::

<!-- slide -->

---
slide_id: operations-observability
mode: generated
layout: summary
theme: modern-tech
slide_type: section
slide_variant: summary
title: 運用と観測
subtitle: GPUクラスタは、使い続けながら壊れる前提で設計する
body: |
  見るべき指標
    - GPU utilization
      - SM utilization
      - memory bandwidth
      - HBM usage
    - job efficiency
      - queue wait time
      - tokens/sec or samples/sec
      - checkpoint duration
    - network health
      - retransmit
      - congestion
      - NCCL timeout
  障害対応
    - node drain
      - 異常GPUを隔離する
      - running jobへの影響を制御する
    - burn-in test
      - 新規nodeを本番投入前に負荷試験する
      - GPU memory errorとthermal issueを見る
    - capacity planning
      - GPU世代の混在を前提にする
      - trainingとinferenceの需要を分けて見る
speaker_notes: |
  GPUクラスタの運用では、単に落ちたnodeを直すだけでは足りません。利用率、待ち時間、通信エラー、checkpoint時間を継続的に観測し、故障・混雑・需要変化に対応できる仕組みが必要です。
---

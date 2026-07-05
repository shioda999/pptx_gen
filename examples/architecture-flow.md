---
slide_id: vllm-architecture
mode: generated
layout: architecture-flow
theme: modern-tech
title: vLLM推論基盤の構成
subtitle: API Gateway経由で複数のvLLM Podへリクエストを分散
speaker_notes: |
  このスライドでは、利用者からGPUクラスタまでの推論経路を説明します。
  API Gatewayで認証と負荷分散を行い、vLLM Podがリクエストを処理します。
---

# vLLM推論基盤の構成

> API Gateway経由で複数のvLLM Podへリクエストを分散

:::diagram
nodes:
  - id: user
    label: 利用者
    type: client
  - id: gateway
    label: API Gateway
    type: service
  - id: vllm
    label: vLLM Pod
    type: service
  - id: gpu
    label: GPU Cluster
    type: cluster
edges:
  - from: user
    to: gateway
  - from: gateway
    to: vllm
  - from: vllm
    to: gpu
:::

:::notes
API Gatewayが認証と負荷分散を担い、vLLM Podが推論処理を担当します。
:::

# SynerGist 项目指南

> SynerGist — 源自 "Synergy" 和 "Gist"，意指在多服务器间实现模型推理的协同精髓。

本项目是一个**DNN（深度神经网络）模型分割与分布式推理调度系统**，核心思路是将一个完整的神经网络模型（以 VGG5 为例）按层分割到多个边缘节点上，通过 Socket 通信链式传递中间结果，实现协同推理。同时使用**强化学习（PPO 算法）**自动学习最优的分割策略。

---

## 目录

- [1. 项目结构总览](#1-项目结构总览)
- [2. 核心概念](#2-核心概念)
- [3. 模块详细说明](#3-模块详细说明)
- [4. 数据流与架构图](#4-数据流与架构图)
- [5. 环境配置与依赖安装](#5-环境配置与依赖安装)
- [6. 如何运行](#6-如何运行)
- [7. 关键算法解析](#7-关键算法解析)
- [8. 配置说明](#8-配置说明)
- [9. 常见问题与注意事项](#9-常见问题与注意事项)

---

## 1. 项目结构总览

```
Partition_Scheduling/
│
├── config.py                          # 全局配置：网络地址、模型参数、RL超参数
├── server.py                          # 服务端入口：资源感知分层 + 数据分发
├── client.py                          # 客户端入口：链式推理 + 结果传递
├── utils.py                           # 工具函数：数据加载、模型构建、通信、FedAvg等
├── Scheduling.py                      # 边缘子任务调度算法
├── requirements.txt                   # Python 依赖
├── README.md                          # 项目简介
│
├── models/                            # 模型定义
│   ├── model_struct.py                #   VGG5 层级元数据（类型、通道、FLOPs）
│   └── vgg5/
│       └── vgg5.py                    #   可分割的 VGG5 模型实现
│
├── communication/                     # 通信模块
│   ├── communicator.py                #   Socket通信基类（Communicator + NodeEnd）
│   ├── kill.sh                        #   进程清理脚本
│   ├── demo_json/                     #   JSON格式Socket通信示例
│   │   ├── socket_server.py
│   │   ├── socket_client_1.py
│   │   └── socket_client_2.py
│   └── demo_send/                     #   Pickle格式链式推理演示
│       ├── server.py
│       ├── client_1.py
│       ├── client_2.py
│       └── client_3.py
│
├── strategy/                          # 分割策略
│   ├── segment_strategy.py            #   随机/资源感知分割点选择
│   └── resource_utilization.py        #   远程服务器资源采集（Paramiko SSH）
│
├── RL/                                # 强化学习主模块（PPO + 状态衍生）
│   ├── README.md                      #   RL模块说明
│   ├── correspondence.py              #   RL专用Socket通信基类
│   ├── RLEnv.py                       #   RL环境（Env + RL_Client）
│   ├── PPO.py                         #   PPO算法实现（Actor-Critic）
│   ├── RL_serverrun.py                #   ★ RL服务端入口（训练循环）
│   ├── RL_clientrun.py                #   ★ RL客户端入口
│   ├── state_derivation.py            #   滑窗状态衍生（均值+差分）
│   └── iaf_state_derivation.py        #   可逆仿射流(IAF)状态衍生
│
├── RL_multiple/                       # RL多客户端变体（结构与RL/平行）
│   ├── README.md
│   ├── correspondence.py
│   ├── RLEnv.py
│   ├── PPO.py
│   ├── RL_serverrun.py
│   └── RL_clientrun.py
│
├── RL_IAF/                            # RL + IAF状态衍生变体
│   ├── README.md
│   ├── correspondence.py
│   ├── RLEnv.py
│   ├── PPO.py
│   ├── RL_serverrun.py
│   ├── RL_clientrun.py
│   └── graph.py                       #   绘图脚本
│
├── local_inference/                   # 本地推理实验（多种变体）
│   ├── RL/                            #   DQN强化学习变体
│   │   ├── dqn.py                     #     DQN算法实现
│   │   ├── dqn_server.py              #     DQN服务端
│   │   ├── rl_server.py               #     RL服务端
│   │   ├── rl_optimize_server.py      #     优化版RL服务端
│   │   ├── optimize_dqn.py            #     优化DQN训练
│   │   ├── load_optimize_dqn.py       #     加载训练好的DQN
│   │   ├── load_model.py              #     模型加载工具
│   │   ├── derivation.py              #     GRU状态衍生
│   │   ├── data_inference.py          #     数据推理统计
│   │   ├── draw_graph.py              #     绘图
│   │   ├── client_1.py                #     客户端
│   │   ├── network_utils.py           #     网络工具
│   │   ├── resource_utilization.py    #     资源监控
│   │   └── test/test1.py
│   ├── rl_data_from_server/           #   从服务端获取数据 + Dueling DQN
│   ├── single_data_from_server/       #   单路径链式推理（数据在服务端）
│   ├── single_data_from_client/       #   单路径链式推理（数据在客户端）
│   ├── single_data_from_server_recycle/ # 带回收聚合的服务端变体
│   ├── single_data_from_server_RL/    #   Gym FederatedEnv + PPO
│   ├── multiple_task_from_server/     #   多任务 + Barrier同步
│   └── test/                          #   最小Socket测试
│
└── scientific_research_drawing/       # 科研绘图脚本
    ├── tradition.py                   #   传统方法基线绘图
    ├── contrast.py / contrast2.py     #   对比实验绘图
    ├── multiple_origin.py             #   多源状态轨迹
    ├── multiple_derivative.py         #   多源状态衍生
    ├── rl.py / rl2.py                 #   RL公式实验可视化
    └── ...
```

---

## 2. 核心概念

### 2.1 模型分割（Model Partitioning）

将一个完整的 DNN 模型（如 VGG5）按**层**拆分成多个部分，分配到不同的边缘设备上执行。

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ 设备1    │────▶│ 设备2    │────▶│ 设备3    │
│ 第0-1层  │     │ 第2-3层  │     │ 第4-6层  │
│ (Conv+Pool)    │ (Conv+Pool)    │ (Conv+Dense)
└─────────┘     └─────────┘     └─────────┘
     输入             中间激活           最终输出
```

### 2.2 VGG5 模型结构

项目使用简化版 VGG5 作为实验模型，共 7 层：

| 层索引 | 类型 | 输入通道 | 输出通道 | 说明 |
|:------:|:----:|:--------:|:--------:|:-----|
| 0 | C (Conv) | 3 | 32 | 卷积层 + BN + ReLU |
| 1 | M (MaxPool) | 32 | 32 | 最大池化层 |
| 2 | C (Conv) | 32 | 64 | 卷积层 + BN + ReLU |
| 3 | M (MaxPool) | 64 | 64 | 最大池化层 |
| 4 | C (Conv) | 64 | 64 | 卷积层 + BN + ReLU |
| 5 | D (Dense) | 4096 | 128 | 全连接层 |
| 6 | D (Dense) | 128 | 10 | 全连接层（输出分类） |

### 2.3 分割策略

项目实现了两种分割点选择策略：

- **随机分割**：随机选择中间层作为分割点
- **资源感知分割**：根据各节点的 CPU/内存/网络利用率，将计算量大的层分配给资源充足的节点

### 2.4 强化学习自动分割（PPO）

使用 PPO（Proximal Policy Optimization）算法自动学习最优分割策略：

- **状态（State）**：推理时间 + 卸载比例（经状态衍生增强为 3 倍维度）
- **动作（Action）**：连续值，映射为每组客户端的分割层位置
- **奖励（Reward）**：推理时间相对基线的改善程度
- **状态衍生**：通过滑窗计算当前值、历史均值、变化趋势，增强状态表征

### 2.5 通信协议

所有节点间通信采用 **TCP Socket + Pickle 序列化**：

```
[4字节大端长度头] + [Pickle序列化消息体]
```

消息体为 Python 列表，第一个元素通常为消息类型字符串。

---

## 3. 模块详细说明

### 3.1 `config.py` — 全局配置

所有配置集中在此文件中，包括：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SERVER_ADDR` / `SERVER_PORT` | 服务器地址和端口 | `192.168.215.128:51000` |
| `server_list` | 边缘设备列表（IP、SSH凭证、端口） | 4台设备 |
| `N` / `B` | 数据总量 / 批次大小 | 10000 / 256 |
| `K` | 设备数量 | `len(server_list)` |
| `G` | 分组数量 | 3 |
| `model_name` | 模型名称 | VGG5 |
| `split_layer` | 初始分割层 | `[6, 6, 6]` |
| `model_len` | 模型总层数 | 7 |
| `max_episodes` | RL最大训练回合数 | 100 |
| `K_epochs` | PPO每次更新的迭代次数 | 50 |
| `eps_clip` | PPO裁剪参数 | 0.2 |
| `window_size` | 状态衍生窗口大小 | 10 |
| `node_layer_indices` | 节点-层映射关系 | `{'client1': [0,1], ...}` |

### 3.2 `server.py` — 分布式推理服务端

**功能**：获取集群资源 → 计算分割点 → 加载数据 → 发送给第一个客户端

**流程**：
1. 通过 SSH 获取所有节点资源使用情况（`get_all_server_info`）
2. 使用资源感知策略计算分割点（`resource_aware_segmentation_points`）
3. 加载 CIFAR-10 测试数据
4. 通过 Socket 将数据和分割信息发送给链条中的第一个客户端

### 3.3 `client.py` — 分布式推理客户端

**功能**：接收上游数据 → 执行本地层推理 → 转发给下游客户端或输出结果

**流程**：
1. 等待上一节点的连接，接收消息
2. 加载预训练 VGG5 模型权重
3. 按照分配的层索引执行本地推理
4. 如果不是最后一个节点 → 转发给下一节点
5. 如果是最后一个节点 → 计算 loss 和 accuracy

### 3.4 `models/` — 模型定义

- **`model_struct.py`**：定义 VGG5 每一层的元数据（类型、通道数、特征图大小、FLOPs）
- **`vgg5/vgg5.py`**：实现可分割的 VGG5 类
  - `location='Server'`：构建分割层之前的部分
  - `location='Client'`：构建分割层之前的部分
  - `location='Unit'`：构建完整模型

### 3.5 `communication/` — 通信模块

- **`Communicator` 类**：基础通信类，提供 `bind` / `listen` / `send_message` / `receive_message`
- **`NodeEnd` 类**：继承自 `Communicator`，增加 `node_connect`（带重试的主动连接）
- **`demo_json/`**：JSON 格式聊天式通信示例（学习 Socket 编程参考）
- **`demo_send/`**：Pickle 格式链式推理的简化演示

### 3.6 `strategy/` — 分割策略

- **`NetworkSegmentationStrategy`** 类：
  - `random_select_segmentation_points()`：随机选择 N-1 个分割点
  - `resource_aware_segmentation_points(resource_usage)`：基于资源利用率选择分割点
  - `random_segmentation_point()`：随机选一个分割点（二分）
- **`resource_utilization.py`**：通过 Paramiko SSH 执行远程命令，采集 CPU/GPU/内存/网络信息

### 3.7 `RL/` — PPO 强化学习模块（核心）

这是项目最核心的部分，使用 PPO 算法自动学习最优的模型分割策略。

#### 文件依赖关系

```
RL_serverrun.py  ──▶  RLEnv.py (Env)  ──▶  correspondence.py (Socket通信)
     │                    │                   state_derivation.py (状态增强)
     │                    │                   iaf_state_derivation.py (IAF)
     ▼                    │
  PPO.py             config.py / utils.py / model_struct.py
     │
     ▼
RL_clientrun.py  ──▶  RLEnv.py (RL_Client)
```

#### `RLEnv.py` — 强化学习环境

包含两个类：

**`Env` 类**（服务端环境）：
- `reset()`：重置环境，所有层在客户端执行（不卸载），采集基线指标
- `step(action)`：执行动作（调整分割层），返回新状态、奖励
- `group()`：使用 KMeans 对客户端分组
- `infer()`：多线程执行推理/训练
- `calculate_reward()`：基于推理时间与基线的比较计算奖励

**`RL_Client` 类**（客户端）：
- `initialize()`：初始化模型、优化器
- `infer()`：根据分割层执行本地推理或卸载推理

#### `PPO.py` — PPO 算法

- **`Memory`**：经验缓冲区（状态、动作、奖励、对数概率）
- **`ActorCritic`**：Actor-Critic 网络
  - Actor 输出动作均值（经 Sigmoid 映射到 [0,1]）
  - Critic 输出状态价值
  - 输入维度为 `state_dim × 3`（状态衍生后）
- **`PPO`**：PPO 训练器
  - `select_action()`：采样动作
  - `update()`：PPO Clip 更新
  - `explore_decay()`：探索标准差衰减

#### `state_derivation.py` — 滑窗状态衍生

将原始状态 `s` 增强为 3 倍维度：

```
derived_state = [当前状态 s, 窗口内均值 mean(s), 变化趋势 mean(diff(s))]
```

#### `iaf_state_derivation.py` — IAF 状态衍生（实验性）

使用 LSTM + 可逆仿射变换生成衍生状态（可选替代方案）。

### 3.8 `RL_multiple/` 和 `RL_IAF/`

与 `RL/` 目录结构平行的变体实验：
- `RL_multiple/`：多客户端扩展版本
- `RL_IAF/`：集成 IAF 状态衍生的版本，额外包含 `graph.py` 绘图

### 3.9 `local_inference/` — 本地推理实验集合

包含多种推理和强化学习实验的变体：

| 子目录 | 说明 |
|--------|------|
| `RL/` | DQN 强化学习变体，含 DQN/优化DQN/GRU衍生 |
| `rl_data_from_server/` | Dueling DQN + 从服务端获取资源数据 |
| `single_data_from_server/` | 基础链式推理（数据在服务端准备） |
| `single_data_from_client/` | 基础链式推理（数据在客户端准备） |
| `single_data_from_server_recycle/` | 带回收/聚合的推理变体 |
| `single_data_from_server_RL/` | Gym环境 + PPO（`FederatedEnv`） |
| `multiple_task_from_server/` | 多任务 + `threading.Barrier` 同步 |
| `test/` | 最小化 Socket 通信测试 |

### 3.10 `Scheduling.py` — 子任务调度算法

实现边缘节点上的子任务排序与调度：

1. **分类排序**：将任务按执行时间与传输时间的关系分为两类
2. **A类优先**：优先调度 A 类任务（分类标记），串行排程
3. **最小等待时间贪心**：对非A类任务，按全局最小等待时间贪心插入

### 3.11 `scientific_research_drawing/` — 科研绘图

包含 matplotlib 绘图脚本，用于论文图表生成。

---

## 4. 数据流与架构图

### 4.1 分布式推理流程

```
                    ┌────────────────┐
                    │   server.py    │
                    │  (协调端)       │
                    │ 1. 采集资源     │
                    │ 2. 计算分割点   │
                    │ 3. 加载数据     │
                    └───────┬────────┘
                            │ Socket (数据+分割信息)
                            ▼
                    ┌────────────────┐
                    │  client.py #1  │
                    │  执行第0-1层   │
                    └───────┬────────┘
                            │ Socket (中间激活)
                            ▼
                    ┌────────────────┐
                    │  client.py #2  │
                    │  执行第2-3层   │
                    └───────┬────────┘
                            │ Socket (中间激活)
                            ▼
                    ┌────────────────┐
                    │  client.py #3  │
                    │  执行第4-6层   │
                    │  计算loss/acc  │
                    └────────────────┘
```

### 4.2 RL 训练流程

```
  ┌─────────────────────────────────────────────┐
  │           RL_serverrun.py                    │
  │  ┌─────────┐      ┌──────────┐              │
  │  │  PPO    │◀────▶│  Env     │              │
  │  │ 智能体  │ 状态/ │  RL环境  │              │
  │  │         │ 动作  │          │              │
  │  └─────────┘      └────┬─────┘              │
  └────────────────────────┼────────────────────┘
                           │ Socket (分割层/梯度/权重)
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │RL_Client │ │RL_Client │ │RL_Client │
        │  设备1   │ │  设备2   │ │  设备3   │
        │ 本地训练 │ │ 本地训练 │ │ 本地训练 │
        └──────────┘ └──────────┘ └──────────┘
```

### 4.3 状态衍生流程

```
原始状态 s(t)
    │
    ▼
┌───────────────────┐
│  StateDerivation  │
│                   │
│ buffer: [s(t-w), ..., s(t)]
│                   │
│ mean = avg(buffer)│
│ diff = mean(Δs)  │
└───────┬───────────┘
        │
        ▼
衍生状态: [s(t), mean, diff]  (维度×3)
        │
        ▼
    PPO Actor-Critic 网络
```

---

## 5. 环境配置与依赖安装

### 5.1 Python 环境

建议使用 Python 3.8+，推荐使用 conda 或 venv 创建虚拟环境：

```bash
conda create -n synergist python=3.8
conda activate synergist
```

### 5.2 安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表**：

| 包 | 版本 | 用途 |
|---|---|---|
| torch | 1.10.0+cpu | 深度学习框架 |
| torchvision | ~0.16.0 | 数据集和模型工具 |
| paramiko | 3.4.0 | SSH远程命令执行 |
| matplotlib | ~3.7.3 | 绘图 |
| tqdm | ~4.66.1 | 进度条 |
| numpy | ~1.24.4 | 数值计算 |
| scikit-learn | ~1.3.0 | KMeans聚类 |

> **注意**：`torch==1.10.0+cpu` 与 `torchvision~=0.16.0` 版本可能不兼容。
> 建议根据你的 CUDA 版本从 [PyTorch 官网](https://pytorch.org/) 选择合适的组合。
> 例如：`torch==2.0.0` + `torchvision==0.15.0`

### 5.3 数据集

项目使用 **CIFAR-10** 数据集：
- `server.py` 中设置 `download=True`，首次运行会自动下载
- `utils.py` 中设置 `download=False`，需要数据集已存在于 `dataset_path`

### 5.4 路径配置（重要）

`config.py` 中的数据集路径依赖于项目根目录名称：

```python
home = sys.path[0].split('SynerGist')[0] + 'SynerGist'
dataset_path = home + '/dataset/vgg5/'
```

如果你的项目文件夹名不是 `SynerGist`（当前为 `Partition_Scheduling`），需要修改此路径。

---

## 6. 如何运行

### 6.1 分布式推理（基础版）

需要多台机器或多个终端模拟：

```bash
# 步骤1: 修改 config.py 中的 IP 地址为你的实际环境

# 步骤2: 在各客户端机器上启动客户端（先于服务端启动）
python client.py

# 步骤3: 在服务端机器上启动服务端
python server.py
```

### 6.2 RL 训练（PPO 自动分割）

```bash
# 步骤1: 修改 config.py 中的配置

# 步骤2: 在服务端启动 RL 训练
cd RL/
python RL_serverrun.py

# 步骤3: 在每个客户端设备上启动
cd RL/
python RL_clientrun.py
```

### 6.3 本地单机测试

使用 `local_inference/` 下的脚本进行本地实验，无需多机部署：

```bash
# 示例：单路径推理
cd local_inference/single_data_from_server/

# 终端1: 启动服务端
python server.py

# 终端2-4: 启动客户端（按顺序）
python client_1.py
python client_2.py
python client_3.py
```

### 6.4 Socket 通信测试

```bash
cd local_inference/test/

# 终端1
python server.py

# 终端2
python client1.py
```

---

## 7. 关键算法解析

### 7.1 PPO（Proximal Policy Optimization）

PPO 是一种策略梯度方法，通过限制策略更新幅度来保证训练稳定性：

```
L_CLIP(θ) = E[min(r(θ)·A, clip(r(θ), 1-ε, 1+ε)·A)]
```

其中：
- `r(θ) = π_θ(a|s) / π_θ_old(a|s)` 为新旧策略比率
- `A` 为优势函数
- `ε` 为裁剪参数（默认 0.2）

项目中的具体实现：
- Actor 网络输出连续动作（多元正态分布采样）
- 动作经 Sigmoid 映射到 [0,1]，再转换为分割层索引
- 奖励 = Σ(基线时间 - 推理时间) / 基线时间

### 7.2 状态衍生

将 `2G` 维原始状态（推理时间 + 卸载比例）增强为 `6G` 维：

```python
derived_state = concat(
    current_state,           # 当前状态
    mean(state_buffer),      # 滑窗内历史均值
    mean(diff(state_buffer)) # 状态变化趋势
)
```

### 7.3 子任务调度算法

`Scheduling.py` 实现三阶段调度：

1. **阶段一**：每个边缘节点内部，按执行时间/传输时间将任务分为两类排序
2. **阶段二**：A 类任务前置，串行排程，记录结束时间
3. **阶段三**：非A类任务按最小等待时间贪心调度

### 7.4 资源感知分割

```python
# 按 CPU/内存/网络利用率对节点排序
sorted_nodes = sorted(resource_usage, key=cpu+memory+network)

# 遍历模型各层，当某层的 FLOPs 超过当前节点 CPU 负载时，切换到下一个节点
for layer in layers:
    if layer.flops > current_node.cpu:
        add_segmentation_point()
        move_to_next_node()
```

---

## 8. 配置说明

### 8.1 网络配置

修改 `config.py` 中的服务器列表以匹配你的环境：

```python
server_list = [
    {
        "ip": "你的设备IP",
        "username": "SSH用户名",
        "password": "SSH密码",
        "hostname": "设备名",
        "application": {
            "VGG5": 9001  # 应用端口
        }
    },
    # ...更多设备
]
```

### 8.2 RL 超参数调优

| 参数 | 建议范围 | 说明 |
|------|----------|------|
| `rl_lr` | 1e-4 ~ 1e-3 | 学习率，过大导致不稳定 |
| `K_epochs` | 10 ~ 80 | PPO更新迭代次数 |
| `eps_clip` | 0.1 ~ 0.3 | 裁剪范围 |
| `rl_gamma` | 0.9 ~ 0.99 | 折扣因子 |
| `action_std` | 0.3 ~ 0.7 | 探索标准差初始值 |
| `exploration_times` | 10 ~ 30 | 不衰减探索的轮数 |
| `window_size` | 5 ~ 20 | 状态衍生窗口大小 |
| `G` | 2 ~ 5 | 客户端分组数 |

---

## 9. 常见问题与注意事项

### Q1: `config.py` 中的路径报错

`dataset_path` 依赖于 `SynerGist` 目录名。如果项目目录名为 `Partition_Scheduling`，需要修改：

```python
# 修改前
home = sys.path[0].split('SynerGist')[0] + 'SynerGist'

# 修改后（直接指定路径）
home = 'E:/1_MyCode/model_partitioning/Partition_Scheduling'
dataset_path = home + '/dataset/vgg5/'
```

### Q2: 无法连接 SSH 获取资源

`resource_utilization.py` 使用 Paramiko SSH 连接远程服务器，需要：
- 目标机器开启 SSH 服务
- 安装 `ifstat`（网络监控命令）
- 确保 `nvidia-smi` 可用（如需 GPU 监控）

本地调试时可跳过资源采集，直接手动指定分割点。

### Q3: 客户端启动顺序

分布式推理场景中，**客户端必须先于服务端启动**（客户端需要先监听端口等待连接）。

### Q4: `sys.path.append('../')` 导致模块导入失败

`RL/` 等子目录下的脚本使用 `sys.path.append('../')` 来导入根目录的模块。运行时必须 `cd` 到对应目录下执行：

```bash
cd RL/
python RL_serverrun.py  # 正确

# 不要这样运行：
python RL/RL_serverrun.py  # 可能导致导入失败
```

### Q5: VGG5 预训练权重

`client.py` 中需要加载 `models/vgg5/vgg5.pth` 权重文件。项目仓库中未包含此文件，需要自行训练或获取。

### Q6: 单机调试建议

如果没有多台设备，可以：
1. 使用 `local_server_list`（`config.py`），所有 IP 为 `127.0.0.1`
2. 使用不同端口区分客户端
3. 在不同终端窗口中分别启动各节点

---

## 附：技术栈总结

| 技术 | 用途 |
|------|------|
| PyTorch | 深度学习模型构建和训练 |
| Socket + Pickle | 节点间通信 |
| Paramiko | SSH远程资源采集 |
| PPO (Actor-Critic) | 强化学习优化分割策略 |
| KMeans | 客户端聚类分组 |
| DQN / Dueling DQN | 备选RL算法（local_inference中） |
| CIFAR-10 | 实验数据集 |
| Matplotlib | 科研绘图 |

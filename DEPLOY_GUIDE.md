# 两台机器实验部署指南

## 硬件环境

| 角色 | 机器 | CPU | GPU | OS | 运行程序 |
|------|------|-----|-----|----|----------|
| **主机A**（RL服务端 + 客户端1） | 台式机 | i7-14700KF | RTX 5060 Ti 16GB | Windows | `RL_serverrun.py` + `RL_clientrun.py` |
| **主机B**（客户端2） | 台式机 | i5-12600KF | 无 | Ubuntu 24.04 | `RL_clientrun.py` |

## 架构图

```
┌──────────────────────────────────────┐
│         主机A (Windows, GPU)          │
│                                      │
│  终端1: RL_serverrun.py              │
│    ├─ PPO 智能体训练 (可用GPU)        │
│    ├─ 环境管理 (Env)                  │
│    └─ 等待2个客户端连接               │
│                                      │
│  终端2: RL_clientrun.py              │
│    └─ 客户端1 (GPU加速推理)           │
└───────────────┬──────────────────────┘
                │ TCP Socket (端口51000)
                │ 局域网连接
┌───────────────┴──────────────────────┐
│         主机B (Ubuntu, CPU)           │
│                                      │
│  终端1: RL_clientrun.py              │
│    └─ 客户端2 (CPU推理)              │
└──────────────────────────────────────┘
```

## 第一步：获取两台机器的网络信息

### 主机A (Windows)

打开 PowerShell，分别执行：

```powershell
# 获取主机名
python -c "import socket; print(socket.gethostname())"
# 输出示例: DESKTOP-ABC1234

# 获取局域网 IP
ipconfig
# 找到 "以太网适配器" 下的 IPv4 地址，如: 192.168.1.100
```

### 主机B (Ubuntu)

打开终端，分别执行：

```bash
# 获取主机名
python3 -c "import socket; print(socket.gethostname())"
# 输出示例: ubuntu-desktop

# 获取局域网 IP
ip addr show | grep "inet " | grep -v 127.0.0.1
# 输出示例: inet 192.168.1.101/24

# 测试连通性
ping <主机A的IP>
```

### 确认互通

两台机器必须在**同一局域网**内，且能互相 ping 通。

---

## 第二步：修改配置文件

打开 `config.py`，修改文件顶部 **3 处带 ★ 标记的配置**：

```python
# ★ 1. 填写实际 IP
MACHINE_A_IP = '192.168.1.100'       # 替换为主机A实际IP
MACHINE_B_IP = '192.168.1.101'       # 替换为主机B实际IP

# ★ 2. 填写实际主机名
MACHINE_A_HOSTNAME = 'DESKTOP-ABC1234'  # 替换为主机A的 socket.gethostname() 输出
MACHINE_B_HOSTNAME = 'ubuntu-desktop'   # 替换为主机B的 socket.gethostname() 输出

# ★ 3. 填写 Ubuntu SSH 凭证
MACHINE_B_SSH_USER = 'victor'         # Ubuntu 用户名
MACHINE_B_SSH_PASS = '你的密码'        # Ubuntu 密码
```

---

## 第三步：配置环境

### 主机A (Windows) — 安装 PyTorch GPU 版

```powershell
# 方式1: 运行配置脚本
.\setup_windows.ps1

# 方式2: 手动安装
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install paramiko==3.4.0 matplotlib tqdm numpy scikit-learn
```

### 主机B (Ubuntu) — 安装 PyTorch CPU 版

首先将整个项目复制到主机B：

```bash
# 方式1: 用 git clone
git clone <你的仓库地址> ~/Partition_Scheduling
cd ~/Partition_Scheduling

# 方式2: 用 scp 从主机A复制
scp -r victor@<主机A_IP>:/path/to/Partition_Scheduling ~/Partition_Scheduling
cd ~/Partition_Scheduling

# 运行配置脚本
bash setup_ubuntu.sh
```

### 两台机器都需要：下载 CIFAR-10 数据集

```bash
# 确保在项目根目录下
python -c "
import torchvision, os
d = os.path.join(os.path.dirname(os.path.abspath('config.py')), 'dataset', 'vgg5')
os.makedirs(d, exist_ok=True)
torchvision.datasets.CIFAR10(root=d, train=True, download=True)
print('OK: ' + d)
"
```

---

## 第四步：开放防火墙端口

### 主机A (Windows)

RL Server 监听 51000 端口，Windows 防火墙默认会阻止入站连接：

```powershell
# 以管理员身份运行 PowerShell
New-NetFirewallRule -DisplayName "SynerGist RL Server" -Direction Inbound -LocalPort 51000 -Protocol TCP -Action Allow
```

或者在 "Windows Defender 防火墙" → "高级设置" → "入站规则" → 新建规则 → TCP 端口 51000。

### 主机B (Ubuntu)

通常 Ubuntu 默认不限制出站连接，无需额外配置。如果有 ufw：

```bash
sudo ufw allow out 51000/tcp
```

---

## 第五步：运行 RL 训练实验

### 启动顺序（严格按此顺序执行）

**① 主机A 终端1：启动 RL 服务端**

```powershell
cd E:\1_MyCode\model_partitioning\Partition_Scheduling
.\.venv\Scripts\Activate.ps1
cd RL
python RL_serverrun.py
```

服务端启动后会显示 `Waiting for incoming connection...`，等待 2 个客户端连接。

**② 主机A 终端2（新开一个终端）：启动客户端1**

```powershell
cd E:\1_MyCode\model_partitioning\Partition_Scheduling
.\.venv\Scripts\Activate.ps1
cd RL
python RL_clientrun.py
```

**③ 主机B 终端1：启动客户端2**

```bash
cd ~/Partition_Scheduling
source .venv/bin/activate
cd RL
python3 RL_clientrun.py
```

### 预期输出

当两个客户端都连接后，服务端会开始 PPO 训练循环：

```
INFO - Baseline: {"192.168.1.100": 0.5, "192.168.1.101": 0.8}
INFO - Current OPs: [6, 4]
INFO - Training time per iteration: {...}
INFO - Current reward: 0.15
INFO - Current maxtime: 0.6
```

训练结果保存在 `RL/RL_res.pkl`，模型权重保存在 `RL/PPO.pth`。

---

## 故障排查

### 问题1: 客户端连接超时

```
连接到192.168.1.100:51000失败，正在重试...
```

**检查项**：
- 主机A 防火墙是否开放了 51000 端口
- 两台机器能否互相 ping 通
- `config.py` 中的 IP 地址是否正确

### 问题2: hostname 找不到

```
TypeError: 'NoneType' object is not subscriptable
```

说明 `socket.gethostname()` 返回的主机名在 `server_list` 中找不到匹配。

**检查方法**：

```python
import socket
print(socket.gethostname())  # 确认输出与 config.py 中的 MACHINE_x_HOSTNAME 一致
```

### 问题3: CIFAR-10 数据集找不到

```
RuntimeError: Dataset not found
```

确认 `dataset/vgg5/` 目录下有 `cifar-10-batches-py/` 文件夹。如果没有，重新下载：

```python
import torchvision
torchvision.datasets.CIFAR10(root='./dataset/vgg5', train=True, download=True)
```

### 问题4: CUDA 不可用

主机A 如果 `torch.cuda.is_available()` 返回 False：
- 确认安装了 CUDA 版 PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu124`
- 确认 NVIDIA 驱动已安装: `nvidia-smi`

主机B 没有 GPU，代码会自动使用 CPU，这是正常的。

---

## 实验参数说明

当前配置为 **K=2（2台设备）, G=2（2个分组）** 的最小可行实验：

| 参数 | 值 | 说明 |
|------|-----|------|
| K | 2 | 设备数量 |
| G | 2 | KMeans 分组数 |
| state_dim | 4 (2×G) | 推理时间+卸载比例 |
| action_dim | 2 (G) | 每组的分割点决策 |
| 衍生后 state_dim | 12 (4×3) | 当前+均值+趋势 |
| max_episodes | 100 | 训练回合数 |
| VGG5 层数 | 7 | 可选分割点: 层1~5 |

如果后续增加设备，只需在 `server_list` 中添加条目，`K` 和 `split_layer` 会自动调整。

---

## 扩展到更多设备（可选）

当前代码用客户端 IP 地址作为标识符，同一台机器上不能运行多个客户端。如果将来想在同一台机器上模拟多个客户端，需要修改 `RLEnv.py` 中 `Env.__init__` 的客户端识别逻辑（用 `ip:port` 替代 `ip`）。

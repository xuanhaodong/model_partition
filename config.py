import sys
import os
"""
 配置相关
 ============================================================
 【部署前必读】请按你的实际环境修改以下带 ★ 标记的配置
 ============================================================

 六节点部署拓扑：
   主机A (Windows 32GB, i7-14700KF + 5060Ti)
     ├─ 宿主机: RL Server + client1  (GPU)     ← 16GB 预留
     ├─ VMware VM1: client2                     ← 4GB
     └─ VMware VM2: client3                     ← 4GB
   主机B (Ubuntu 16GB, i5-12600KF)
     ├─ 宿主机: client4  (CPU)                  ← ~8GB
     ├─ Docker 容器: client5                     ← ~4GB (共享宿主内存)
     └─ Docker 容器: client6                     ← ~4GB (共享宿主内存)
"""

# =============================================================
#  ★ 需要手动填写的配置（共 6 个节点的 IP 和 hostname）
# =============================================================
# 获取 hostname 方法: python -c "import socket; print(socket.gethostname())"
# 获取 IP 方法:       Windows → ipconfig | Ubuntu → ip addr
#                     VM → ip addr | Docker → docker inspect <容器名>

# ★ 主机A 宿主机（Windows，运行 RL Server + client1）
MACHINE_A_IP       = '192.168.80.100'    # ★ 替换为主机A实际局域网 IP
MACHINE_A_HOSTNAME = 'DESKTOP-XXXXX'     # ★ 替换为 python socket.gethostname() 输出

# ★ VMware VM（在主机A上，桥接模式获得独立 IP）
VM1_IP       = '192.168.80.131'          # ★ VM1 静态 IP
VM1_HOSTNAME = 'vm-client2'              # ★ VM1 中 sudo hostnamectl set-hostname 设定的值
VM2_IP       = '192.168.80.132'          # ★ VM2 静态 IP
VM2_HOSTNAME = 'vm-client3'              # ★ VM2 中 sudo hostnamectl set-hostname 设定的值

# ★ 主机B 宿主机（Ubuntu）
MACHINE_B_IP       = '192.168.80.140'    # ★ 替换为主机B实际局域网 IP
MACHINE_B_HOSTNAME = 'ubuntu-host'       # ★ 替换为主机B的 hostname

# ★ Docker 容器（在主机B上，macvlan 模式获得独立 IP）
DOCKER1_IP       = '192.168.80.141'      # ★ 容器1 分配的 IP
DOCKER1_HOSTNAME = 'docker-client5'      # ★ docker run --hostname 指定的值
DOCKER2_IP       = '192.168.80.142'      # ★ 容器2 分配的 IP
DOCKER2_HOSTNAME = 'docker-client6'      # ★ docker run --hostname 指定的值

# ★ SSH 凭证（VM 和 Docker 容器如不需要资源采集可用默认值）
DEFAULT_SSH_USER = 'victor'              # ★ 通用 SSH 用户名
DEFAULT_SSH_PASS = '123456'              # ★ 通用 SSH 密码

# =============================================================
#  以下配置基于上面的变量自动生成，一般不需要修改
# =============================================================

# RL Server 运行在主机A宿主机上
SERVER_ADDR = MACHINE_A_IP
SERVER_PORT = 51000

# 六节点部署配置
server_list = [
    {
        "ip": MACHINE_A_IP,
        "username": "administrator",
        "password": DEFAULT_SSH_PASS,
        "hostname": MACHINE_A_HOSTNAME,
        "application": {"VGG5": 9001},
    },
    {
        "ip": VM1_IP,
        "username": DEFAULT_SSH_USER,
        "password": DEFAULT_SSH_PASS,
        "hostname": VM1_HOSTNAME,
        "application": {"VGG5": 9001},
    },
    {
        "ip": VM2_IP,
        "username": DEFAULT_SSH_USER,
        "password": DEFAULT_SSH_PASS,
        "hostname": VM2_HOSTNAME,
        "application": {"VGG5": 9001},
    },
    {
        "ip": MACHINE_B_IP,
        "username": DEFAULT_SSH_USER,
        "password": DEFAULT_SSH_PASS,
        "hostname": MACHINE_B_HOSTNAME,
        "application": {"VGG5": 9001},
    },
    {
        "ip": DOCKER1_IP,
        "username": DEFAULT_SSH_USER,
        "password": DEFAULT_SSH_PASS,
        "hostname": DOCKER1_HOSTNAME,
        "application": {"VGG5": 9001},
    },
    {
        "ip": DOCKER2_IP,
        "username": DEFAULT_SSH_USER,
        "password": DEFAULT_SSH_PASS,
        "hostname": DOCKER2_HOSTNAME,
        "application": {"VGG5": 9001},
    },
]

CLIENTS_LIST = [server["ip"] for server in server_list]
dataset_config = {
    'VGG5': "vgg5",
    'VGG6': ""
}
# Dataset configuration
home = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(home, 'dataset', 'vgg5')
# data length
N = 10000
# Batch size
B = 256
iterations = int(N / B)
# Number of devices
K = len(server_list)
# Number of groups (KMeans clusters, must be <= K)
G = 3
model_name = 'VGG5'
model_size = 1.28
model_flops = 32.902
total_flops = 8488192
# Initial split layers (length == K, 6 = model_len-1 = no offloading)
split_layer = [6] * K
model_len = 7


# RL training configration
LR = 0.01                  # Learning rate
max_episodes = 100         # max training episodes
max_time_steps = 100       # max time steps in one episode
exploration_times = 20	   # exploration times without std decay
n_latent_var = 64          # number of variables in hidden layer
action_std = 0.5           # constant std for action distribution (Multivariate Normal)
update_timestep = 10       # update policy every n time steps
K_epochs = 50              # update policy for K epochs
eps_clip = 0.2             # clip parameter for PPO
rl_gamma = 0.9             # discount factor
rl_b = 100				   # Batch size
rl_lr = 0.0003             # parameters for Adam optimizer
rl_betas = (0.9, 0.999)

node_layer_indices = {
    MACHINE_A_HOSTNAME: [0, 1],
    VM1_HOSTNAME:       [2, 3],
    VM2_HOSTNAME:       [4, 5, 6],
}

# infer times for each device
iteration = {server['ip']: 5 for server in server_list}

# 状态衍生的时间窗口大小
window_size = 10
buffer_size = 10

# IAF model configuration
hidden_dim = 64
iaf_lr = 0.001

random = True
random_seed = 0

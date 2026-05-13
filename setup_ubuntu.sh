#!/bin/bash
# ============================================================
# Ubuntu 24.04 主机 (主机B) 环境配置脚本
# 在 Ubuntu 终端中以普通用户执行: bash setup_ubuntu.sh
# ============================================================

set -e

echo "===== 1/5 安装系统依赖 ====="
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git openssh-server ifstat

echo "===== 2/5 确保 SSH 服务启动（用于资源采集） ====="
sudo systemctl enable ssh
sudo systemctl start ssh

echo "===== 3/5 创建 Python 虚拟环境 ====="
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate

echo "===== 4/5 安装 Python 依赖 ====="
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install paramiko==3.4.0 matplotlib tqdm numpy scikit-learn

echo "===== 5/5 下载 CIFAR-10 数据集 ====="
python3 -c "
import torchvision
import torchvision.transforms as transforms
import os

dataset_dir = os.path.join(os.path.dirname(os.path.abspath('$0')), 'dataset', 'vgg5')
os.makedirs(dataset_dir, exist_ok=True)
print(f'下载 CIFAR-10 到 {dataset_dir}')
torchvision.datasets.CIFAR10(root=dataset_dir, train=True, download=True)
torchvision.datasets.CIFAR10(root=dataset_dir, train=False, download=True)
print('CIFAR-10 数据集下载完成！')
"

echo ""
echo "===== 环境配置完成！ ====="
echo ""
echo "后续步骤："
echo "  1. 确认主机名: python3 -c \"import socket; print(socket.gethostname())\""
echo "  2. 确认 IP 地址: ip addr show | grep 'inet '"
echo "  3. 将以上信息填入 config.py 的 MACHINE_B_HOSTNAME 和 MACHINE_B_IP"
echo "  4. 激活环境后运行: source .venv/bin/activate && cd RL && python3 RL_clientrun.py"

# ============================================================
# Windows 主机 (主机A) 环境配置脚本
# 在 PowerShell 中以管理员身份执行
# ============================================================

Write-Host "===== 1/4 检查 Python =====" -ForegroundColor Cyan
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "请先安装 Python 3.8+ 并添加到 PATH" -ForegroundColor Red
    exit 1
}

Write-Host "===== 2/4 创建虚拟环境 =====" -ForegroundColor Cyan
Set-Location $PSScriptRoot
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Write-Host "===== 3/4 安装 Python 依赖 =====" -ForegroundColor Cyan
pip install --upgrade pip
# 安装带 CUDA 支持的 PyTorch (适配 5060 Ti)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install paramiko==3.4.0 matplotlib tqdm numpy scikit-learn

Write-Host "===== 4/4 下载 CIFAR-10 数据集 =====" -ForegroundColor Cyan
python -c @"
import torchvision, os
dataset_dir = os.path.join(r'$PSScriptRoot', 'dataset', 'vgg5')
os.makedirs(dataset_dir, exist_ok=True)
print(f'Downloading CIFAR-10 to {dataset_dir}')
torchvision.datasets.CIFAR10(root=dataset_dir, train=True, download=True)
torchvision.datasets.CIFAR10(root=dataset_dir, train=False, download=True)
print('Done!')
"@

Write-Host ""
Write-Host "===== 环境配置完成！ =====" -ForegroundColor Green
Write-Host ""
Write-Host "后续步骤：" -ForegroundColor Yellow
Write-Host "  1. 确认主机名: python -c `"import socket; print(socket.gethostname())`""
Write-Host "  2. 确认 IP 地址: ipconfig"
Write-Host "  3. 将以上信息填入 config.py 的 MACHINE_A_HOSTNAME 和 MACHINE_A_IP"
Write-Host "  4. 关闭防火墙或开放端口 51000: "
Write-Host "     New-NetFirewallRule -DisplayName 'SynerGist RL' -Direction Inbound -LocalPort 51000 -Protocol TCP -Action Allow"

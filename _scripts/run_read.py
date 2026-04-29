# -*- coding: utf-8 -*-
"""绕开命令行编码问题，直接在脚本中写死路径"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from read_docs import read_docx, read_pdf_excerpt

DOCX = [
    r"D:\系统默认\桌面\组会\星地协同模型分割.docx",
]

PDFS_LLM = [
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Zhang 等 - 2025 - Communication-Efficient Distributed On-Device LLM Inference Over Wireless Networks - .pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Zhang 等 - 2025 - Beyond the Cloud Edge Inference for Generative Large Language Models in Wireless Networks - .pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Zhu 等 - 2025 - Birds in Cages Edge Inference Allocation for Distributed LLM Deployment - .pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Xu 等 - 2025 - Joint Inference Offloading and Model Caching for Small and Large Language Model Collaboration - .pdf",
]

PDFS_PART = [
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Peng 等 - 2026 - APT-SAT An Adaptive DNN Partitioning and Task Offloading Framework Within Collaborative Satellite C - IEEE Trans. Netw. Sci. Eng..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Li 等 - 2024 - Distributed DNN Inference With Fine-Grained Model Partitioning in Mobile Edge Computing Networks - IEEE Trans. on Mobile Comput..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Yan 等 - 2025 - Multi-Endpoint DAG-Driven Joint Partitioning-Offloading and Scheduling Optimization for DNN Inferenc - IEEE Internet Things J..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Chen 等 - 2025 - SLICE Energy-Efficient Satellite-Ground Co-Inference via Layer-Wise Scheduling Optimization - .pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Qiao 等 - 2025 - On-Orbit DNN Distributed Inference for Remote Sensing Images in Satellite Internet of Things - IEEE Internet Things J..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Taufique 等 - 2025 - HiDPHierarchical DNN Partitioning for Distributed Inference on Heterogeneous Edge Platforms - .pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Liu 等 - 2024 - MoEI Mobility-Aware Edge Inference Based on Model Partition and Service Migration - IEEE Trans. on Mobile Comput..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Eshratifar 等 - 2021 - JointDNN An Efficient Training and Inference Engine for Intelligent Mobile Cloud Computing Services - IEEE Trans. on Mobile Comput..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Liao 等 - 2023 - PMP A partition-match parallel mechanism for DNN inference acceleration in cloud–edge collaborative - Journal of Network and Computer Applications.pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Zhang 等 - 2021 - DeepSlicing Collaborative and Adaptive CNN Inference With Low Latency - .pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Zhang 等 - 2025 - SatCooper Enhancing Cooperative Inference Analytics for Satellite Service via Multi-Exit DNNs - IEEE Trans. on Mobile Comput..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Li 等 - 2020 - Edge AI On-Demand Accelerating Deep Neural Network Inference via Edge Computing - IEEE Trans. Wireless Commun..pdf",
    r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Teerapittayanon 等 - 2017 - BranchyNet Fast Inference via Early Exiting from Deep Neural Networks - .pdf",
]

if __name__ == "__main__":
    for f in DOCX:
        read_docx(f)
    for f in PDFS_LLM + PDFS_PART:
        if os.path.exists(f):
            read_pdf_excerpt(f, max_pages=2)
        else:
            print(f"NOT FOUND: {f}")

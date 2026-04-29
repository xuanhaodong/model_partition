# -*- coding: utf-8 -*-
"""精确提取每篇论文的 Testbed / Experimental Setup 段落"""
import os
import sys
import re
import fitz

sys.stdout.reconfigure(encoding='utf-8')

KEYWORDS = [
    r"jetson", r"raspberry", r"orin", r"xavier", r"tegra",
    r"nvidia", r"videocore", r"broadcom",
    r"\bresnet[- ]?152", r"\bvgg[- ]?19", r"\bvgg[- ]?16", r"\bvgg5\b",
    r"efficientnet", r"inception", r"mobilenet",
    r"experimental setup", r"testbed", r"evaluation",
    r"\d+\s*mbps", r"\d+\s*gbps", r"wi[- ]?fi", r"wireless",
    r"raspbian", r"ubuntu", r"jetpack", r"pytorch", r"tensorflow",
    r"core[- ]?i[3579]", r"intel", r"amd", r"\bGPU\b",
    r"watts", r"power", r"energy",
]
PATTERN = re.compile("|".join(KEYWORDS), re.IGNORECASE)

PDFS = {
    "HiDP-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Taufique 等 - 2025 - HiDPHierarchical DNN Partitioning for Distributed Inference on Heterogeneous Edge Platforms - .pdf",
    "Tango-2024": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Taufique 等 - 2024 - Tango Low Latency Multi-DNN Inference on Heterogeneous Edge Platforms - .pdf",
    "DeepSlicing-2021": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Zhang 等 - 2021 - DeepSlicing Collaborative and Adaptive CNN Inference With Low Latency - .pdf",
    "MoEI-2024": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Liu 等 - 2024 - MoEI Mobility-Aware Edge Inference Based on Model Partition and Service Migration - IEEE Trans. on Mobile Comput..pdf",
    "EdgeAI-2020": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Li 等 - 2020 - Edge AI On-Demand Accelerating Deep Neural Network Inference via Edge Computing - IEEE Trans. Wireless Commun..pdf",
    "FineGrained-2024": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Li 等 - 2024 - Distributed DNN Inference With Fine-Grained Model Partitioning in Mobile Edge Computing Networks - IEEE Trans. on Mobile Comput..pdf",
    "POPS-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Yan 等 - 2025 - Multi-Endpoint DAG-Driven Joint Partitioning-Offloading and Scheduling Optimization for DNN Inferenc - IEEE Internet Things J..pdf",
    "PMP-2023": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Liao 等 - 2023 - PMP A partition-match parallel mechanism for DNN inference acceleration in cloud–edge collaborative - Journal of Network and Computer Applications.pdf",
    "JointDNN-2021": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Eshratifar 等 - 2021 - JointDNN An Efficient Training and Inference Engine for Intelligent Mobile Cloud Computing Services - IEEE Trans. on Mobile Comput..pdf",
    "BranchyNet-2017": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Teerapittayanon 等 - 2017 - BranchyNet Fast Inference via Early Exiting from Deep Neural Networks - .pdf",
    "APT-SAT-2026": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Peng 等 - 2026 - APT-SAT An Adaptive DNN Partitioning and Task Offloading Framework Within Collaborative Satellite C - IEEE Trans. Netw. Sci. Eng..pdf",
    "SLICE-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Chen 等 - 2025 - SLICE Energy-Efficient Satellite-Ground Co-Inference via Layer-Wise Scheduling Optimization - .pdf",
    "Qiao-OnOrbit-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Qiao 等 - 2025 - On-Orbit DNN Distributed Inference for Remote Sensing Images in Satellite Internet of Things - IEEE Internet Things J..pdf",
    "SatCooper-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Zhang 等 - 2025 - SatCooper Enhancing Cooperative Inference Analytics for Satellite Service via Multi-Exit DNNs - IEEE Trans. on Mobile Comput..pdf",
    "NaviSplit-2024": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Johnsen 等 - 2024 - NaviSplit Dynamic Multi-Branch Split DNNs for Efficient Distributed Autonomous Navigation - .pdf",
    "Ruzicka-Sat-2023": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\R??i?ka 等 - 2023 - Fast Model Inference and Training On-Board of Satellites - .pdf",
    "Plumridge-Sat-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Plumridge 等 - 2025 - Rapid Distributed Fine-tuning of a Segmentation Model Onboard Satellites - .pdf",
    "Guan-Sat-2024": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\模型分割\Guan 等 - 2024 - Collaborative Inference in DNN-Based Satellite Systems with Dynamic Task Streams - .pdf",
    "CommEffLLM-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Zhang 等 - 2025 - Communication-Efficient Distributed On-Device LLM Inference Over Wireless Networks - .pdf",
    "BeyondCloud-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Zhang 等 - 2025 - Beyond the Cloud Edge Inference for Generative Large Language Models in Wireless Networks - .pdf",
    "Birds-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Zhu 等 - 2025 - Birds in Cages Edge Inference Allocation for Distributed LLM Deployment - .pdf",
    "LSCI-2025": r"C:\Users\victor\Nutstore\1\zotero\卫星网络\LLM分布式推理\Xu 等 - 2025 - Joint Inference Offloading and Model Caching for Small and Large Language Model Collaboration - .pdf",
}


def extract_relevant_lines(path, max_pages=None):
    print(f"\n========== {os.path.basename(path)} ==========")
    try:
        doc = fitz.open(path)
        if max_pages is None:
            max_pages = len(doc)
        for i in range(min(max_pages, len(doc))):
            page_text = doc[i].get_text("text")
            # 按行筛选
            lines = page_text.split('\n')
            keep = []
            for j, line in enumerate(lines):
                if PATTERN.search(line):
                    # 加上前后各 1 行上下文
                    start = max(0, j - 1)
                    end = min(len(lines), j + 2)
                    keep.append(f"  L{j:03d}: " + " | ".join(
                        l.strip() for l in lines[start:end] if l.strip()))
            if keep:
                print(f"-- page {i+1} --")
                for k in keep[:25]:
                    print(k)
        doc.close()
    except Exception as e:
        print(f"ERR: {e}")


if __name__ == "__main__":
    keys = sys.argv[1:] or list(PDFS.keys())
    for k in keys:
        if k in PDFS:
            p = PDFS[k]
            if os.path.exists(p):
                extract_relevant_lines(p)
            else:
                print(f"NOT FOUND: {p}")


# 🆓 Verified Free Models (OpenRouter)
**Last Updated**: Dec 2025
**Source**: User Verification

This document lists currently available high-performance free models verified for the auto-blogger pipeline.

## 🚀 Tier 1: Reasoning & Logic (Orchestrator/Critic)
| Model Name | ID | Context | Strengths |
| :--- | :--- | :--- | :--- |
| **DeepSeek R1T2 Chimera** | `tngtech/deepseek-r1t2-chimera:free` | 164K | **Strongest Logician**. Tri-parent design (R1-0528 + R1 + V3). 2x faster than R1. Best for outlines/critiques. |
| **DeepSeek R1 0528** | `deepseek/deepseek-r1-0528:free` | 164K | "O1-class" reasoning. excellent for complex structuring. |
| **Nex N1 (DeepSeek V3.1)** | `nex-agi/nex-n1:free` | 131K | Strong agent autonomy and real-world productivity. |

## ✍️ Tier 2: Content Generation (Drafter)
| Model Name | ID | Context | Strengths |
| :--- | :--- | :--- | :--- |
| **Llama 3.3 70B Instruct** | `meta-llama/llama-3.3-70b-instruct:free` | 131K | **Best Writer**. State-of-the-art open source instruction tuning. Multi-lingual. |
| **Qwen 2.5 VL 7B** | `qwen/qwen-2.5-vl-7b-instruct:free` | 33K | Strong generalist, multimodal capabilities. |
| **Mistral Small 3.1 24B** | `mistralai/mistral-small-3.1-24b-instruct:free` | 128K | Efficient, high-quality text gen. |

## 🎨 Tier 3: Polishing & Refinement
| Model Name | ID | Context | Strengths |
| :--- | :--- | :--- | :--- |
| **Hermes 3 405B** | `nousresearch/hermes-3-llama-3.1-405b:free` | 131K | **Frontier Class**. Incredible nuance and steering options. |
| **Llama 3.1 405B** | `meta-llama/llama-3.1-405b-instruct:free` | 131K | Massive capacity for tone adjustment. |

## 🛠️ Specialized Agents (Coding/Tech)
| Model Name | ID | Context | Strengths |
| :--- | :--- | :--- | :--- |
| **Qwen3 Coder 480B** | `qwen/qwen3-coder-480b-instruct:free` | 262K | Massive coding expert. Great for technical blog snippets. |
| **Devstral 2** | `mistralai/devstral-2-2512:free` | 262K | Agentic coding specialist. |

---

## 🏗️ Auto-Blogger Configuration Plan

Based on this list, the architecture will be upgraded to:

*   **Orchestrator**: `tngtech/deepseek-r1t2-chimera:free` (Reasoning Powerhouse)
*   **Drafter**: `meta-llama/llama-3.3-70b-instruct:free` (Best Open Source Writer)
*   **Critic**: `deepseek/deepseek-r1-0528:free` (Strict logic check)
*   **Polisher**: `nousresearch/hermes-3-llama-3.1-405b:free` (Nuanced style)

*Fallback for all*: `mistralai/mistral-7b-instruct:free` (Reliable baseline)

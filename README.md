# PS02: Offline Security Incident Triage Assistant

[![Python Version](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![Offline Capable](https://img.shields.io/badge/Mode-100%25%20Offline-success.svg)](#)
[![Model](https://img.shields.io/badge/SLM-SmolLM2--135M--Instruct-orange.svg)](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-13%2F13%20Passed-brightgreen.svg)](#)

> **Air-Gapped, Small Language Model-Powered Security Incident Triage Assistant with Deterministic Severity Scoring and Hallucination-Guarded Forensic Reporting.**

---

## 📌 Project & Participant Metadata

- **Event:** Tinyverse Hackathon Phase 2 (Top 24 Individual Finals)
- **Problem Statement:** PS02 — *Offline Security Incident Triage Assistant*
- **Domain:** Cybersecurity | Small Language Models (SLMs)
- **Participant:** Mir Farzin Hussain
- **USN:** `1MS24CI073`
- **Branch:** Computer Science & Engineering (Artificial Intelligence & Machine Learning)
- **Institution:** Ramaiah Institute of Technology

---

## 🎯 Executive Summary

In air-gapped environments, defense enclaves, and critical infrastructure networks (SCADA, power utilities, financial cores), sending security logs to cloud-hosted AI APIs (such as OpenAI, Azure Sentinel Copilot, or Gemini) is **strictly forbidden** due to data leakage regulations.

**PS02 Offline Security Incident Triage Assistant** provides an end-to-end, locally deployed solution that:
1. Ingests and normalizes authentication and endpoint logs from CSV and JSON.
2. Identifies suspicious activity using **four independent detection rules** (failed login bursts, unusual login hours, unapproved privilege escalation, and security control tampering).
3. Correlates related security events across users, endpoints, and IP addresses within sliding time windows using graph-based **Union-Find clustering**.
4. Computes an auditable, **deterministic severity score (0–100)** incorporating compound attack chain synergies.
5. Employs a **genuine locally running Small Language Model (SmolLM2-135M)** to synthesize event timelines, distinguish verified facts from hypotheses, and recommend advisory investigation actions.
6. Enforces **strict programmatic hallucination validation** to ensure no fictitious event IDs are ever cited.
7. Operates **100% offline** with zero internet calls during live triage.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph INGESTION["1. Log Ingestion & Normalization"]
        A1[Auth Logs: CSV / JSON] --> B[Schema Parser & Field Alias Mapper]
        A2[Endpoint Logs: CSV / JSON] --> B
        B --> C[NormalizedEvent Schema\n• Standardized ISO-8601 Timestamps\n• Preserved Raw Event\n• Deterministic SHA-256 Event ID]
    end

    subgraph DETECTION["2. Suspicious Activity Detectors"]
        C --> D1[Rule 1: Failed Logins Burst & Escalation]
        C --> D2[Rule 2: Out-of-Hours & Weekend Access]
        C --> D3[Rule 3: Privilege Escalation & Ticket Check]
        C --> D4[Rule 4: Defense Evasion & Tool Tampering]
    end

    subgraph CORRELATION["3. Event Correlation & Severity"]
        D1 & D2 & D3 & D4 --> E[Temporal Entity Correlator\n• Union-Find Graph Clustering\n• Shared User, Device, or Source IP\n• 30-min Sliding Time Window]
        E --> F[Deterministic Severity Engine\n• Transparent Multi-Factor Score (0-100)\n• Multi-Stage Attack Synergies\n• Critical, High, Medium, Low]
    end

    subgraph OFFLINE_SLM["4. Local SLM Triage & Safety"]
        F --> G[Prompt Defense & Sanitizer\n• Delimiter Containment\n• Strict JSON Output Schema]
        G --> H[Local SLM: SmolLM2-135M / Fallback\n• 100% Offline Weights\n• Zero Cloud APIs]
        H --> I[Hallucination Guard\n• Validate All Cited Event IDs\n• Strip & Flag Hallucinations]
    end

    subgraph REPORTING["5. Multi-Format Reporting & UI"]
        I --> J1[Streamlit SOC Live Dashboard]
        I --> J2[Interactive Modular CLI]
        I --> J3[Multi-Format Exports: JSON, Markdown, PDF]
    end
```

---

## 🔍 Four Independent Detection Rules

| Rule ID | Rule Name | Detection Criteria | Default Threshold |
| :--- | :--- | :--- | :--- |
| `RULE_FAILED_LOGIN_BURST` | Repeated Failed Logins | $\ge N$ failed authentication attempts within a sliding time window. | $\ge 5$ failures in 5 minutes |
| `RULE_BURST_FOLLOWED_BY_SUCCESS` | Credential Burst Followed by Success | Successful logon follows within $M$ minutes of a failed login burst targeting the same identity. | High-risk compromise escalation |
| `RULE_UNUSUAL_LOGIN_HOURS` | Anomalous Out-of-Hours Access | Successful login outside configured business hours or on weekends in configured timezone (`Asia/Kolkata`). | Deep night (00:00–05:00) elevation |
| `RULE_UNAUTHORIZED_PRIV_ESCALATION` | Unapproved Privilege Escalation | Addition of user to privileged group (`Administrators`, `Domain Admins`, `sudo`) without change ticket. | Verified against `approval_reference` |
| `RULE_SECURITY_CONTROL_TAMPERING` | Defense Evasion & Tool Tampering | Commands tampering with Windows Defender, stopping EDR, or executing attack tools (`mimikatz.exe`, `vssadmin delete shadows`). | Instant Critical promotion |

---

## 📊 Empirical Evaluation & Benchmarks

The system was evaluated against a reproducible synthetic benchmark dataset containing five ground-truth scenarios (Scenarios A through E):

| Metric | Score | Validation Note |
| :--- | :--- | :--- |
| **Precision** | **1.00 (100%)** | Zero false-positive alerts on benign operational baselines |
| **Recall** | **1.00 (100%)** | All 7 ground-truth attack rules successfully triggered |
| **F1-Score** | **1.00 (100%)** | Optimal balance across all attack scenarios |
| **False Positive Rate** | **0.00%** | Approved maintenance activities correctly dampened |
| **Ingestion Throughput** | **605 EPS** | Events per second processed on local machine |
| **Pipeline Latency** | **35.1 ms** | Ingestion + Detection + Correlation + Severity scoring |
| **Test Coverage** | **13 / 13 Passed** | 100% pass rate across automated pytest suites |

> **Evaluation Disclosure:** All metrics are empirically measured against the labelled synthetic demonstration dataset. They are not represented as enterprise production telemetry.

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10 to 3.14
- Git
- 4 GB RAM minimum (6 GB+ recommended for local SLM)

### 2. Virtual Environment Setup
```powershell
cd PS02_Offline_Security_Incident_Triage_Assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install pinned dependencies
pip install -r requirements.txt
```

### 3. Local Model Verification
The genuine Small Language Model (`HuggingFaceTB/SmolLM2-135M-Instruct`) is cached in `models/SmolLM2-135M-Instruct`.
To re-cache or verify offline weights:
```powershell
python src/cli.py download-model
```

### 4. Run Automated Test Suite
```powershell
python -m pytest tests -v
```

---

## 🖥️ Running the Application

### Option A: Interactive Streamlit SOC Dashboard
```powershell
streamlit run src/app.py
```
Access the live SOC interface in your browser:
- **Overview:** Active KPIs, severity distributions, and active cases.
- **Telemetry Ingestion:** Upload custom CSV/JSON or load synthetic test data.
- **Correlated Incidents:** Detailed cluster cards, attack synergies, and timeline audits.
- **Incident Deep Dive:** Verified facts vs. hypotheses, advisory recommendations, and 1-click PDF/Markdown/JSON downloads.
- **Evaluation:** Live benchmark execution matrix.

### Option B: Command Line Interface (CLI)
```powershell
# Run full offline triage on synthetic datasets
python src/cli.py triage

# Run benchmark evaluation against ground truth
python src/cli.py benchmark
```

---

## 🛡️ Security, Human-in-the-Loop & Safety Guardrails

1. **Advisory Triage Only:** The assistant does **NOT** autonomously disable user accounts, isolate endpoints, or execute remediation commands. All suggested actions are advisory and require human analyst review.
2. **Defensive Prompt Engineering:** Log field contents are wrapped inside `<INCIDENT_TELEMETRY>` tags and stripped of injection markers, preventing untrusted logs from overriding system directives.
3. **Programmatic Hallucination Validation:** The `SLMOutputValidator` regex-scans all model outputs and verifies that every cited Event ID exists in the ground truth. Fictitious event IDs are immediately stripped and flagged.

---

## 📜 AI Usage & Third-Party Disclosure

- **AI Assistance:** Architectural design, test generation, and presentation scripting were assisted by AI coding agents under participant direction. All code was reviewed, debugged, and verified by participant Mir Farzin Hussain.
- **Model Attribution:** `HuggingFaceTB/SmolLM2-135M-Instruct` is developed by Hugging Face TB and released under the **Apache 2.0 License**.
- **Third-Party Libraries:** Pydantic (MIT), Streamlit (Apache 2.0), ReportLab (BSD), python-pptx (MIT), Pytest (MIT).

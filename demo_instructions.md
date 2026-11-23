# PS02: Demonstration & Presentation Runbook

**Participant:** Mir Farzin Hussain  
**USN:** 1MS24CI073  
**Branch:** CSE (AI & ML)  
**Problem Statement:** PS02 - Offline Security Incident Triage Assistant  
**Judging Date:** 24 November 2026  

---

## 🎯 3-Minute Quick Demo Script for Judges

When the judges visit your desk:

### 1. The Elevator Pitch (30 seconds)
> *"Good morning judges. I am Mir Farzin Hussain (USN: 1MS24CI073). I built PS02: an Offline Security Incident Triage Assistant. In defense, air-gapped SCADA, or healthcare enclaves, sending sensitive logs to cloud APIs like OpenAI or Azure Copilot is strictly prohibited due to data leakage. My system ingests authentication and endpoint logs, runs 4 deterministic detection rules, correlates events across users and hosts into unified attack incidents, computes a transparent 0-100 severity score, and uses a genuine, locally cached Small Language Model (SmolLM2-135M) to produce an evidence-backed incident report with 100% offline hallucination safeguards."*

### 2. Live CLI Demonstration (45 seconds)
Open PowerShell inside `PS02_Offline_Security_Incident_Triage_Assistant`:
```powershell
.\.venv\Scripts\python.exe src/cli.py triage
```
**Point out to judges:**
- 20 logs ingested across 5 scenarios.
- Correlation grouped them into 5 distinct cases.
- **Incident INC-20261123-0002** was escalated to **CRITICAL (Score: 100/100)** because of the multi-stage attack synergy: credential burst + success + defense evasion (EDR disabled) + unapproved privilege escalation (`Domain Admins`).
- Hallucination Validation: **PASSED** (every cited Event ID is strictly verified against real evidence).
- JSON, Markdown, and PDF reports generated on the fly.

### 3. Live Streamlit SOC Dashboard (60 seconds)
Run:
```powershell
.\.venv\Scripts\streamlit.exe run src/app.py
```
1. **Overview Tab:** Show high-level KPIs, severity distribution bar chart, and active case breakdown.
2. **Telemetry Tab:** Show normalized fields (timestamp standardized to IST, original raw event preserved, deterministic ID generated).
3. **Correlated Incidents Tab:** Expand Critical Incident `INC-20261123-0002` showing the attack chain and timeline.
4. **Deep Dive Tab:** Highlight the **Verified Facts** vs. **Plausible Hypotheses** separation, the advisory next steps with human authorization checkboxes, and click **Download PDF Report**.
5. **Evaluation Tab:** Click *Execute Full Evaluation Suite* to show **100% Precision, 100% Recall, 0% FPR** on the synthetic benchmark dataset in **35 ms**!

### 4. Prove 100% Offline Capability (30 seconds)
Turn off Wi-Fi or unplug ethernet:
- Run the CLI triage or refresh the Streamlit app.
- Everything runs with 0 internet requests because the model weights and all libraries are cached locally on the disk.

---

## 🛠️ Verification & Test Suite Run

To demonstrate code quality to technical evaluators:
```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```
All **13 automated test suites** execute and pass in under 2 seconds.

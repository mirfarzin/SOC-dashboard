# PS02 Viva Preparation & Defense Architecture Guide

**Participant:** Mir Farzin Hussain  
**USN:** 1MS24CI073  
**Branch:** CSE (AI & ML)  
**Project:** Offline Security Incident Triage Assistant (PS02)  

---

## ❓ 1. Problem Statement & Architecture

### Q: What is the core problem PS02 solves?
**A:** Traditional Security Operations Centers (SOCs) are overwhelmed by thousands of disconnected security logs. Analysts suffer from alert fatigue. While cloud AI assistants exist, they cannot be used in **air-gapped networks** (defense, nuclear plants, core banking, critical infrastructure) because uploading employee usernames, server hostnames, and IP addresses violates security compliance. PS02 runs **100% offline**, performing log ingestion, multi-rule detection, event correlation, deterministic severity classification, and local Small Language Model (SLM) triage without sending a single byte outside the machine.

### Q: Why not let the SLM classify the severity directly?
**A:** Small Language Models (and LLMs in general) are stochastic and non-deterministic; they can suffer from prompt sensitivity or drift, assigning "Medium" to an attack on one run and "Critical" on the next. For forensic and compliance reasons, **severity must be auditable, transparent, and reproducible**. In our architecture, the **Deterministic Severity Engine** is the sole authority for assigning severity (0–100 score based on documented weights and attack synergy bonuses). The SLM is used for what it excels at: **synthesizing context, explaining timelines, and drafting analyst briefing reports**.

---

## ❓ 2. Detection & Correlation Algorithms

### Q: How does your Event Correlation algorithm work?
**A:** We use **Disjoint-Set Union (Union-Find) graph clustering**:
1. Detection findings and context events are treated as nodes.
2. An edge is formed between finding $A$ and finding $B$ if:
   - They share at least one identity entity (same username, or same hostname/device, or same source IP), **AND**
   - The temporal distance between their event time ranges is within the configurable sliding window (default: $1800\text{ seconds} = 30\text{ minutes}$).
3. Connected components form unified, deduplicated **Incident Cases**.
4. Events within each incident are sorted chronologically into an event timeline with relative second offsets ($t_0, t_0 + \Delta t$).

### Q: Explain your four detection rules.
1. **Rule 1: Repeated Failed Logins with Burst Escalation (`RULE_FAILED_LOGIN_BURST` & `RULE_BURST_FOLLOWED_BY_SUCCESS`)**:
   - Detects $\ge 5$ authentication failures within a 5-minute sliding window.
   - If a successful logon follows for that same identity within 10 minutes, the rule escalates the finding to a high-risk credential breach.
2. **Rule 2: Unusual Login Hours (`RULE_UNUSUAL_LOGIN_HOURS`)**:
   - Converts event timestamps to the organization timezone (`Asia/Kolkata`).
   - Flags logins outside 09:00–18:00 or on non-business days (weekends).
   - Contextual logic applies extra weight if the account has administrative privileges or logs in during deep night (00:00–05:00).
3. **Rule 3: Privilege Escalation & Sensitive Groups (`RULE_UNAUTHORIZED_PRIV_ESCALATION` & `RULE_AUTHORIZED_PRIV_ESCALATION`)**:
   - Detects additions to sensitive groups (`Administrators`, `Domain Admins`, `sudo`, `wheel`).
   - Checks for a valid change ticket or approval reference (`approval_reference`).
   - If an approval ticket is present, the event is categorized as authorized (low severity); if missing, it triggers a critical unauthorized privilege anomaly.
4. **Rule 4: Endpoint Defense Tampering & Attack Utilities (`RULE_SECURITY_CONTROL_TAMPERING` & `RULE_SUSPICIOUS_PROCESS_EXECUTION`)**:
   - Detects offensive utilities (`mimikatz.exe`, `vssadmin delete shadows`, encoded powershell) and defense evasion commands (disabling Windows Defender, stopping EDR services).

---

## ❓ 3. Small Language Model (SLM) & Hallucination Defense

### Q: Which model did you choose and why?
**A:** We integrated **`HuggingFaceTB/SmolLM2-135M-Instruct`**:
- **Size:** ~135 Million parameters (~270 MB safetensors file).
- **License:** Apache 2.0 (permissive, open-source).
- **Footprint:** Requires < 1 GB RAM, running smoothly on standard CPUs or laptops without requiring discrete GPU clusters.
- **Offline Delivery:** The model weights and tokenizer are pre-cached in `models/SmolLM2-135M-Instruct` and loaded with `local_files_only=True`.
- **Fallback Resilience:** If running in ultra-fast mode or if weights are absent, a deterministic heuristic engine generates identical structured reports in < 2 milliseconds.

### Q: How do you prevent hallucinations in the SLM triage report?
**A:** We implement a two-tier safeguard:
1. **Defensive Delimited Prompting:**
   - Raw logs are wrapped inside `<INCIDENT_TELEMETRY>`.
   - Field sanitization strips special characters and control delimiters to prevent prompt injection.
   - System instruction strictly enforces pure JSON conforming to a rigid schema.
2. **Programmatic Evidence Validator (`SLMOutputValidator`):**
   - After parsing the SLM JSON, every single event ID cited in `referenced_event_ids` or extracted from text fields via regex is cross-referenced against the incident's ground-truth `event_ids`.
   - If an event ID does not exist in the ingested logs, `validation_passed` is set to `False`, the hallucinated ID is stripped, and an audit warning is permanently logged in the report.

---

## ❓ 4. Safety & Human-in-the-Loop Guardrails

### Q: Does your assistant automatically block IP addresses or isolate computers?
**A:** **No.** By design, this system is an **advisory triage assistant**, not an autonomous response agent. In high-consequence enterprise environments, automated isolation based on AI inference risks breaking critical business operations (e.g. accidentally isolating a domain controller or hospital database).
- Every recommendation is marked **ADVISORY ONLY**.
- The Streamlit UI includes explicit human authorization checkboxes for analysts to confirm actions before execution.

---

## ❓ 5. Performance & Benchmarking

### Q: What were your evaluation results?
**A:** Evaluated against a labelled benchmark dataset representing 5 distinct scenarios (Scenarios A through E):
- **Precision:** 100% (No false-positive alarms on benign baseline).
- **Recall:** 100% (All 7 ground-truth detection rules triggered).
- **F1-Score:** 1.00.
- **False Positive Rate:** 0.00%.
- **Ingestion Throughput:** 605 Events Per Second (EPS).
- **Pipeline Latency:** 35.1 milliseconds.
- **Unit & Integration Tests:** 13 / 13 passed with 100% success rate.

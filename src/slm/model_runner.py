"""
Local Small Language Model (SLM) Runner for PS02.
Operates 100% offline using locally stored model weights or transparent,
evidence-grounded heuristic fallback.
Never calls cloud APIs (No OpenAI, No Gemini, No Groq).
"""

from __future__ import annotations
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.config import AppConfig
from src.schema import Incident, SLMReportAnalysis
from src.slm.prompt_builder import build_triage_prompt
from src.slm.validator import SLMOutputValidator


class RuleBasedSLMFallback:
    """
    High-fidelity, deterministic triage intelligence generator.
    Used when local SLM weights are absent or when running in pure deterministic offline mode.
    Strictly grounds every fact in real event telemetry and never cites non-existent IDs.
    """

    @staticmethod
    def generate(incident: Incident, reason: str = "SLM weights not loaded") -> SLMReportAnalysis:
        rule_ids = set(f.rule_id for f in incident.findings)
        users = incident.entities_involved.get("users", [])
        hosts = incident.entities_involved.get("hosts", [])
        ips = incident.entities_involved.get("ips", [])

        user_label = ", ".join(users) if users else "unspecified identity"
        host_label = ", ".join(hosts) if hosts else "unspecified host"
        ip_label = ", ".join(ips) if ips else "internal/local"

        facts = []
        hypotheses = []
        rule_explanations = []
        missing_evidence = []
        recommended_actions = []

        # 1. Facts grounded directly in events
        for f in incident.findings:
            eids_str = ", ".join(f.supporting_event_ids[:4])
            facts.append(
                f"Rule '{f.rule_name}' confirmed by event(s) [{eids_str}]: {f.description}"
            )
            rule_explanations.append(f.explanation)

        if incident.timeline:
            first_evt = incident.timeline[0]
            last_evt = incident.timeline[-1]
            facts.append(
                f"Activity sequence commenced at {first_evt.get('timestamp')} (Event {first_evt.get('event_id')}) "
                f"and concluded at {last_evt.get('timestamp')} (Event {last_evt.get('event_id')})."
            )

        # 2. Hypotheses based on attack patterns
        if "RULE_BURST_FOLLOWED_BY_SUCCESS" in rule_ids:
            hypotheses.append(
                f"High probability of credential stuffing, password spray, or brute-force attack against '{user_label}' "
                f"culminating in unauthorized account breach."
            )
            recommended_actions.append(f"Promptly invalidate active web and Kerberos sessions for account '{user_label}'.")
            recommended_actions.append(f"Block remote ingress from source IP(s): {ip_label} at perimeter firewall.")
            missing_evidence.append(f"Perimeter VPN and Web Application Firewall (WAF) logs for source IP(s) {ip_label}.")

        elif "RULE_FAILED_LOGIN_BURST" in rule_ids:
            hypotheses.append(
                f"Automated credential spray or misconfigured script causing rapid authentication failures for '{user_label}'."
            )
            recommended_actions.append(f"Inspect host '{host_label}' for cached credential failure loops or scheduled tasks.")

        if "RULE_UNAUTHORIZED_PRIV_ESCALATION" in rule_ids:
            hypotheses.append(
                f"Threat actor or rogue administrator establishing persistent root/administrative access on '{host_label}' "
                "outside legitimate change approval workflows."
            )
            recommended_actions.append(
                f"Verify authorization of '{user_label}' group membership change with Change Advisory Board (CAB)."
            )
            recommended_actions.append(
                f"If unauthorized, revoke elevated privileges for '{user_label}' and audit recent audit log deletions."
            )
            missing_evidence.append("Active Directory Security Event 4672 / 4728 audit trail to identify the originating security principal.")

        if "RULE_UNUSUAL_LOGIN_HOURS" in rule_ids:
            hypotheses.append(
                f"Off-hours access by '{user_label}' may indicate compromised credentials exploited during low-monitoring windows "
                "or legitimate after-hours operational overtime."
            )
            recommended_actions.append(
                f"Directly contact user '{user_label}' via secondary out-of-band communication (phone/manager) to verify physical presence."
            )

        if "RULE_SECURITY_CONTROL_TAMPERING" in rule_ids:
            hypotheses.append(
                f"Adversary actively engaging in Defense Evasion (MITRE ATT&CK T1562) to disable EDR / antivirus monitoring on '{host_label}'."
            )
            recommended_actions.append(f"Immediately isolate endpoint '{host_label}' from local VLAN pending forensic memory acquisition.")
            missing_evidence.append(f"EDR process tree and PowerShell ScriptBlock logging (Event ID 4104) from '{host_label}'.")

        if not missing_evidence:
            missing_evidence.append("Host memory dump and surrounding network connection telemetry.")
        if not recommended_actions:
            recommended_actions.append("Conduct standard analyst triage review and interview asset custodian.")

        # Executive summary
        summary = (
            f"Automated triage analyzed Incident {incident.incident_id} involving identity '{user_label}' and "
            f"device '{host_label}'. Deterministic severity engine assigned {incident.severity.value.upper()} "
            f"(Score: {incident.severity_score}/100) based on {len(incident.findings)} triggered detection rule(s). "
            f"Primary indicators: {'; '.join(f.rule_name for f in incident.findings)}."
        )

        raw_payload = {
            "title": incident.title,
            "executive_summary": summary,
            "facts": facts,
            "hypotheses": hypotheses,
            "rule_explanations": rule_explanations,
            "missing_evidence": missing_evidence,
            "recommended_actions": recommended_actions,
            "referenced_event_ids": sorted(list(incident.event_ids))[:10],
            "model_name": f"Deterministic Heuristic Fallback ({reason})",
            "is_fallback": True
        }

        return SLMOutputValidator.validate_and_clean(raw_payload, incident)


class LocalSLMRunner:
    """
    Manages local Small Language Model inference.
    Executes entirely offline using cached weights or cleanly falls back.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self._load_attempted = False
        self._is_ready = False
        self._load_error: Optional[str] = None

    def load_model(self) -> bool:
        """Attempt to load local model weights from configured offline path."""
        if self._load_attempted:
            return self._is_ready

        self._load_attempted = True
        local_path = Path(self.config.slm.local_model_path)
        base_dir = Path(__file__).resolve().parent.parent.parent

        # Robust path resolution across diverse execution working directories
        if not (local_path.exists() and (local_path / "config.json").exists()):
            if (base_dir / local_path).exists() and (base_dir / local_path / "config.json").exists():
                local_path = base_dir / local_path
            else:
                stripped_parts = [part for part in local_path.parts if part != "PS02_Offline_Security_Incident_Triage_Assistant"]
                if stripped_parts:
                    stripped = Path(*stripped_parts)
                    if (base_dir / stripped).exists() and (base_dir / stripped / "config.json").exists():
                        local_path = base_dir / stripped
                    elif stripped.exists() and (stripped / "config.json").exists():
                        local_path = stripped

        # Check if local path exists with weights
        if not local_path.exists() or not (local_path / "config.json").exists():
            self._load_error = f"Local model weights directory '{local_path}' not found or incomplete."
            return False

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            print(f"[SLM] Loading local model from {local_path} (Offline Mode)...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(local_path),
                local_files_only=True
            )
            load_kwargs = {"local_files_only": True}
            if self.config.slm.device == "cuda" and torch.cuda.is_available():
                load_kwargs["device_map"] = "cuda"
            self.model = AutoModelForCausalLM.from_pretrained(
                str(local_path),
                **load_kwargs
            )
            self._is_ready = True
            print("[SLM] Model loaded successfully in offline mode!")
            return True
        except Exception as e:
            self._load_error = f"Failed loading local model: {e}"
            print(f"[SLM ERROR] {self._load_error}")
            return False

    @property
    def is_available(self) -> bool:
        if not self._load_attempted:
            self.load_model()
        return self._is_ready

    def analyze(self, incident: Incident) -> Tuple[SLMReportAnalysis, float]:
        """
        Run inference on the incident.
        Returns (SLMReportAnalysis, latency_ms).
        """
        start_time = time.perf_counter()

        # If model is not loaded, use deterministic fallback
        if not self.is_available:
            reason = self._load_error or "Offline mode active without pre-downloaded weights"
            res = RuleBasedSLMFallback.generate(incident, reason=reason)
            latency = (time.perf_counter() - start_time) * 1000
            return res, latency

        # Generate using local SLM
        try:
            import torch
            prompt = build_triage_prompt(incident)
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.config.slm.device != "cpu" and torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            gen_start = time.perf_counter()
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.config.slm.max_new_tokens,
                    temperature=self.config.slm.temperature,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            generated_text = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            latency = (time.perf_counter() - start_time) * 1000

            # Parse JSON from generated text
            parsed_json = self._extract_json(generated_text)
            if parsed_json:
                parsed_json["model_name"] = f"Local SLM ({self.config.slm.model_id})"
                parsed_json["is_fallback"] = False
                res = SLMOutputValidator.validate_and_clean(parsed_json, incident)
                return res, latency
            else:
                # Malformed JSON, fallback
                res = RuleBasedSLMFallback.generate(incident, reason="SLM output did not adhere to valid JSON syntax")
                return res, latency

        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            res = RuleBasedSLMFallback.generate(incident, reason=f"Inference exception: {e}")
            return res, latency

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract first valid JSON object from model output."""
        text = text.strip()
        # Look for outermost braces
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end + 1]
            try:
                return json.loads(json_str)
            except Exception:
                pass
        return None

"""
Evaluation and Metrics Engine for PS02.
Benchmarks detection outputs against synthetic ground-truth labels.
Computes True Positives, False Positives, False Negatives, Precision, Recall, F1,
and system throughput/latency.
"""

from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Set

from src.schema import Incident, NormalizedEvent
from src.ingestion.parser import ingest_file
from src.detection.engine import DetectionEngine
from src.correlation.correlator import EventCorrelator
from src.severity.classifier import SeverityClassifier
from src.config import AppConfig


class EvaluationSuite:
    def __init__(self, config: AppConfig):
        self.config = config

    def run_benchmark(
        self,
        auth_file: Path | str,
        endpoint_file: Path | str,
        ground_truth_file: Path | str
    ) -> Dict[str, Any]:
        """
        Execute end-to-end evaluation pipeline and compute statistical metrics.
        """
        # Load ground truth
        with open(ground_truth_file, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
        scenarios = gt_data.get("scenarios", {})

        # 1. Ingestion Benchmark
        t0 = time.perf_counter()
        res_auth = ingest_file(auth_file, default_tz=self.config.organization.timezone)
        res_endp = ingest_file(endpoint_file, default_tz=self.config.organization.timezone)
        ingestion_time_s = time.perf_counter() - t0

        all_events = res_auth.events + res_endp.events
        total_events = len(all_events)
        throughput_eps = total_events / max(ingestion_time_s, 0.0001)

        # 2. Detection Benchmark
        detection_engine = DetectionEngine(self.config)
        t1 = time.perf_counter()
        findings = detection_engine.run(all_events)
        detection_time_ms = (time.perf_counter() - t1) * 1000

        # 3. Correlation Benchmark
        correlator = EventCorrelator(self.config)
        t2 = time.perf_counter()
        raw_incidents = correlator.correlate(all_events, findings)
        correlation_time_ms = (time.perf_counter() - t2) * 1000

        # 4. Severity Classification Benchmark
        classifier = SeverityClassifier(self.config)
        t3 = time.perf_counter()
        incidents = [classifier.classify(inc) for inc in raw_incidents]
        classification_time_ms = (time.perf_counter() - t3) * 1000

        # 5. Evaluate against Ground Truth
        # For each scenario, check if expected rules were detected and if expected severity matches
        detected_rule_ids = set(f.rule_id for f in findings)
        all_expected_rules = set()
        for s in scenarios.values():
            all_expected_rules.update(s.get("expected_rules", []))

        # True Positives: Expected rules that fired
        tp_rules = detected_rule_ids.intersection(all_expected_rules)
        tp = len(tp_rules)

        # False Positives: Rules that fired but were not expected in any ground truth scenario
        fp_rules = detected_rule_ids - all_expected_rules
        fp = len(fp_rules)

        # False Negatives: Rules expected in ground truth that did not fire
        fn_rules = all_expected_rules - detected_rule_ids
        fn = len(fn_rules)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + max(1, len(all_expected_rules)))

        # Severity distribution
        severity_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        for inc in incidents:
            severity_dist[inc.severity.value] += 1

        # Check Scenario-level match
        scenario_results = {}
        for s_key, s_data in scenarios.items():
            expected_rules = set(s_data.get("expected_rules", []))
            target_entity = s_data.get("entity", "").lower()

            # Find matching incident
            matched_inc = None
            for inc in incidents:
                inc_users = [u.lower() for u in inc.entities_involved.get("users", [])]
                if target_entity in inc_users:
                    matched_inc = inc
                    break

            if matched_inc:
                inc_rules = set(f.rule_id for f in matched_inc.findings)
                rule_match = expected_rules.issubset(inc_rules) or bool(expected_rules.intersection(inc_rules))
                sev_match = (matched_inc.severity.value.lower() == s_data.get("expected_severity", "").lower())
                scenario_results[s_key] = {
                    "matched": True,
                    "incident_id": matched_inc.incident_id,
                    "rules_matched": list(expected_rules.intersection(inc_rules)),
                    "severity_assigned": matched_inc.severity.value,
                    "expected_severity": s_data.get("expected_severity"),
                    "severity_correct": sev_match
                }
            else:
                scenario_results[s_key] = {
                    "matched": False,
                    "reason": "No incident grouped for target entity"
                }

        return {
            "evaluation_notice": "RESULTS BASED ON SYNTHETIC BENCHMARK DATASET. NOT AN ENTERPRISE PRODUCTION BENCHMARK.",
            "metrics": {
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "false_positive_rate": round(fpr, 4)
            },
            "performance": {
                "total_events_processed": total_events,
                "ingestion_throughput_eps": round(throughput_eps, 2),
                "ingestion_latency_s": round(ingestion_time_s, 4),
                "detection_latency_ms": round(detection_time_ms, 2),
                "correlation_latency_ms": round(correlation_time_ms, 2),
                "severity_scoring_latency_ms": round(classification_time_ms, 2),
                "total_pipeline_latency_ms": round((ingestion_time_s * 1000) + detection_time_ms + correlation_time_ms + classification_time_ms, 2)
            },
            "incidents_summary": {
                "total_incidents_formed": len(incidents),
                "severity_distribution": severity_dist
            },
            "scenarios_evaluation": scenario_results
        }

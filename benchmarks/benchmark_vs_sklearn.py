#!/usr/bin/env python3
"""
WaveGuard vs Scikit-learn Anomaly Detection Benchmark
=====================================================

Compares WaveGuard API against:
  - Isolation Forest (sklearn)
  - Local Outlier Factor (sklearn)
  - One-Class SVM (sklearn)

on 6 realistic anomaly detection scenarios:
  1. Server metrics (IT ops)
  2. Financial transactions (fraud)
  3. IoT sensor readings (industrial)
  4. Network traffic (security)
  5. Time-series with drift (monitoring)
  6. High-dimensional sparse data

Metrics: Precision, Recall, F1, AUC-ROC, Latency
"""

import json
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np

warnings.filterwarnings("ignore")

# ── Sklearn methods ─────────────────────────────────────────────────────
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix,
)

# ── WaveGuard SDK ───────────────────────────────────────────────────────
from waveguard import WaveGuard


# ═════════════════════════════════════════════════════════════════════════
# Dataset generators
# ═════════════════════════════════════════════════════════════════════════

def _to_native(d: Dict) -> Dict:
    """Convert numpy types to Python native types for JSON serialization."""
    return {k: (int(v) if isinstance(v, (np.integer,)) else
               float(v) if isinstance(v, (np.floating,)) else v)
            for k, v in d.items()}


def _make_scenario(
    name: str,
    description: str,
    feature_names: List[str],
    normal_generator,
    anomaly_generator,
    n_train: int = 30,
    n_test_normal: int = 20,
    n_test_anomaly: int = 10,
    seed: int = 42,
) -> Dict[str, Any]:
    """Create a benchmark scenario with labeled data."""
    rng = np.random.RandomState(seed)

    training = [_to_native(normal_generator(rng)) for _ in range(n_train)]
    test_normal = [_to_native(normal_generator(rng)) for _ in range(n_test_normal)]
    test_anomaly = [_to_native(anomaly_generator(rng)) for _ in range(n_test_anomaly)]

    test_data = test_normal + test_anomaly
    labels = [0] * n_test_normal + [1] * n_test_anomaly  # 0=normal, 1=anomaly

    # Shuffle
    idx = list(range(len(test_data)))
    rng.shuffle(idx)
    test_data = [test_data[i] for i in idx]
    labels = [labels[i] for i in idx]

    return {
        "name": name,
        "description": description,
        "feature_names": feature_names,
        "training": training,
        "test": test_data,
        "labels": labels,
        "n_train": n_train,
        "n_test_normal": n_test_normal,
        "n_test_anomaly": n_test_anomaly,
    }


def scenario_server_metrics():
    """Scenario 1: IT server monitoring — detect compromised servers."""
    features = ["cpu_pct", "memory_pct", "disk_io_kbps", "network_mbps",
                 "error_rate", "latency_ms", "connections", "swap_pct"]

    def normal(rng):
        return dict(zip(features, [
            rng.normal(45, 8),    # cpu
            rng.normal(62, 5),    # memory
            rng.normal(120, 20),  # disk io
            rng.normal(50, 10),   # network
            rng.exponential(0.5), # error rate
            rng.normal(25, 5),    # latency
            rng.normal(150, 30),  # connections
            rng.normal(10, 3),    # swap
        ]))

    def anomaly(rng):
        kind = rng.choice(["crypto", "ddos", "leak", "crash"])
        if kind == "crypto":
            return dict(zip(features, [
                rng.normal(98, 1), 85 + rng.normal(0, 2), rng.normal(400, 50),
                rng.normal(10, 3), rng.normal(2, 1), rng.normal(150, 30),
                rng.normal(20, 5), rng.normal(60, 10),
            ]))
        elif kind == "ddos":
            return dict(zip(features, [
                rng.normal(75, 5), rng.normal(70, 5), rng.normal(100, 20),
                rng.normal(500, 50), rng.normal(15, 5), rng.normal(800, 200),
                rng.normal(5000, 500), rng.normal(15, 5),
            ]))
        elif kind == "leak":
            return dict(zip(features, [
                rng.normal(50, 5), rng.normal(95, 2), rng.normal(300, 50),
                rng.normal(200, 30), rng.normal(8, 2), rng.normal(500, 100),
                rng.normal(200, 30), rng.normal(85, 5),
            ]))
        else:  # crash
            return dict(zip(features, [
                rng.normal(5, 2), rng.normal(20, 5), rng.normal(5, 2),
                rng.normal(2, 1), rng.normal(50, 10), rng.normal(5000, 1000),
                rng.normal(0, 1), rng.normal(5, 2),
            ]))

    return _make_scenario(
        "Server Metrics (IT Ops)", "Detect compromised/failing servers",
        features, normal, anomaly,
    )


def scenario_fraud():
    """Scenario 2: Financial transaction fraud detection."""
    features = ["amount", "items", "session_sec", "returning_customer",
                 "hour_of_day", "distance_km", "failed_attempts", "velocity"]

    def normal(rng):
        return dict(zip(features, [
            rng.lognormal(3.5, 0.8),   # amount ~$30-150
            rng.poisson(3) + 1,         # items
            rng.normal(300, 100),        # session time
            rng.binomial(1, 0.7),        # returning
            rng.choice(range(8, 22)),    # business hours
            rng.exponential(15),         # distance
            0,                           # no failures
            rng.exponential(2),          # velocity (txn/day)
        ]))

    def anomaly(rng):
        kind = rng.choice(["card_testing", "big_fraud", "bot", "account_takeover"])
        if kind == "card_testing":
            return dict(zip(features, [
                rng.uniform(0.01, 1.0), 1, rng.uniform(1, 5), 0,
                rng.choice(range(0, 6)), rng.uniform(500, 2000),
                rng.randint(3, 10), rng.uniform(50, 200),
            ]))
        elif kind == "big_fraud":
            return dict(zip(features, [
                rng.uniform(2000, 15000), rng.randint(10, 30), rng.uniform(5, 20), 0,
                rng.choice(range(0, 6)), rng.uniform(1000, 5000),
                rng.randint(0, 2), rng.uniform(5, 20),
            ]))
        elif kind == "bot":
            return dict(zip(features, [
                rng.uniform(50, 200), rng.randint(1, 3), rng.uniform(1, 3), 0,
                rng.choice(range(0, 24)), rng.uniform(0, 10),
                0, rng.uniform(100, 500),
            ]))
        else:  # account_takeover
            return dict(zip(features, [
                rng.lognormal(3.5, 0.8), rng.poisson(3) + 1, rng.uniform(10, 30), 1,
                rng.choice(range(0, 6)), rng.uniform(2000, 8000),
                rng.randint(2, 8), rng.uniform(10, 50),
            ]))

    return _make_scenario(
        "Financial Fraud", "Detect fraudulent transactions",
        features, normal, anomaly,
    )


def scenario_iot():
    """Scenario 3: IoT industrial sensor readings."""
    features = ["temperature_c", "pressure_psi", "vibration_g", "humidity_pct",
                 "flow_rate_lpm", "voltage_v", "current_a", "rpm",
                 "bearing_temp_c", "oil_viscosity"]

    def normal(rng):
        return dict(zip(features, [
            rng.normal(72, 3),      # temp
            rng.normal(14.7, 0.3),  # pressure
            rng.normal(0.5, 0.15),  # vibration
            rng.normal(45, 5),      # humidity
            rng.normal(100, 8),     # flow rate
            rng.normal(220, 5),     # voltage
            rng.normal(15, 2),      # current
            rng.normal(1750, 25),   # rpm
            rng.normal(55, 3),      # bearing temp
            rng.normal(32, 2),      # oil viscosity
        ]))

    def anomaly(rng):
        kind = rng.choice(["bearing_fail", "leak", "overload", "voltage_sag"])
        if kind == "bearing_fail":
            return dict(zip(features, [
                rng.normal(95, 5), rng.normal(14.7, 0.3), rng.normal(3.5, 0.5),
                rng.normal(45, 5), rng.normal(95, 8), rng.normal(220, 5),
                rng.normal(20, 3), rng.normal(1700, 50),
                rng.normal(120, 10), rng.normal(18, 3),
            ]))
        elif kind == "leak":
            return dict(zip(features, [
                rng.normal(72, 3), rng.normal(8, 1), rng.normal(0.5, 0.15),
                rng.normal(80, 5), rng.normal(30, 5), rng.normal(220, 5),
                rng.normal(15, 2), rng.normal(1750, 25),
                rng.normal(55, 3), rng.normal(32, 2),
            ]))
        elif kind == "overload":
            return dict(zip(features, [
                rng.normal(88, 3), rng.normal(18, 1), rng.normal(2.0, 0.3),
                rng.normal(45, 5), rng.normal(160, 10), rng.normal(210, 8),
                rng.normal(35, 5), rng.normal(1850, 30),
                rng.normal(80, 5), rng.normal(25, 2),
            ]))
        else:
            return dict(zip(features, [
                rng.normal(72, 3), rng.normal(14.7, 0.3), rng.normal(0.8, 0.2),
                rng.normal(45, 5), rng.normal(80, 10), rng.normal(185, 10),
                rng.normal(22, 4), rng.normal(1650, 40),
                rng.normal(60, 5), rng.normal(32, 2),
            ]))

    return _make_scenario(
        "IoT Sensor (Industrial)", "Detect equipment anomalies from sensor data",
        features, normal, anomaly,
    )


def scenario_network():
    """Scenario 4: Network traffic anomaly detection."""
    features = ["bytes_in", "bytes_out", "packets", "duration_sec",
                 "src_port_entropy", "dst_port_count", "syn_ratio", "payload_entropy"]

    def normal(rng):
        return dict(zip(features, [
            rng.lognormal(8, 1),     # bytes in
            rng.lognormal(7, 1),     # bytes out
            rng.lognormal(5, 0.5),   # packets
            rng.exponential(30),      # duration
            rng.uniform(3.0, 4.5),   # src port entropy
            rng.poisson(5) + 1,      # dst port count
            rng.uniform(0.01, 0.1),  # syn ratio
            rng.uniform(5.0, 7.5),   # payload entropy
        ]))

    def anomaly(rng):
        kind = rng.choice(["port_scan", "exfiltration", "c2", "dos"])
        if kind == "port_scan":
            return dict(zip(features, [
                rng.lognormal(5, 0.5), rng.lognormal(4, 0.5),
                rng.lognormal(8, 0.3), rng.uniform(1, 5),
                rng.uniform(1.0, 2.0), rng.randint(100, 1000),
                rng.uniform(0.8, 1.0), rng.uniform(0, 1),
            ]))
        elif kind == "exfiltration":
            return dict(zip(features, [
                rng.lognormal(6, 0.5), rng.lognormal(12, 0.5),
                rng.lognormal(7, 0.3), rng.uniform(100, 600),
                rng.uniform(3.0, 4.0), rng.poisson(2) + 1,
                rng.uniform(0.01, 0.05), rng.uniform(7.5, 8.0),
            ]))
        elif kind == "c2":
            return dict(zip(features, [
                rng.lognormal(4, 0.3), rng.lognormal(4, 0.3),
                rng.lognormal(3, 0.3), rng.uniform(0.1, 1),
                rng.uniform(0.5, 1.5), 1,
                rng.uniform(0.01, 0.05), rng.uniform(7.8, 8.0),
            ]))
        else:
            return dict(zip(features, [
                rng.lognormal(12, 0.5), rng.lognormal(4, 0.5),
                rng.lognormal(10, 0.3), rng.uniform(1, 10),
                rng.uniform(0.5, 1.5), rng.poisson(3) + 1,
                rng.uniform(0.9, 1.0), rng.uniform(0, 1),
            ]))

    return _make_scenario(
        "Network Traffic (Security)", "Detect intrusions and data exfiltration",
        features, normal, anomaly,
    )


def scenario_timeseries():
    """Scenario 5: Time-series with sudden regime changes."""
    features = [f"t_{i}" for i in range(10)]  # 10-point windows

    def normal(rng):
        base = rng.normal(100, 5)
        trend = rng.uniform(-0.5, 0.5)
        noise = rng.normal(0, 2, 10)
        vals = base + trend * np.arange(10) + noise
        return dict(zip(features, vals.tolist()))

    def anomaly(rng):
        kind = rng.choice(["spike", "dropout", "level_shift", "oscillation"])
        base = rng.normal(100, 5)
        vals = np.full(10, base) + rng.normal(0, 2, 10)
        if kind == "spike":
            pos = rng.randint(2, 8)
            vals[pos] = base + rng.choice([-1, 1]) * rng.uniform(30, 60)
        elif kind == "dropout":
            vals[3:7] = rng.uniform(-5, 5, 4)
        elif kind == "level_shift":
            vals[5:] += rng.uniform(25, 50)
        else:
            vals = base + 20 * np.sin(np.linspace(0, 6 * np.pi, 10))
        return dict(zip(features, vals.tolist()))

    return _make_scenario(
        "Time-Series (Monitoring)", "Detect sudden changes in time-series windows",
        features, normal, anomaly,
    )


def scenario_sparse():
    """Scenario 6: High-dimensional sparse data (like log features)."""
    n_feat = 20
    features = [f"feat_{i}" for i in range(n_feat)]

    def normal(rng):
        vals = np.zeros(n_feat)
        active = rng.choice(n_feat, size=rng.randint(3, 6), replace=False)
        for a in active:
            vals[a] = rng.exponential(2)
        return dict(zip(features, vals.tolist()))

    def anomaly(rng):
        vals = np.zeros(n_feat)
        # Activate unusual features (indices 12-19 are rare in normal)
        active = rng.choice(range(12, 20), size=rng.randint(3, 7), replace=False)
        for a in active:
            vals[a] = rng.exponential(5)
        # Also some normal features
        n_normal = rng.randint(0, 3)
        if n_normal > 0:
            extra = rng.choice(range(0, 12), size=n_normal, replace=False)
            for a in extra:
                vals[a] = rng.exponential(2)
        return dict(zip(features, vals.tolist()))

    return _make_scenario(
        "Sparse Features (Logs)", "Detect unusual feature activation patterns",
        features, normal, anomaly,
    )


# ═════════════════════════════════════════════════════════════════════════
# Method runners
# ═════════════════════════════════════════════════════════════════════════

def _dicts_to_matrix(dicts: List[Dict], features: List[str]) -> np.ndarray:
    """Convert list of dicts to numpy matrix."""
    return np.array([[d.get(f, 0) for f in features] for d in dicts])


def run_sklearn_method(method_name: str, train_dicts: list, test_dicts: list,
                       features: list) -> Tuple[List[int], float]:
    """Run an sklearn anomaly detector. Returns (predictions, latency_ms)."""
    X_train = _dicts_to_matrix(train_dicts, features)
    X_test = _dicts_to_matrix(test_dicts, features)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    t0 = time.perf_counter()

    if method_name == "IsolationForest":
        clf = IsolationForest(contamination=0.3, random_state=42, n_estimators=200)
        clf.fit(X_train_s)
        raw = clf.predict(X_test_s)  # -1=anomaly, 1=normal
        preds = [1 if r == -1 else 0 for r in raw]
        scores = -clf.score_samples(X_test_s)  # higher = more anomalous
    elif method_name == "LOF":
        clf = LocalOutlierFactor(novelty=True, contamination=0.3, n_neighbors=min(10, len(X_train_s)-1))
        clf.fit(X_train_s)
        raw = clf.predict(X_test_s)
        preds = [1 if r == -1 else 0 for r in raw]
        scores = -clf.score_samples(X_test_s)
    elif method_name == "OneClassSVM":
        clf = OneClassSVM(kernel="rbf", gamma="auto", nu=0.3)
        clf.fit(X_train_s)
        raw = clf.predict(X_test_s)
        preds = [1 if r == -1 else 0 for r in raw]
        scores = -clf.score_samples(X_test_s)
    else:
        raise ValueError(f"Unknown method: {method_name}")

    latency = (time.perf_counter() - t0) * 1000

    return preds, scores, latency


def run_waveguard(wg: WaveGuard, train_dicts: list, test_dicts: list,
                  sensitivity: float = 1.0) -> Tuple[List[int], float]:
    """Run WaveGuard via the live API. Returns (predictions, scores, latency_ms)."""
    t0 = time.perf_counter()
    result = wg.scan(training=train_dicts, test=test_dicts, sensitivity=sensitivity)
    latency = (time.perf_counter() - t0) * 1000

    preds = [1 if r.is_anomaly else 0 for r in result.results]
    # Use confidence as score (higher = more anomalous)
    scores = [r.confidence for r in result.results]

    return preds, scores, latency


# ═════════════════════════════════════════════════════════════════════════
# Evaluation
# ═════════════════════════════════════════════════════════════════════════

def evaluate(labels: List[int], preds: List[int], scores: List[float]) -> Dict[str, float]:
    """Compute metrics."""
    labels_arr = np.array(labels)
    preds_arr = np.array(preds)
    scores_arr = np.array(scores)

    prec = precision_score(labels_arr, preds_arr, zero_division=0)
    rec  = recall_score(labels_arr, preds_arr, zero_division=0)
    f1   = f1_score(labels_arr, preds_arr, zero_division=0)

    try:
        auc = roc_auc_score(labels_arr, scores_arr)
    except ValueError:
        auc = 0.0

    tn, fp, fn, tp = confusion_matrix(labels_arr, preds_arr, labels=[0, 1]).ravel()

    return {
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "auc_roc": round(auc, 4),
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
    }


# ═════════════════════════════════════════════════════════════════════════
# Main benchmark
# ═════════════════════════════════════════════════════════════════════════

def run_benchmark():
    print("=" * 78)
    print("  WaveGuard vs Scikit-learn: Anomaly Detection Benchmark")
    print("=" * 78)
    print()

    # All scenarios
    scenarios = [
        scenario_server_metrics(),
        scenario_fraud(),
        scenario_iot(),
        scenario_network(),
        scenario_timeseries(),
        scenario_sparse(),
    ]

    methods = ["WaveGuard", "IsolationForest", "LOF", "OneClassSVM"]
    # WaveGuard sensitivity: higher = more aggressive anomaly flagging
    wg_sensitivity = 1.5

    wg = WaveGuard()  # free tier, no API key

    print(f"  WaveGuard sensitivity: {wg_sensitivity}")
    print(f"  API: {wg.base_url}")
    print()

    all_results = {}
    summary_data = []

    for sc in scenarios:
        print(f"\n{'─' * 78}")
        print(f"  Scenario: {sc['name']}")
        print(f"  {sc['description']}")
        print(f"  Train: {sc['n_train']}  |  Test normal: {sc['n_test_normal']}  |  Test anomaly: {sc['n_test_anomaly']}")
        print(f"  Features: {len(sc['feature_names'])}  |  Anomaly rate: {sc['n_test_anomaly']}/{sc['n_test_normal']+sc['n_test_anomaly']} = {sc['n_test_anomaly']/(sc['n_test_normal']+sc['n_test_anomaly']):.0%}")
        print(f"{'─' * 78}")
        print(f"  {'Method':<18} {'Prec':>6} {'Recall':>7} {'F1':>6} {'AUC':>7} {'TP':>4} {'FP':>4} {'FN':>4} {'TN':>4} {'Latency':>10}")
        print(f"  {'─'*18} {'─'*6} {'─'*7} {'─'*6} {'─'*7} {'─'*4} {'─'*4} {'─'*4} {'─'*4} {'─'*10}")

        sc_results = {}

        for method in methods:
            try:
                if method == "WaveGuard":
                    preds, scores, latency = run_waveguard(wg, sc["training"], sc["test"],
                                                           sensitivity=wg_sensitivity)
                else:
                    preds, scores, latency = run_sklearn_method(
                        method, sc["training"], sc["test"], sc["feature_names"]
                    )

                metrics = evaluate(sc["labels"], preds, scores)
                metrics["latency_ms"] = round(latency, 1)
                sc_results[method] = metrics

                winner_marker = ""
                print(f"  {method:<18} {metrics['precision']:>6.2f} {metrics['recall']:>7.2f} "
                      f"{metrics['f1']:>6.2f} {metrics['auc_roc']:>7.3f} "
                      f"{metrics['tp']:>4} {metrics['fp']:>4} {metrics['fn']:>4} {metrics['tn']:>4} "
                      f"{metrics['latency_ms']:>8.0f}ms")

            except Exception as e:
                print(f"  {method:<18} ERROR: {e}")
                sc_results[method] = {"error": str(e)}

        all_results[sc["name"]] = sc_results

        # Determine per-scenario winner (by F1)
        best_f1 = -1
        best_method = ""
        for m, r in sc_results.items():
            if "f1" in r and r["f1"] > best_f1:
                best_f1 = r["f1"]
                best_method = m
        if best_method:
            print(f"  → Winner (F1): {best_method} ({best_f1:.2f})")

        summary_data.append({
            "scenario": sc["name"],
            "results": sc_results,
            "winner_f1": best_method,
        })

    # ── Summary table ─────────────────────────────────────────────────
    print(f"\n\n{'=' * 78}")
    print("  SUMMARY: F1 Scores Across All Scenarios")
    print(f"{'=' * 78}")
    print(f"  {'Scenario':<30}", end="")
    for m in methods:
        print(f" {m:>15}", end="")
    print(f" {'Winner':>15}")
    print(f"  {'─'*30}", end="")
    for _ in methods:
        print(f" {'─'*15}", end="")
    print(f" {'─'*15}")

    method_wins = {m: 0 for m in methods}
    method_f1_totals = {m: [] for m in methods}

    for sd in summary_data:
        sc_name = sd["scenario"][:28]
        print(f"  {sc_name:<30}", end="")
        for m in methods:
            r = sd["results"].get(m, {})
            f1 = r.get("f1", 0)
            method_f1_totals[m].append(f1)
            marker = " ★" if m == sd["winner_f1"] else ""
            print(f" {f1:>13.2f}{marker}" if f1 > 0 else f" {'ERR':>15}", end="")
        print(f" {sd['winner_f1']:>15}")
        method_wins[sd["winner_f1"]] += 1

    print(f"\n  {'AVERAGE':<30}", end="")
    for m in methods:
        avg = np.mean(method_f1_totals[m]) if method_f1_totals[m] else 0
        print(f" {avg:>15.3f}", end="")
    print()
    print(f"  {'WINS':<30}", end="")
    for m in methods:
        print(f" {method_wins.get(m, 0):>15}", end="")
    print()

    # ── Save results ──────────────────────────────────────────────────
    out_dir = Path(__file__).resolve().parent
    results_file = out_dir / "benchmark_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "methods": methods,
            "scenarios": summary_data,
            "method_wins": method_wins,
            "method_avg_f1": {m: round(np.mean(method_f1_totals[m]), 4) for m in methods},
        }, f, indent=2, default=str)
    print(f"\n  Results saved to: {results_file}")
    print()

    return all_results, summary_data


if __name__ == "__main__":
    run_benchmark()

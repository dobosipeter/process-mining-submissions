"""
Process Mining Analysis — BPI Challenge 2020: Throughput Comparison.

Compares the travel declaration process for domestic vs. international trips
at Eindhoven University of Technology (TU/e).

Datasets:
  - DomesticDeclarations.xes.gz    (10,500 cases, 56,437 events)
  - InternationalDeclarations.xes.gz (6,449 cases, 72,151 events)
Source: https://data.4tu.nl/collections/BPI_Challenge_2020/5065541/1
"""

import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pm4py

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"

DOMESTIC_PATH = DATA_DIR / "DomesticDeclarations.xes.gz"
INTERNATIONAL_PATH = DATA_DIR / "InternationalDeclarations.xes.gz"

_start = time.time()


def log(msg: str) -> None:
    """Print a timestamped progress message to stdout."""
    elapsed = time.time() - _start
    print(f"[{elapsed:6.1f}s] {msg}", flush=True)


def output_exists(name: str) -> bool:
    """Return True and log a skip message if the output file already exists."""
    path = OUTPUT_DIR / name
    if path.exists() and path.stat().st_size > 0:
        log(f"SKIP (exists): {name}")
        return True
    return False


# Loading

def load_log(path: Path, label: str) -> pd.DataFrame:
    """Load an XES event log and format it for pm4py."""
    log(f"Loading {label}...")
    data = pm4py.read_xes(str(path))
    data = pm4py.format_dataframe(
        data,
        case_id="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    log(f"  {len(data)} events, {data['case:concept:name'].nunique()} cases, "
        f"{data['concept:name'].nunique()} activities")
    return data


# Exploratory analysis

def print_statistics(data: pd.DataFrame, label: str) -> dict:
    """Print and return basic log statistics (events, cases, activities, timespan)."""
    log(f"Statistics for {label}:")
    stats = {
        "events": len(data),
        "cases": data["case:concept:name"].nunique(),
        "activities": data["concept:name"].nunique(),
        "timespan_start": data["time:timestamp"].min(),
        "timespan_end": data["time:timestamp"].max(),
    }
    for k, v in stats.items():
        print(f"       {k}: {v}", flush=True)
    return stats


def plot_activity_frequencies(data: pd.DataFrame, label: str, filename: str) -> None:
    """Generate a horizontal bar chart of activity frequencies."""
    if output_exists(filename):
        return
    log(f"Plotting activity frequencies ({label})...")
    counts = data["concept:name"].value_counts()
    fig, ax = plt.subplots(figsize=(12, max(6, len(counts) * 0.35)))
    counts.plot(kind="barh", ax=ax)
    ax.set_xlabel("Frequency")
    ax.set_title(f"Activity Frequencies — {label}")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close(fig)
    log(f"Saved: {filename}")


def plot_case_durations(data: pd.DataFrame, label: str, filename: str) -> dict:
    """Compute case duration statistics and plot the distribution histogram."""
    log(f"Case durations ({label})...")
    durations = pm4py.get_all_case_durations(data)
    days = [d / 86400 for d in durations]
    s = pd.Series(days)
    stats = {"mean": s.mean(), "median": s.median(), "min": s.min(), "max": s.max()}
    log(f"  Mean: {stats['mean']:.1f} d, Median: {stats['median']:.1f} d, "
        f"Min: {stats['min']:.1f} d, Max: {stats['max']:.1f} d")

    if not output_exists(filename):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(days, bins=60, edgecolor="black", alpha=0.7)
        ax.set_xlabel("Case Duration (days)")
        ax.set_ylabel("Number of Cases")
        ax.set_title(f"Case Duration Distribution — {label}")
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / filename, dpi=150)
        plt.close(fig)
        log(f"Saved: {filename}")
    return stats


def plot_variants(data: pd.DataFrame, label: str, filename: str) -> None:
    """Compute process variants and plot the top 15 by frequency."""
    if output_exists(filename):
        return
    log(f"Variants ({label})...")
    variants = pm4py.get_variants(data)
    vc = sorted(variants.values(), reverse=True)
    top_n = 15
    log(f"  Total variants: {len(variants)}, "
        f"top 5 cover {sum(vc[:5]) / sum(vc) * 100:.1f}%")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(min(top_n, len(vc))), vc[:top_n], edgecolor="black", alpha=0.7)
    ax.set_xlabel("Variant Rank")
    ax.set_ylabel("Number of Cases")
    ax.set_title(f"Top {top_n} Process Variants — {label} (of {len(variants)} total)")
    ax.set_xticks(range(min(top_n, len(vc))))
    ax.set_xticklabels(range(1, min(top_n, len(vc)) + 1))
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close(fig)
    log(f"Saved: {filename}")


# Throughput comparison

def plot_throughput_comparison(dom_data: pd.DataFrame, intl_data: pd.DataFrame) -> None:
    """Plot overlapping histograms of case durations for both declaration types."""
    filename = "throughput_comparison.png"
    if output_exists(filename):
        return
    log("Plotting throughput comparison...")
    dom_dur = [d / 86400 for d in pm4py.get_all_case_durations(dom_data)]
    intl_dur = [d / 86400 for d in pm4py.get_all_case_durations(intl_data)]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(dom_dur, bins=60, alpha=0.6, label="Domestic", edgecolor="black")
    ax.hist(intl_dur, bins=60, alpha=0.6, label="International", edgecolor="black")
    ax.set_xlabel("Case Duration (days)")
    ax.set_ylabel("Number of Cases")
    ax.set_title("Case Duration: Domestic vs. International Declarations")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close(fig)
    log(f"Saved: {filename}")


def plot_throughput_boxplot(dom_data: pd.DataFrame, intl_data: pd.DataFrame) -> None:
    """Plot side-by-side boxplots of case durations (outliers hidden)."""
    filename = "throughput_boxplot.png"
    if output_exists(filename):
        return
    log("Plotting throughput boxplot...")
    dom_dur = [d / 86400 for d in pm4py.get_all_case_durations(dom_data)]
    intl_dur = [d / 86400 for d in pm4py.get_all_case_durations(intl_data)]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot([dom_dur, intl_dur], tick_labels=["Domestic", "International"],
               showfliers=False)
    ax.set_ylabel("Case Duration (days)")
    ax.set_title("Case Duration Comparison (outliers hidden)")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close(fig)
    log(f"Saved: {filename}")


def decompose_international_duration(intl_data: pd.DataFrame) -> pd.DataFrame:
    """Decompose international case durations into pre-trip, trip, and post-trip phases."""
    log("Decomposing international durations...")
    starts = intl_data[intl_data["concept:name"] == "Start trip"][
        ["case:concept:name", "time:timestamp"]
    ].rename(columns={"time:timestamp": "trip_start"})
    ends = intl_data[intl_data["concept:name"] == "End trip"][
        ["case:concept:name", "time:timestamp"]
    ].rename(columns={"time:timestamp": "trip_end"})
    case_first = intl_data.groupby("case:concept:name")["time:timestamp"].min().rename("case_start")
    case_last = intl_data.groupby("case:concept:name")["time:timestamp"].max().rename("case_end")

    trip = starts.merge(ends, on="case:concept:name").set_index("case:concept:name")
    trip = trip.join(case_first).join(case_last)
    trip["pre_trip"] = (trip["trip_start"] - trip["case_start"]).dt.total_seconds() / 86400
    trip["trip_dur"] = (trip["trip_end"] - trip["trip_start"]).dt.total_seconds() / 86400
    trip["post_trip"] = (trip["case_end"] - trip["trip_end"]).dt.total_seconds() / 86400

    for col, label in [("pre_trip", "Pre-trip admin"), ("trip_dur", "Trip duration"), ("post_trip", "Post-trip admin")]:
        s = trip[col]
        log(f"  {label}: mean={s.mean():.1f}d, median={s.median():.1f}d")

    return trip


def plot_decomposition(trip: pd.DataFrame) -> None:
    """Plot a stacked bar chart of the international duration decomposition."""
    filename = "international_decomposition.png"
    if output_exists(filename):
        return
    log("Plotting decomposition...")
    phases = ["Pre-trip Admin", "Trip Duration", "Post-trip Admin"]
    means = [trip["pre_trip"].mean(), trip["trip_dur"].mean(), trip["post_trip"].mean()]
    medians = [trip["pre_trip"].median(), trip["trip_dur"].median(), trip["post_trip"].median()]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    fig, ax = plt.subplots(figsize=(8, 5))
    for col_idx, (values, x_pos) in enumerate([(means, 0), (medians, 1)]):
        bottom = 0
        for i, phase in enumerate(phases):
            bar_label = phase if col_idx == 0 else None
            ax.bar(x_pos, values[i], bottom=bottom, color=colors[i],
                   edgecolor="black", width=0.5, label=bar_label)
            ax.text(x_pos, bottom + values[i] / 2, f"{values[i]:.1f}d",
                    ha="center", va="center", fontsize=10, fontweight="bold")
            bottom += values[i]

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Mean", "Median"])
    ax.set_ylabel("Duration (days)")
    ax.set_title("International Declaration Duration Decomposition")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close(fig)
    log(f"Saved: {filename}")


def plot_admin_only_comparison(dom_data: pd.DataFrame, trip: pd.DataFrame) -> None:
    """Compare domestic total duration against international admin-only duration."""
    filename = "admin_only_comparison.png"
    if output_exists(filename):
        return
    log("Plotting admin-only comparison...")
    dom_dur = [d / 86400 for d in pm4py.get_all_case_durations(dom_data)]
    intl_admin = (trip["pre_trip"] + trip["post_trip"]).values

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot([dom_dur, list(intl_admin)],
               tick_labels=["Domestic\n(total)", "International\n(admin only)"],
               showfliers=False)
    ax.set_ylabel("Duration (days)")
    ax.set_title("Domestic Total vs. International Admin-Only Duration")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close(fig)
    log(f"Saved: {filename}")


# Process discovery

def discover_dfg(data: pd.DataFrame, label: str, freq_file: str, perf_file: str) -> None:
    """Discover and save frequency- and performance-annotated DFGs."""
    if not output_exists(freq_file):
        log(f"DFG frequency ({label})...")
        dfg, sa, ea = pm4py.discover_dfg(data)
        pm4py.save_vis_dfg(dfg, sa, ea, str(OUTPUT_DIR / freq_file))
        log(f"Saved: {freq_file}")

    if not output_exists(perf_file):
        log(f"DFG performance ({label})...")
        dfg_p, sa_p, ea_p = pm4py.discover_performance_dfg(data)
        pm4py.save_vis_performance_dfg(dfg_p, sa_p, ea_p, str(OUTPUT_DIR / perf_file))
        log(f"Saved: {perf_file}")


def discover_models(data: pd.DataFrame, label: str, prefix: str) -> dict:
    """Run Alpha, Heuristic, and Inductive miners; save Petri nets, process tree, BPMN, and model files."""
    models = {}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"Alpha Miner ({label})...")
    net, im, fm = pm4py.discover_petri_net_alpha(data)
    models["Alpha Miner"] = (net, im, fm)
    pm4py.write_pnml(net, im, fm, str(MODELS_DIR / f"{prefix}_alpha.pnml"))
    fname = f"{prefix}_alpha_petri_net.png"
    if not output_exists(fname):
        pm4py.save_vis_petri_net(net, im, fm, str(OUTPUT_DIR / fname))
        log(f"Saved: {fname}")

    log(f"Heuristic Miner ({label})...")
    net, im, fm = pm4py.discover_petri_net_heuristics(data)
    models["Heuristic Miner"] = (net, im, fm)
    pm4py.write_pnml(net, im, fm, str(MODELS_DIR / f"{prefix}_heuristic.pnml"))
    fname = f"{prefix}_heuristic_petri_net.png"
    if not output_exists(fname):
        pm4py.save_vis_petri_net(net, im, fm, str(OUTPUT_DIR / fname))
        log(f"Saved: {fname}")

    log(f"Inductive Miner ({label})...")
    net, im, fm = pm4py.discover_petri_net_inductive(data)
    models["Inductive Miner"] = (net, im, fm)
    pm4py.write_pnml(net, im, fm, str(MODELS_DIR / f"{prefix}_inductive.pnml"))
    fname = f"{prefix}_inductive_petri_net.png"
    if not output_exists(fname):
        pm4py.save_vis_petri_net(net, im, fm, str(OUTPUT_DIR / fname))
        log(f"Saved: {fname}")

    tree_fname = f"{prefix}_inductive_process_tree.png"
    if not output_exists(tree_fname):
        log(f"Process tree ({label})...")
        tree = pm4py.discover_process_tree_inductive(data)
        pm4py.save_vis_process_tree(tree, str(OUTPUT_DIR / tree_fname))
        log(f"Saved: {tree_fname}")

    bpmn_fname = f"{prefix}_inductive_bpmn.png"
    if not output_exists(bpmn_fname):
        log(f"BPMN model ({label})...")
        bpmn = pm4py.discover_bpmn_inductive(data)
        pm4py.write_bpmn(bpmn, str(MODELS_DIR / f"{prefix}_inductive.bpmn"))
        pm4py.save_vis_bpmn(bpmn, str(OUTPUT_DIR / bpmn_fname))
        log(f"Saved: {bpmn_fname}")

    return models


# Conformance checking

def conformance_checking(data: pd.DataFrame, models: dict, label: str) -> dict:
    """Compute fitness, precision, and generalization for each model via token-based replay."""
    log(f"Conformance checking ({label})...")
    results = {}
    for name, (net, im, fm) in models.items():
        log(f"  {name}...")
        fitness = pm4py.fitness_token_based_replay(data, net, im, fm)
        precision = pm4py.precision_token_based_replay(data, net, im, fm)
        generalization = pm4py.generalization_tbr(data, net, im, fm)

        f_val = fitness.get("log_fitness", fitness.get("average_trace_fitness", 0))
        log(f"    Fitness: {f_val:.4f}, Precision: {precision:.4f}, "
            f"Generalization: {generalization:.4f}")

        results[name] = {
            "fitness": f_val,
            "precision": precision,
            "generalization": generalization,
        }
    return results


def plot_conformance(results: dict, label: str, filename: str) -> None:
    """Plot a grouped bar chart comparing fitness, precision, and generalization."""
    if output_exists(filename):
        return
    log(f"Plotting conformance ({label})...")
    names = list(results.keys())
    fitness = [results[n]["fitness"] for n in names]
    precision = [results[n]["precision"] for n in names]
    gen = [results[n]["generalization"] for n in names]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(names))
    w = 0.25
    ax.bar([i - w for i in x], fitness, w, label="Fitness")
    ax.bar(x, precision, w, label="Precision")
    ax.bar([i + w for i in x], gen, w, label="Generalization")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Score")
    ax.set_title(f"Model Quality Comparison — {label}")
    ax.set_ylim(0, 1.1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close(fig)
    log(f"Saved: {filename}")


# Main

def main():
    """Run the full analysis pipeline."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dom = load_log(DOMESTIC_PATH, "Domestic")
    intl = load_log(INTERNATIONAL_PATH, "International")

    print_statistics(dom, "Domestic")
    print_statistics(intl, "International")

    plot_activity_frequencies(dom, "Domestic", "domestic_activity_frequencies.png")
    plot_activity_frequencies(intl, "International", "international_activity_frequencies.png")

    dom_dur = plot_case_durations(dom, "Domestic", "domestic_case_durations.png")
    intl_dur = plot_case_durations(intl, "International", "international_case_durations.png")

    plot_variants(dom, "Domestic", "domestic_variants.png")
    plot_variants(intl, "International", "international_variants.png")

    plot_throughput_comparison(dom, intl)
    plot_throughput_boxplot(dom, intl)

    trip = decompose_international_duration(intl)
    plot_decomposition(trip)
    plot_admin_only_comparison(dom, trip)

    discover_dfg(dom, "Domestic", "domestic_dfg_frequency.png", "domestic_dfg_performance.png")
    discover_dfg(intl, "International", "international_dfg_frequency.png", "international_dfg_performance.png")

    dom_models = discover_models(dom, "Domestic", "domestic")
    intl_models = discover_models(intl, "International", "international")

    dom_conf = conformance_checking(dom, dom_models, "Domestic")
    intl_conf = conformance_checking(intl, intl_models, "International")

    plot_conformance(dom_conf, "Domestic", "domestic_conformance.png")
    plot_conformance(intl_conf, "International", "international_conformance.png")

    log("=== Analysis complete ===")


if __name__ == "__main__":
    main()

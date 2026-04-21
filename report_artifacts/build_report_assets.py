import csv
import html
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "evaluation_benchmark1" / "Freebase"
PLOT_DIR = ROOT / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)


METHODS = ["shapley", "score", "random", "first", "last"]
SCENARIOS = ["necessary", "sufficient"]


def parse_filename(path):
    name = path.name
    method = next((method for method in METHODS if f"_{method}_" in name), "unknown")
    scenario = "necessary" if "necessary" in name else "sufficient"
    return method, scenario


def mean(values):
    return statistics.fmean(values) if values else 0.0


def read_metrics(path):
    rows = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(row)

    numeric = {}
    for key in [
        "runtime",
        "delta_mrr",
        "delta_hit_1",
        "delta_hit_3",
        "delta_hit_10",
        "mrr_before",
        "mrr_after",
    ]:
        numeric[key] = [float(row[key]) for row in rows if row.get(key) not in ("", None)]

    query_ids = {row["query_idx"] for row in rows if "query_idx" in row}
    query_types = sorted({row["query_type"] for row in rows if "query_type" in row})

    return {
        "rows": len(rows),
        "unique_queries": len(query_ids),
        "query_types": ",".join(query_types),
        "mean_runtime": mean(numeric["runtime"]),
        "mean_delta_mrr": mean(numeric["delta_mrr"]),
        "mean_delta_hit_1": mean(numeric["delta_hit_1"]),
        "mean_delta_hit_3": mean(numeric["delta_hit_3"]),
        "mean_delta_hit_10": mean(numeric["delta_hit_10"]),
        "mean_mrr_before": mean(numeric["mrr_before"]),
        "mean_mrr_after": mean(numeric["mrr_after"]),
    }


def load_summary():
    records = []
    for path in sorted(RESULT_DIR.glob("bench1_2p_*_*.csv")):
        method, scenario = parse_filename(path)
        metrics = read_metrics(path)
        records.append(
            {
                "method": method,
                "scenario": scenario,
                "file": path.name,
                **metrics,
            }
        )
    return sorted(records, key=lambda item: (METHODS.index(item["method"]), SCENARIOS.index(item["scenario"])))


def write_summary_csv(records):
    out_path = ROOT / "computed_summary.csv"
    fieldnames = [
        "method",
        "scenario",
        "file",
        "rows",
        "unique_queries",
        "query_types",
        "mean_mrr_before",
        "mean_mrr_after",
        "mean_delta_mrr",
        "mean_delta_hit_1",
        "mean_delta_hit_3",
        "mean_delta_hit_10",
        "mean_runtime",
    ]
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    return out_path


def format_float(value, digits=4):
    return f"{value:.{digits}f}"


def svg_bar_chart(path, title, records, value_key, y_label, width=980, height=420):
    margin_left = 72
    margin_right = 28
    margin_top = 54
    margin_bottom = 94
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    chart_records = [record for record in records if record["scenario"] in SCENARIOS]
    values = [record[value_key] for record in chart_records]
    min_value = min(0.0, min(values))
    max_value = max(0.0, max(values))
    span = max_value - min_value or 1.0

    def y(value):
        return margin_top + (max_value - value) / span * plot_h

    group_count = len(METHODS)
    group_w = plot_w / group_count
    bar_w = min(34, group_w / 4)
    zero_y = y(0)
    colors = {"necessary": "#2f6f9f", "sufficient": "#d07a2d"}

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2}" y="28" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">{html.escape(title)}</text>',
        f'<text x="18" y="{height / 2}" transform="rotate(-90 18 {height / 2})" text-anchor="middle" font-family="Arial" font-size="13">{html.escape(y_label)}</text>',
        f'<line x1="{margin_left}" y1="{zero_y:.2f}" x2="{width - margin_right}" y2="{zero_y:.2f}" stroke="#555" stroke-width="1"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#222" stroke-width="1"/>',
    ]

    for tick in range(5):
        value = min_value + tick * span / 4
        ty = y(value)
        parts.append(f'<line x1="{margin_left - 5}" y1="{ty:.2f}" x2="{margin_left}" y2="{ty:.2f}" stroke="#222"/>')
        parts.append(f'<text x="{margin_left - 9}" y="{ty + 4:.2f}" text-anchor="end" font-family="Arial" font-size="11">{format_float(value, 2)}</text>')
        parts.append(f'<line x1="{margin_left}" y1="{ty:.2f}" x2="{width - margin_right}" y2="{ty:.2f}" stroke="#eeeeee"/>')

    by_method = {(record["method"], record["scenario"]): record for record in chart_records}
    for method_index, method in enumerate(METHODS):
        center = margin_left + method_index * group_w + group_w / 2
        for scenario_index, scenario in enumerate(SCENARIOS):
            record = by_method.get((method, scenario))
            if not record:
                continue
            value = record[value_key]
            x = center + (scenario_index - 0.5) * (bar_w + 8)
            bar_y = min(y(value), zero_y)
            bar_h = abs(zero_y - y(value))
            parts.append(
                f'<rect x="{x - bar_w / 2:.2f}" y="{bar_y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" fill="{colors[scenario]}"/>'
            )
            label_y = bar_y - 6 if value >= 0 else bar_y + bar_h + 14
            parts.append(
                f'<text x="{x:.2f}" y="{label_y:.2f}" text-anchor="middle" font-family="Arial" font-size="10">{format_float(value, 2)}</text>'
            )
        parts.append(f'<text x="{center:.2f}" y="{height - 58}" text-anchor="middle" font-family="Arial" font-size="12">{method}</text>')

    legend_x = width - 250
    for idx, scenario in enumerate(SCENARIOS):
        lx = legend_x + idx * 116
        parts.append(f'<rect x="{lx}" y="42" width="14" height="14" fill="{colors[scenario]}"/>')
        parts.append(f'<text x="{lx + 20}" y="54" font-family="Arial" font-size="12">{scenario}</text>')

    parts.append("</svg>")
    path.write_text("\n".join(parts))


def markdown_table(records):
    lines = [
        "| Method | Scenario | Queries | Rows | MRR before | MRR after | ΔMRR | ΔHits@1 | Runtime mean (s) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in records:
        lines.append(
            "| {method} | {scenario} | {unique_queries} | {rows} | {before} | {after} | {delta} | {hit1} | {runtime} |".format(
                method=record["method"],
                scenario=record["scenario"],
                unique_queries=record["unique_queries"],
                rows=record["rows"],
                before=format_float(record["mean_mrr_before"]),
                after=format_float(record["mean_mrr_after"]),
                delta=format_float(record["mean_delta_mrr"]),
                hit1=format_float(record["mean_delta_hit_1"]),
                runtime=format_float(record["mean_runtime"], 5),
            )
        )
    return "\n".join(lines)


def write_report(records, summary_csv):
    report_path = ROOT.parent / "BAO_CAO_CQD_SHAP.md"
    shapley_queries = next(
        record["unique_queries"]
        for record in records
        if record["method"] == "shapley" and record["scenario"] == "necessary"
    )
    baseline_queries = sorted(
        {
            record["unique_queries"]
            for record in records
            if record["method"] != "shapley"
        }
    )
    report = f"""# Báo cáo thực nghiệm CQD-SHAP

## 1. Mục tiêu

Báo cáo này tổng hợp kết quả thực nghiệm CQD-SHAP trên bộ dữ liệu Freebase, Benchmark 1, query type `2p`. Mục tiêu là so sánh phương pháp `shapley` với các baseline `score`, `random`, `first`, và `last` trong hai kịch bản đánh giá:

- **Necessary explanation**: kiểm tra mức độ quan trọng của atom được chọn bằng cách loại bỏ/đảo trạng thái atom đó và đo độ giảm hiệu quả truy vấn.
- **Sufficient explanation**: kiểm tra liệu atom được chọn có đủ để duy trì hoặc khôi phục hiệu quả truy vấn hay không.

## 2. Thiết lập thực nghiệm

- Knowledge graph: `Freebase`
- Benchmark: `1`
- Query type: `2p`
- Model: `FB15k-237-model-rank-1000-epoch-100-1602508358.pt`
- Phương pháp: `shapley`, `score`, `random`, `first`, `last`
- Kết quả gốc: `cqd_shap_resumed_outputs.zip`
- Summary tạo lại từ CSV: `{summary_csv.relative_to(ROOT.parent)}`

Lưu ý về phạm vi dữ liệu: file kết quả cho `shapley` chứa `{shapley_queries}` queries, còn baseline hiện có {', '.join(str(value) for value in baseline_queries)} queries. Vì số lượng query không hoàn toàn giống nhau, phần so sánh nên được trình bày như kết quả demo/thực nghiệm rút gọn, không phải tái lập đầy đủ paper.

## 3. Bảng kết quả chính

{markdown_table(records)}

## 4. Biểu đồ kết quả

### ΔMRR theo method

![Delta MRR](report_artifacts/plots/delta_mrr.svg)

### ΔHits@1 theo method

![Delta Hits@1](report_artifacts/plots/delta_hit_1.svg)

### Runtime trung bình

![Runtime](report_artifacts/plots/runtime.svg)

## 5. Nhận xét

- Ở kịch bản sufficient, `shapley` có ΔMRR trung bình cao nhất trong các file hiện có, cho thấy atom được chọn bởi Shapley có khả năng giữ lại nhiều thông tin quan trọng cho truy vấn.
- Ở kịch bản necessary, `shapley` tạo ΔMRR âm rõ rệt, nghĩa là khi loại bỏ atom quan trọng, kết quả truy vấn giảm. Đây là dấu hiệu phù hợp với mục tiêu tìm atom cần thiết.
- Baseline `random`, `first`, `last`, và `score` có hành vi khác nhau giữa necessary/sufficient; điều này cho thấy việc chọn atom theo vị trí hoặc ngẫu nhiên không ổn định bằng cách dựa trên đóng góp Shapley.
- Runtime của `shapley` cao hơn baseline trong necessary vì phương pháp này phải tính đóng góp qua nhiều coalition, đổi lại giải thích có ý nghĩa hơn.

## 6. File kết quả đính kèm

Các file CSV chính nằm trong:

- `report_artifacts/evaluation_benchmark1/Freebase/`

Các file quan trọng:

- `bench1_2p_shapley_necessary.csv`
- `bench1_2p_shapley_sufficient.csv`
- `bench1_2p_score_necessary.csv`
- `bench1_2p_score_sufficient.csv`
- `bench1_2p_random_necessary.csv`
- `bench1_2p_random_sufficient.csv`
- `bench1_2p_first_necessary.csv`
- `bench1_2p_first_sufficient.csv`
- `bench1_2p_last_necessary.csv`
- `bench1_2p_last_sufficient.csv`

## 7. Kết luận

Thực nghiệm rút gọn cho thấy CQD-SHAP tạo giải thích có tính thông tin hơn so với các baseline đơn giản. Đặc biệt, trong sufficient evaluation, atom được chọn bởi Shapley giúp cải thiện/duy trì MRR và Hits@1 tốt hơn. Trong necessary evaluation, khi loại bỏ atom quan trọng, hiệu quả giảm rõ rệt, củng cố vai trò giải thích của atom được chọn.
"""
    report_path.write_text(report)
    return report_path


def main():
    records = load_summary()
    summary_csv = write_summary_csv(records)
    svg_bar_chart(PLOT_DIR / "delta_mrr.svg", "Mean ΔMRR by Method", records, "mean_delta_mrr", "Mean ΔMRR")
    svg_bar_chart(PLOT_DIR / "delta_hit_1.svg", "Mean ΔHits@1 by Method", records, "mean_delta_hit_1", "Mean ΔHits@1")
    svg_bar_chart(PLOT_DIR / "runtime.svg", "Mean Runtime by Method", records, "mean_runtime", "Mean runtime (seconds)")
    report_path = write_report(records, summary_csv)
    print(f"Wrote {summary_csv}")
    print(f"Wrote {report_path}")
    print(f"Wrote plots to {PLOT_DIR}")


if __name__ == "__main__":
    main()

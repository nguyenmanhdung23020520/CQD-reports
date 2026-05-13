# Student Experiment Report – CQD-SHAP

Nguồn chính để viết báo cáo: `cqd.txt` (paper), `README.md`, `evaluation.py`, `requirements.txt`, các log trong `evaluation_benchmark*`, và artifact trong `report_artifacts/`.

Quy ước nguồn:

- **paper / cqd.txt**: số liệu, mô tả và nhận xét lấy từ bài báo trong `cqd.txt`.
- **student log/output**: số liệu nhóm đã chạy, lấy từ file log/CSV thật trong repo.
- Không tự bịa kết quả. Nếu một số không có trong paper hoặc log thật, báo cáo không điền số đó.

## 1. Tóm tắt bài báo từ cqd.txt

### Bài toán của paper

Theo bài báo trong `cqd.txt`, Complex Query Answering (CQA) mở rộng link prediction từ truy vấn 1-hop sang các truy vấn phức tạp cần suy luận multi-hop, conjunction, disjunction trên knowledge graph chưa hoàn chỉnh. CQD có tính diễn giải hơn neural CQA thuần túy vì có thể theo dõi intermediate results, nhưng vẫn chưa giải thích được **phần nào của query quan trọng hơn** đối với một answer cụ thể.

CQD-SHAP giải quyết bài toán giải thích ở cấp **query atom**: với một query gồm nhiều atom, phương pháp đo đóng góp của từng atom vào thứ hạng của một target answer.

### Ý tưởng CQD-SHAP

Theo paper, mỗi atom trong query có thể được thực thi theo hai cách:

- **Symbolic execution**: tra cứu trực tiếp trên observed KG, chỉ dùng fact có sẵn.
- **Neural execution**: dùng CQD/link predictor để suy luận link còn thiếu.

CQD-SHAP định nghĩa một Shapley game:

- Player: các query atoms.
- Coalition `S`: tập atom được thực thi neural; các atom còn lại thực thi symbolic.
- Value function: dựa trên thay đổi rank của target answer khi chuyển từ symbolic sang neural execution.

Shapley value của một atom thể hiện mức độ atom đó giúp cải thiện rank của answer khi dùng neural inference thay vì symbolic retrieval. Theo efficiency axiom, tổng Shapley values của các atom bằng chênh lệch rank giữa query chạy hoàn toàn symbolic và query chạy hoàn toàn neural/neurosymbolic.

### Datasets theo bài báo

Theo Table 1 trong `cqd.txt`:

| Dataset | Nodes | Relations | `G_train` | `G_valid` | `G_test` |
|---|---:|---:|---:|---:|---:|
| FB15k-237 | 14,505 | 474 | 544,230 | 579,300 | 620,232 |
| NELL995 | 63,361 | 400 | 456,852 | 716,472 | 1,005,086 |

Paper dùng 8 query types:

| Paper query type | Tên trong code/README |
|---|---|
| `2p` | `2p` |
| `2u` | `2u` |
| `2i` | `2i` |
| `3i` | `3i` |
| `3p` | `3p` |
| `2u1p` | `up` |
| `2i1p` | `ip` |
| `1p2i` | `pi` |

Theo paper: validation/test có 5,000 queries mỗi type cho FB15k-237 và 4,000 queries mỗi type cho NELL995.

### Metrics theo bài báo

Paper dùng filtered ranking và báo cáo:

- `MRR`
- `Hits@1`
- Trong Table 2: `ΔMRR` và `ΔHits@1`

Ý nghĩa chiều tốt:

- **Necessary evaluation**: lower/more negative is better, vì khi thay atom quan trọng bằng symbolic execution thì target answer phải tụt rank mạnh.
- **Sufficient evaluation**: higher/more positive is better, vì chỉ cần atom quan trọng được chạy neural thì target answer phải cải thiện rank.

### Baseline methods theo bài báo

Theo Section 5.1 trong `cqd.txt`:

| Paper method | Code method | Mô tả ngắn |
|---|---|---|
| First-level | `first` | Chọn ngẫu nhiên một atom ở first level/anchor level. |
| Last-level | `last` | Chọn ngẫu nhiên một atom ở last level/target level. |
| Random | `random` | Chọn ngẫu nhiên một atom bất kỳ. |
| Score-based | `score` | Chọn atom dựa trên link prediction scores. |
| CQD-SHAP | `shapley` | Tính Shapley value cho các atom và chọn atom có Shapley value cao nhất. |

### Kết quả chính của paper

Theo Section 5.2 và Table 2 trong `cqd.txt`, CQD-SHAP tốt hơn baseline trong hầu hết trường hợp. Paper ghi nhận:

- CQD-SHAP làm giảm MRR trong necessary scenario từ `0.642` đến `0.999` tùy dataset/query type.
- CQD-SHAP làm tăng MRR trong sufficient scenario từ `0.205` đến `0.521`.
- Ngoại lệ đáng chú ý: sufficient evaluation cho `2u1p`, CQD-SHAP rất gần top-performing method.
- Paper nhận xét: atom quan trọng nhất do CQD-SHAP tìm ra thường **necessary** để đạt rank tốt, nhưng không phải lúc nào cũng **sufficient** nếu chỉ chạy riêng atom đó theo neural execution.

CQD-SHAP results theo Table 2 trong paper:

| Dataset | Scenario | Query Type | CQD-SHAP ΔMRR | CQD-SHAP ΔHits@1 | Source |
|---|---|---|---:|---:|---|
| FB15k-237 | necessary | 2p | -0.685 | -0.752 | paper Table 2, `cqd.txt` |
| FB15k-237 | necessary | 2u | -0.999 | -1.000 | paper Table 2, `cqd.txt` |
| FB15k-237 | necessary | 2i | -0.931 | -0.971 | paper Table 2, `cqd.txt` |
| FB15k-237 | necessary | 3i | -0.945 | -0.994 | paper Table 2, `cqd.txt` |
| FB15k-237 | necessary | 3p | -0.665 | -0.730 | paper Table 2, `cqd.txt` |
| FB15k-237 | necessary | 2u1p | -0.950 | -0.961 | paper Table 2, `cqd.txt` |
| FB15k-237 | necessary | 2i1p | -0.857 | -0.896 | paper Table 2, `cqd.txt` |
| FB15k-237 | necessary | 1p2i | -0.788 | -0.842 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 2p | -0.793 | -0.845 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 2u | -0.999 | -1.000 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 2i | -0.861 | -0.928 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 3i | -0.894 | -0.973 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 3p | -0.642 | -0.709 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 2u1p | -0.982 | -0.986 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 2i1p | -0.871 | -0.914 | paper Table 2, `cqd.txt` |
| NELL995 | necessary | 1p2i | -0.752 | -0.823 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 2p | +0.318 | +0.242 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 2u | +0.348 | +0.250 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 2i | +0.429 | +0.373 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 3i | +0.499 | +0.511 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 3p | +0.274 | +0.210 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 2u1p | +0.205 | +0.137 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 2i1p | +0.227 | +0.168 | paper Table 2, `cqd.txt` |
| FB15k-237 | sufficient | 1p2i | +0.311 | +0.264 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 2p | +0.388 | +0.306 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 2u | +0.521 | +0.412 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 2i | +0.401 | +0.361 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 3i | +0.489 | +0.516 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 3p | +0.356 | +0.286 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 2u1p | +0.242 | +0.165 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 2i1p | +0.248 | +0.189 | paper Table 2, `cqd.txt` |
| NELL995 | sufficient | 1p2i | +0.284 | +0.235 | paper Table 2, `cqd.txt` |

## 2. Môi trường chạy

### Môi trường paper

Theo `cqd.txt`, tác giả chạy toàn bộ thí nghiệm trên:

| Thành phần | Giá trị theo paper |
|---|---|
| GPU | NVIDIA H100-20C, 20GB VRAM |
| RAM | 128GB |
| CPU | 16-core CPU |
| Beam search `k` | 10 |
| t-norm | product t-norm |
| t-conorm | product t-conorm |
| Model | pre-trained CQD link prediction model, không fine-tune thêm |

Theo Table 3 trong paper, runtime trung bình để tính Shapley values cho một query-answer pair:

| Dataset | 2p | 2u | 2i | 3i | 3p | 2u1p | 2i1p | 1p2i |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FB15k-237 | 41 ms | 29 ms | 30 ms | 91 ms | 306 ms | 129 ms | 149 ms | 147 ms |
| NELL995 | 100 ms | 85 ms | 81 ms | 232 ms | 474 ms | 287 ms | 327 ms | 335 ms |

### Môi trường repo hiện tại khi lập báo cáo

| Thành phần | Giá trị kiểm tra được |
|---|---|
| Runtime | WSL2 / Linux `6.6.87.2-microsoft-standard-WSL2` |
| Current shell Python | Python `3.13.12`, `/home/manhdung0507/miniconda3/bin/python` |
| Conda env active | `base` |
| Conda env có sẵn | `xcqa`, Python `3.10.20` |
| Git branch | `main` |
| Git commit | `c2769c06ab31c5eca576aedfa95edefb55ecd731` |

Package chính theo `requirements.txt`:

| Package | Version |
|---|---|
| `numpy` | `2.2.6` |
| `networkx` | `3.4.2` |
| `matplotlib` | `3.10.5` |
| `pandas` | `2.3.0` |
| `tqdm` | `4.67.1` |
| `torch` | `2.7.0` |

Không chạy lại evaluation trong lần lập báo cáo này vì workspace hiện không có `data/` và `models/`.

## 3. Kiểm tra repo, data và models

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| `evaluation.py` | Có | Script chạy explanation evaluation. |
| `requirements.txt` | Có | Danh sách package. |
| `README.md` | Có | Hướng dẫn setup, download data/model, chạy evaluation. |
| `data/` | Không có ở repo root | Chưa thấy dataset đã unzip trong workspace hiện tại. |
| `models/` | Không có ở repo root | Chưa thấy pretrained model trong workspace hiện tại. |
| `evaluation_benchmark1/` | Có | Log thật cho Benchmark 1, Freebase/NELL, 5 methods. |
| `evaluation_benchmark2/` | Có | Log thật cho Benchmark 2, Freebase/NELL, 5 methods. |
| `evaluation/` | Không có ở repo root | Default output folder chưa tồn tại. |
| `output/` | Không có ở repo root | Không thấy thư mục output riêng. |
| `result/` hoặc `results/` | Không có ở repo root | Không thấy thư mục result riêng. |
| `report_artifacts/` | Có | CSV, log rút gọn và chart SVG đã tạo trước đó. |

Artifact có sẵn dùng trong báo cáo:

| Loại | Đường dẫn |
|---|---|
| Log đầy đủ Benchmark 1 | `evaluation_benchmark1/Freebase/*.log`, `evaluation_benchmark1/NELL/*.log` |
| Log đầy đủ Benchmark 2 | `evaluation_benchmark2/Freebase/*.log`, `evaluation_benchmark2/NELL/*.log` |
| Summary CSV rút gọn | `report_artifacts/computed_summary.csv` |
| Summary CSV resumed | `report_artifacts/evaluation_summary_resumed_2p.csv` |
| CSV chi tiết 2p | `report_artifacts/evaluation_benchmark1/Freebase/bench1_2p_*_necessary.csv` |
| CSV chi tiết 2p | `report_artifacts/evaluation_benchmark1/Freebase/bench1_2p_*_sufficient.csv` |
| Chart | `report_artifacts/plots/delta_mrr.svg` |
| Chart | `report_artifacts/plots/delta_hit_1.svg` |
| Chart | `report_artifacts/plots/runtime.svg` |

## 4. Quy trình setup và chạy

Theo `README.md`:

```bash
git clone https://github.com/ds-jrg/CQD-SHAP.git
cd CQD-SHAP

conda create -n xcqa python=3.10
conda activate xcqa
pip install -r requirements.txt
```

Download dataset:

```bash
wget https://groups.uni-paderborn.de/fg-ds-jrg/projects/cqd-shap/datasets/data_v2.zip
unzip data_v2.zip
```

Download pretrained models:

```bash
wget https://groups.uni-paderborn.de/fg-ds-jrg/projects/cqd-shap/models/models.zip
unzip models.zip
```

Chạy CQD-SHAP:

```bash
python evaluation.py --kg Freebase --benchmark 2 --method shapley
```

Chạy baseline:

```bash
python evaluation.py --kg Freebase --benchmark 2 --method score
python evaluation.py --kg Freebase --benchmark 2 --method random
python evaluation.py --kg Freebase --benchmark 2 --method first
python evaluation.py --kg Freebase --benchmark 2 --method last
```

Chạy nhanh một query type:

```bash
python evaluation.py --kg Freebase --benchmark 1 --query_type 2p --method shapley
```

Default model path trong `evaluation.py`:

| KG | Model path |
|---|---|
| Freebase | `models/FB15k-237-model-rank-1000-epoch-100-1602508358.pt` |
| NELL | `models/NELL-model-rank-1000-epoch-100-1602499096.pt` |

## 5. Kết quả thực nghiệm nhóm sinh viên

### Nguồn kết quả nhóm

Repo có output/log thật. Báo cáo dùng nhóm log đầy đủ cho Freebase Benchmark 1 query type `2p`:

- `evaluation_benchmark1/Freebase/bench1_all_shapley.log`
- `evaluation_benchmark1/Freebase/bench1_all_score.log`
- `evaluation_benchmark1/Freebase/bench1_all_random.log`
- `evaluation_benchmark1/Freebase/bench1_all_first.log`
- `evaluation_benchmark1/Freebase/bench1_all_last.log`

Lưu ý khi so sánh: log nhóm hiện tại ghi metrics cho toàn bộ hard-answer cases trong query type `2p`. Trong khi đó, paper Table 2 lọc theo điều kiện riêng cho necessary/sufficient. Đặc biệt với necessary evaluation, paper chỉ xét các hard answers đã được CQD rank 1, còn log nhóm không thể hiện đúng cùng tập lọc này. Vì vậy, necessary results của nhóm **không so sánh trực tiếp 1-1** với paper.

### Bảng kết quả nhóm từ log thật

`MRR` và `Hits@1` trong bảng là giá trị `after`; phần trong ngoặc là delta `after - before`.

| Dataset | Benchmark | Query Type | Method | MRR | Hits@1 | Source |
|---|---|---|---|---|---|---|
| Freebase / FB15k-237 | 1 | 2p | shapley necessary | 0.1082 (Δ=-0.1524) | 0.0701 (Δ=-0.1113) | `evaluation_benchmark1/Freebase/bench1_all_shapley.log` |
| Freebase / FB15k-237 | 1 | 2p | shapley sufficient | 0.3328 (Δ=+0.3181) | 0.2573 (Δ=+0.2437) | `evaluation_benchmark1/Freebase/bench1_all_shapley.log` |
| Freebase / FB15k-237 | 1 | 2p | score necessary | 0.1844 (Δ=-0.0762) | 0.1444 (Δ=-0.0370) | `evaluation_benchmark1/Freebase/bench1_all_score.log` |
| Freebase / FB15k-237 | 1 | 2p | score sufficient | 0.2566 (Δ=+0.2418) | 0.1830 (Δ=+0.1693) | `evaluation_benchmark1/Freebase/bench1_all_score.log` |
| Freebase / FB15k-237 | 1 | 2p | random necessary | 0.2172 (Δ=-0.0434) | 0.1611 (Δ=-0.0203) | `evaluation_benchmark1/Freebase/bench1_all_random.log` |
| Freebase / FB15k-237 | 1 | 2p | random sufficient | 0.2238 (Δ=+0.2090) | 0.1664 (Δ=+0.1527) | `evaluation_benchmark1/Freebase/bench1_all_random.log` |
| Freebase / FB15k-237 | 1 | 2p | first necessary | 0.2346 (Δ=-0.0260) | 0.1597 (Δ=-0.0217) | `evaluation_benchmark1/Freebase/bench1_all_first.log` |
| Freebase / FB15k-237 | 1 | 2p | first sufficient | 0.2064 (Δ=+0.1917) | 0.1678 (Δ=+0.1541) | `evaluation_benchmark1/Freebase/bench1_all_first.log` |
| Freebase / FB15k-237 | 1 | 2p | last necessary | 0.2064 (Δ=-0.0541) | 0.1678 (Δ=-0.0136) | `evaluation_benchmark1/Freebase/bench1_all_last.log` |
| Freebase / FB15k-237 | 1 | 2p | last sufficient | 0.2346 (Δ=+0.2198) | 0.1597 (Δ=+0.1460) | `evaluation_benchmark1/Freebase/bench1_all_last.log` |

### Chart/hình có sẵn trong repo

Các hình dưới đây đã được tạo trước đó trong repo từ `report_artifacts/computed_summary.csv`:

![Delta MRR](report_artifacts/plots/delta_mrr.svg)

![Delta Hits@1](report_artifacts/plots/delta_hit_1.svg)

![Runtime](report_artifacts/plots/runtime.svg)

Lưu ý về chart: `report_artifacts/computed_summary.csv` là artifact rút gọn cho Freebase Benchmark 1 query `2p`; `shapley` có 5,000 queries, còn các baseline trong CSV rút gọn có 2,000 queries. Do đó chart phù hợp để minh họa thực nghiệm nhóm, nhưng không nên trình bày là tái lập đầy đủ Table 2 của paper.

## 6. So sánh với kết quả bài báo

### So sánh trực tiếp trên FB15k-237 / Benchmark 1 / `2p`

Bảng này so sánh kết quả paper Table 2 với log thật của nhóm cho cùng dataset/query type. Paper chỉ báo cáo delta, nên bảng dùng `ΔMRR` và `ΔHits@1`.

| Scenario | Method | Paper ΔMRR | Student ΔMRR | Paper ΔHits@1 | Student ΔHits@1 | Source |
|---|---|---:|---:|---:|---:|---|
| necessary | First-level / `first` | -0.240 | -0.0260 | -0.277 | -0.0217 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_first.log` |
| necessary | Last-level / `last` | -0.500 | -0.0541 | -0.554 | -0.0136 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_last.log` |
| necessary | Random / `random` | -0.377 | -0.0434 | -0.424 | -0.0203 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_random.log` |
| necessary | Score-based / `score` | -0.551 | -0.0762 | -0.610 | -0.0370 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_score.log` |
| necessary | CQD-SHAP / `shapley` | -0.685 | -0.1524 | -0.752 | -0.1113 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_shapley.log` |
| sufficient | First-level / `first` | +0.195 | +0.1917 | +0.157 | +0.1541 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_first.log` |
| sufficient | Last-level / `last` | +0.223 | +0.2198 | +0.148 | +0.1460 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_last.log` |
| sufficient | Random / `random` | +0.207 | +0.2090 | +0.152 | +0.1527 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_random.log` |
| sufficient | Score-based / `score` | +0.246 | +0.2418 | +0.172 | +0.1693 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_score.log` |
| sufficient | CQD-SHAP / `shapley` | +0.318 | +0.3181 | +0.242 | +0.2437 | paper Table 2; `evaluation_benchmark1/Freebase/bench1_all_shapley.log` |

### Nhận xét so sánh

- Với sufficient evaluation trên `2p`, kết quả nhóm gần như trùng với paper ở tất cả methods. Ví dụ CQD-SHAP: paper `ΔMRR=+0.318`, `ΔHits@1=+0.242`; log nhóm `ΔMRR=+0.3181`, `ΔHits@1=+0.2437`.
- Với necessary evaluation trên `2p`, log nhóm thấp hơn paper rất nhiều. Ví dụ CQD-SHAP: paper `ΔMRR=-0.685`, `ΔHits@1=-0.752`; log nhóm `ΔMRR=-0.1524`, `ΔHits@1=-0.1113`.
- Lý do hợp lý nhất từ code/log hiện có: necessary evaluation của paper chỉ xét target answers đang ở rank 1 dưới CQD, còn log nhóm hiện tại average trên phạm vi rộng hơn. Vì vậy necessary result của nhóm không tái lập đúng author setting.
- Xu hướng tương đối vẫn giống ý tưởng paper: trong log nhóm, `shapley` tạo mức giảm mạnh nhất ở necessary và mức tăng cao nhất ở sufficient cho query `2p`.
- Khi làm slide, nên nói rõ: nhóm đã có kết quả thực nghiệm thật cho `2p`, nhưng phần necessary chưa cùng protocol với paper, nên chưa thể gọi là tái lập đầy đủ Table 2.

File output/log đã đọc:

- `evaluation_benchmark1/Freebase/bench1_all_shapley.log`
- `evaluation_benchmark1/Freebase/bench1_all_score.log`
- `evaluation_benchmark1/Freebase/bench1_all_random.log`
- `evaluation_benchmark1/Freebase/bench1_all_first.log`
- `evaluation_benchmark1/Freebase/bench1_all_last.log`
- `report_artifacts/computed_summary.csv`
- `report_artifacts/evaluation_summary_resumed_2p.csv`
- `report_artifacts/evaluation_benchmark1/Freebase/bench1_2p_score.log`
- `report_artifacts/evaluation_benchmark1/Freebase/bench1_2p_random.log`
- `report_artifacts/evaluation_benchmark1/Freebase/bench1_2p_first.log`
- `report_artifacts/evaluation_benchmark1/Freebase/bench1_2p_last.log`

Chart/hình/result đã sử dụng:

- `report_artifacts/plots/delta_mrr.svg`
- `report_artifacts/plots/delta_hit_1.svg`
- `report_artifacts/plots/runtime.svg`
- `report_artifacts/computed_summary.csv`
- `report_artifacts/evaluation_summary_resumed_2p.csv`

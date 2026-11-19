# 跨站频闪复核事故

两站按同一试验出件，中心收件后关闭站库并重开中心库。试验频偏为 0 至 1/4 圈每秒。甲站在 0 秒记录闭弧 3/4→1/4，乙站在 1 秒记录精确零刻线。夜班指定这两份站件预测 2 秒，现有报告给出闭区间 [0,3/4]，误收了 1/2 圈。正确报告是闭区间 [0,1/4]。

在项目根目录执行原事故回归。

```sh
python3 -B -m unittest tests.test_forecast.ForecastTests.test_wrapped_station_and_exact_tick
```

另外两笔原核账可分别检查过零取值和跨时刻取值。第一笔只选频偏为零的甲站过零件，0 秒应得 [0,1/4] 与 [3/4,1)。第二笔甲站改用 0 秒的 [3/4,7/8]，乙站仍是 1 秒零刻线，频偏为 [0,1/4]，2 秒应得 [1/8,1/4]。

```sh
python3 -B -m unittest tests.test_handoff.HandoffTests.test_offline_wrapped_branches tests.test_forecast.ForecastTests.test_complete_evidence_preserves_correlation
```

README.md 说明试验登记、收件、报告领取和数值约定。完整回归与演示沿用项目根目录的 `check_project.py` 和 `demo.py`。

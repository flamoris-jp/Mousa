# Training

The first music-specific composition lives in [Mousa Melody/grid_v1](../specializations/melody/grid_v1/README.md), alongside its native model codec, objective, source-label verification and experiment driver.

Generic training loops, numerical models, checkpoint/resume and contract mechanics remain in external [Maidionis](https://github.com/flamoris-jp/Maidionis). The music CLI calls that engine; it does not copy or reimplement Core here.

This is offline research. No autonomous teacher, human preference trainer or production serving path is included.

# conventions — 程式碼慣例（碰原始碼的工作流共用）

[common/README](README.md)｜[INDEX](../../INDEX.md)

碰原始碼的工作流（feature-dev / refactor / investigation）共用這套規矩：**寫碼時要遵守什麼**。哪個檔負責什麼領域、測試在哪 → [code-map](code-map.md)；真相層優先序也在 [code-map](code-map.md)。結構整理原則 → [STRUCTURE](../../STRUCTURE.md)。


## 慣例

| 項目 | 規矩 |
|------|------|
| 協議為唯一接點 | 改 args／exit code／wav 輸出規格，先改 [PROTOCOL.md](../../../PROTOCOL.md)，並對照 ModForge 的 `Voice.BuildTtsArgs` |
| 失敗語意 | 失敗必 exit 非 0、診斷寫 stderr；`--out` 只在驗證成功後原子取代，不留半成品 |
| 本機環境不進 repo | `.venvs/`、ref clip、訓練資料一律 gitignore；venv 內含絕對路徑，不搬、要換位置就重建 |
| 離線測試不載模型 | 新增測試走 `tests/fake_fish_engine.py`，不得需要 GPU 或模型檔 |

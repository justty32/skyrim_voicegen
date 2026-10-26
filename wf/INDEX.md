# INDEX — skyrim-voicegen 專案地圖

skyrim-voicegen = **ModForge 的語音合成基石工具：收「臺詞＋情緒＋參考嗓音」，吐一個 `.wav`（engine：F5-TTS、Fish Speech）；與 ModForge 只透過 PROTOCOL.md 的 CLI 協議連接（`MODFORGE_TTS_BIN`），互為黑盒**。本檔只描述**頂層**：每列一句話＋連結；目錄內部複雜就放它自己的 README / INDEX。

## Repo 佈局

| 路徑 | 內容 |
|------|------|
| `voicegen.py` | 協議實作：解析 args、跑選定 engine、原子寫出 wav |
| `voicegen-f5.sh、voicegen.sh` | wrapper；`voicegen-f5.sh` 是正式版（`.venvs/f5`），`voicegen.sh` 是舊版僅留參考 |
| [PROTOCOL.md](../PROTOCOL.md) | ModForge ↔ voicegen 合約（args／wav／exit code／engine 行為）|
| `tests/` | 離線測試與 fake engine |
| `README.md` | 人類向說明 |
| `workflows/` | 工作流（派發見 [WORKFLOWS.md](WORKFLOWS.md)；共享區 [workflows/common/](workflows/common/README.md)）|
| `.claude/commands/` | slash 指令適配層（可選）。Claude Code 為例：只讀專案根的這層，非侵入式佈局也留在根；沒有 slash 機制的工具忽略本目錄，直接跑 `tools/wf-lint.sh` |
| `tools/` | kernel 工具：`wf-lint.sh`（檢查）、`tabledb.py`（資料檔 CRUD／連結）、`find_big_lists.py`、`fix_moved_links.py`；非侵入式佈局在 `wf/tools/`；資料檔契約見 [workflows/common/data-files.md](workflows/common/data-files.md) |
<!-- wf-insert:INDEX -->

## 頂層文件

| 檔案 | 角色 |
|------|------|
| [WORKFLOWS.md](WORKFLOWS.md) | 派發器：意圖 → 工作流入口 |
| [STRUCTURE.md](STRUCTURE.md) | 結構整理參考（被動）：分層、膨脹即拆、四級成長、archive、工作流形式 |
| [SESSION-LOG.md](SESSION-LOG.md) | 我的 open 進度 |
| [WAIT_USER.md](../../../WAIT_USER.md) | 母 repo 的等使用者清單（本 repo 不另開）|

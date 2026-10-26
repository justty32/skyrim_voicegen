# skyrim-voicegen — AI agent 專案備忘

skyrim-voicegen = **ModForge 的語音合成基石工具：收「臺詞＋情緒＋參考嗓音」，吐一個 `.wav`（engine：F5-TTS、Fish Speech）；與 ModForge 只透過 [PROTOCOL.md](PROTOCOL.md) 的 CLI 協議連接（`MODFORGE_TTS_BIN`），互為黑盒**。本檔是最頂層路由器，只指向下一層；細節不寫這裡（分層原則見 [STRUCTURE.md](wf/STRUCTURE.md)）。

## 開場與入口

- 每個 session 先跑 `grep -c '^- \[' wf/SESSION-LOG.md`：非 0 才開 [SESSION-LOG.md](wf/SESSION-LOG.md)（進度）。等使用者的事一律記母 repo [WAIT_USER.md](../../WAIT_USER.md)，本 repo 不另開一份。
- **碰原始碼前**：慣例與 code map → [workflows/common/conventions.md](wf/workflows/common/conventions.md)、[workflows/common/code-map.md](wf/workflows/common/code-map.md)；環境與指令 → [workflows/dev-env.md](wf/workflows/dev-env.md)。
<!-- wf-insert:AGENTS -->
- **要你動手做事** → [WORKFLOWS.md](wf/WORKFLOWS.md) 依意圖派發，再讀該工作流入口檔。
- **想看專案結構** → [INDEX.md](wf/INDEX.md)；人類向的完整說明 → [README.md](README.md)。
- 使用者偏好與邊界 → [workflows/common/user.md](wf/workflows/common/user.md)。

## 鐵律（always-on，隨時適用）

1. 重構 / 整理**不改原意**：開發＝行為不變且驗證綠燈（`python -m unittest discover -s tests -v`）；非開發＝原意不變，照 `Done when:` 驗收。
2. **不可逆或對外的動作**（push、刪除、對外送出、動 DB）要有**授權來源**：使用者當場確認，或他親自登記在清單裡（routines / schedule）。都沒有就先問。
3. **條列走資料檔、導航留 md**：給 AI 消化的表／清單 >1 KB 存 `.json`／`.csv`（契約 `wf-table/1`，見 [data-files](wf/workflows/common/data-files.md)），用 `wf/tools/tabledb.py` 讀寫、不整份讀進 context；給人點的導航連結留 md。
4. **具體流程**在各工作流入口檔，不在頂層。

## 專案摘要

Python 為主：`voicegen.py` 實作協議，`voicegen-f5.sh` 是正式 wrapper（在 `.venvs/f5` 內跑）。離線測試用 `tests/fake_fish_engine.py`，不載 TTS 模型（6 項）。真正合成需要本機 venv、GPU 與 ref clip，這些都不進 repo（見 [dev-env.md](wf/workflows/dev-env.md)）。根目錄的 `__pycache__/` 已被 `.gitignore`，不准 add。

<!-- wf-kernel v0.6+368468a (2026-10-26 導入) -->

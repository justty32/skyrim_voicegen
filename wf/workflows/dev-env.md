# dev-env — 開發環境、指令、外部工具

[WORKFLOWS](../WORKFLOWS.md)｜[INDEX](../INDEX.md)

這台機器上要能開發需要什麼、怎麼裝、跑什麼指令；外部工具設定與 env var 也收在這裡。

**何時用**：fresh clone、換機器、裝不起來、忘了指令、要加一個外部工具或環境變數。
**何時不用**：驗證 / 測試怎麼跑 → [testing](testing.md)；程式碼慣例 → [common/conventions](common/conventions.md)。

## Done when

- 照「流程（fresh clone 後）」走完，`python -m unittest discover -s tests -v` 回傳 0。
- 下面三張表沒有空欄；要使用者親自做的（帳號、授權、金鑰）在 [WAIT_USER](../../../../WAIT_USER.md) 各佔一行。

## 流程（fresh clone 後）

1. 取得原始碼（無 submodule）。
2. 離線開發不需要 venv：直接跑下面的冒煙指令。
3. 要真的合成才需要：在 repo 根建 `.venvs/f5`（python 3.11；Blackwell 要 torch cu128），或用 `MODFORGE_VOICEGEN_VENV` 指別處；ref clip 由 ModForge `extract-voices` 抽。
4. 跑一次冒煙指令：`python -m unittest discover -s tests -v`（回傳 0）。

## 指令表

| 做什麼 | 指令 | 備註 |
|--------|------|------|
| 離線測試 | `python -m unittest discover -s tests -v` | 6 項；不需模型或遊戲資料 |
| 真實合成（經 wrapper） | `MODFORGE_TTS_BIN=<repo>/voicegen-f5.sh`，由 ModForge `voicelines`／`scripts/ship-voice.sh` 呼叫 | 需 `.venvs/f5` 與 GPU；agent 離線驗證不跑 |

驗證與測試指令不列這裡——連同「誰跑」一起在 [testing](testing.md)。

## 跨機 / 離線差異

| 環境 | 能跑 | 跑不了的 → 怎麼辦 |
|------|------|------------------|
| 本機（Linux） | 離線 unittest 全部 | 真實合成需 `.venvs/f5`；導入時本 repo 根沒有 `.venvs/`（見 notes），要合成先重建 venv |


## 外部工具與 env var

| 名稱 | 用途 | 怎麼取得 / 設定 |
|------|------|----------------|
| `MODFORGE_TTS_BIN` | ModForge 呼叫本工具的入口 | 指向 `voicegen-f5.sh` 絕對路徑（README 範例路徑指向 `ModForge/sub_projs/…`，現已不存在，實際用本 repo 路徑） |
| `MODFORGE_VOICEGEN_VENV` | 覆寫 f5 venv 位置 | 預設 `<repo>/.venvs/f5` |
| `MODFORGE_FISH_SPEECH_BIN` | fish-s2 engine 的轉呼目標 | fish-s2 才需要；查不到安裝來源 |

需要帳號、付費、授權才能取得的：守鐵律 2（授權來源），並在 [WAIT_USER](../../../../WAIT_USER.md) 記一行。

## 交接

- 環境就緒要開工 → [feature-dev](feature-dev/README.md)；先確認驗證跑得動 → [testing](testing.md)。
- 同一個裝機坑第二次撞到 → [common/gotchas](common/gotchas.md)。

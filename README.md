# Divination Casting Randomizer｜占卜抽牌／起卦隨機器

> **RETIRED / COMPATIBILITY-ONLY**
>
> 本 Repository 已完成遷移並停止新功能開發。新的 canonical stochastic runtime、測試、API/Web 維護與 production deployment authority 已移至：
>
> - Repository：`masini1491/ai-divination-playbook`
> - Canonical implementation：`runtime/casting/randomizer.py`
> - Canonical package root：`runtime/casting/`
> - Current production：<https://ai-divination-playbook-casting-masini1491-9205.vercel.app>
> - Current production API：<https://ai-divination-playbook-casting-masini1491-9205.vercel.app/api/cast>
>
> 本 Repo 保留完整 Git history、既有 commit/blob identities、rollback 與 compatibility 用途，以確保歷史 `runtime_source_commit` provenance 仍可解析。請勿刪除或重寫歷史。未來功能、修正與 contract 變更只在 `ai-divination-playbook` 進行。

一套給人類、ChatGPT／AI runtime 與其他程式使用的 stochastic casting tool 歷史／相容版本。

此 Repo 最後的 canonical legacy runtime 支援：

- **Tarot**：完整 78 張牌、每題 fresh shuffle、獨立正逆位。
- **Meihua**：雙數 A/B 起卦。
- **Liuyao**：三錢法六爻起卦，六爻由初爻至上爻依序產生。

本 Repo 只負責「需要隨機性的原始 Draw / Cast Fact」。它**不負責**完整六爻納甲、世應、六親、六神、奇門／六壬排盤或 AI 解讀；這些由各自 deterministic engine／Playbook 負責。

```text
stochastic acquisition
        ↓
Divination Casting Randomizer
        ↓
raw Draw / Cast Fact
        ↓
method engine / AI interpretation
```

## 入口

### Current canonical production

- **Web UI**：<https://ai-divination-playbook-casting-masini1491-9205.vercel.app>
- **Production Casting API**：<https://ai-divination-playbook-casting-masini1491-9205.vercel.app/api/cast>
- Source：`masini1491/ai-divination-playbook/runtime/casting/`

### Legacy compatibility surface

- **Legacy Web UI**：<https://tarot-plum-randomizer-masini1491-9205.vercel.app>
- **Legacy Casting API**：<https://tarot-plum-randomizer-masini1491-9205.vercel.app/api/cast>
- `index.html`：legacy Web UI snapshot。
- `randomizer.py`：legacy Python / CLI snapshot。
- `API.md`：legacy HTTP API contract snapshot。
- `openapi.json`：legacy OpenAPI 3.1 snapshot。
- `test_randomizer.py`：legacy invariant tests。

Legacy URL 保留是為了 compatibility／rollback，不代表此 Repo 仍是 current production authority。

## HTTP Casting API

Current production endpoint：

```text
POST https://ai-divination-playbook-casting-masini1491-9205.vercel.app/api/cast
Content-Type: application/json
```

Legacy compatibility endpoint：

```text
POST https://tarot-plum-randomizer-masini1491-9205.vercel.app/api/cast
Content-Type: application/json
```

最小 Tarot request：

```json
{"method":"tarot","count":3,"repeat":1}
```

受控 HTTP API 只接受：

- `method`: `tarot` / `plum` / `liuyao`
- `count`: `1..24`，預設 `3`
- `repeat`: `1..20`，預設 `1`

`/api/cast` 只是 `randomizer.py` 的薄 HTTP transport adapter，不維護第二份 RNG。成功時直接回傳 canonical runtime 的 `compact_ai_payload()`，其中包含 algorithm/schema identity、`runtime_source_commit`、Taipei timestamp 與最低充分的 raw Draw / Cast Fact。

API **不接收占卜題目或 reading context**。未知欄位會被拒絕，因此 `question`、人物姓名、關係內容、健康內容或其他解讀上下文都不應送到 Randomizer API。Legacy `both` 只保留於既有 CLI compatibility，不屬於 HTTP API contract。

所有 API response 都設定 `Cache-Control: no-store`。Request body 上限為 1024 bytes，單次 `repeat` 上限為 20；這些是 request bounds，不代表跨 Vercel Function instance 的 durable rate limit。

完整 legacy human-readable contract 見 [`API.md`](API.md)；machine-readable schema 見 [`openapi.json`](openapi.json)。Current contract 請以 `ai-divination-playbook/runtime/casting/` 為準。

## Python / AI Runtime CLI

此處 `randomizer.py` 為 legacy compatibility snapshot；current canonical implementation 位於 `ai-divination-playbook/runtime/casting/randomizer.py`。

`randomizer.py` 僅使用 Python 標準庫。

### Tarot

```bash
python randomizer.py tarot --count 6
```

### Meihua

```bash
python randomizer.py plum
```

### Liuyao｜三錢法

```bash
python randomizer.py liuyao
```

也可明示目前唯一正式支援的六爻 casting method：

```bash
python randomizer.py liuyao --method coins
```

### Tarot + Meihua

`both` 為既有相容入口，仍明確表示 Tarot + Meihua，不會自動加入 Liuyao：

```bash
python randomizer.py both --count 6
```

### JSON

AI／程式整合優先使用：

```bash
python randomizer.py liuyao --format json
```

Top-level metadata 包含：

- `source`
- `algorithm_version`
- `schema_version`
- `supported_methods`
- `runtime_source_commit`
- `generated_at_utc`
- `generated_at_taipei`
- `timezone`
- RNG 說明
- `results`

`source = divination-casting-randomizer-python` 是 logical runtime identity；Repo relocation 不改寫既有歷史 identity。

## Canonical Randomness

### Python

- `secrets.randbits(32)` 取得系統級亂數。
- rejection sampling 產生 bounded integer，避免簡單取模偏差。
- Tarot 使用 Fisher–Yates。
- 每張正逆位獨立抽取。
- Meihua A/B 各自獨立取值。
- Liuyao 每一爻的三枚銅錢皆為獨立公平二元抽樣。

### Web

- 優先使用 `crypto.getRandomValues()`。
- 使用完整 `2^32` 範圍做 rejection sampling。
- 只有 Web Crypto 不可用時才退回 `Math.random()`。

Web 與 Python 不追求同 seed / 同序列；它們追求相同的 casting contract 與無人工挑選。

## Tarot Contract

- 78 張唯一牌組。
- 單題 1～24 張。
- 單題內不重複。
- 每個 question identity 重新洗完整牌組。
- 正／逆位固定開啟且每張獨立。

## Meihua Contract

固定雙數：

- A、B 各為 `000～999`。
- `A % 8` → 上卦。
- `B % 8` → 下卦。
- `(A+B) % 6` → 動爻。
- 八卦餘 0 → 坤。
- 動爻餘 0 → 第 6 爻。

## Liuyao Contract｜三錢法

目前只提供 **raw three-coin casting**，不在本 Repo 做完整六爻排盤／解卦。

每一爻：

1. 獨立擲三枚公平銅錢。
2. canonical mapping：
   - `yin = 2`
   - `yang = 3`
3. 三枚相加得到 `6 / 7 / 8 / 9`：
   - `6 = 老陰`，陰爻、動爻
   - `7 = 少陽`，陽爻、靜爻
   - `8 = 少陰`，陰爻、靜爻
   - `9 = 老陽`，陽爻、動爻
4. 六次起卦順序固定為 **初爻 → 二爻 → 三爻 → 四爻 → 五爻 → 上爻**。

單爻理論分布因此自然為：

```text
6: 1/8
7: 3/8
8: 3/8
9: 1/8
```

JSON 會保留每爻的原始 `coin_values`、`coin_faces`、`value`、陰陽、動靜與爻位，方便外部 engine 後續排本卦／變卦、納甲、世應、六親與六神。

範例 shape：

```json
{
  "method": "liuyao",
  "liuyao": {
    "cast_method": "three-coins",
    "line_order": "bottom-to-top",
    "lines": [
      {
        "position": 1,
        "position_name": "初爻",
        "coin_values": [3, 2, 2],
        "coin_faces": ["yang", "yin", "yin"],
        "value": 7,
        "yin_yang": "yang",
        "changing": false,
        "line_type": "少陽"
      }
    ]
  }
}
```

## Version Semantics

Legacy snapshot：

```text
algorithm_version: 2
schema_version: 4
```

- v2：新增 canonical Liuyao three-coin stochastic contract；Web rejection sampling 同步使用完整 `2^32` range。
- schema v4：新增 `supported_methods` 與 Liuyao result shape。
- 只改 README、UI 文案或其他不改變 runtime result contract 的內容，不應升 `algorithm_version`。

此 Repo retirement pointer 不改 algorithm/schema。後續版本變更只在 `ai-divination-playbook` 進行。

## Web UI

Legacy Web UI 支援：

- 多題連續 Tarot。
- 單題 Tarot。
- 單題 Meihua。
- 單題 Liuyao 三錢六爻。
- 單題 Tarot + Meihua 相容入口。
- 一鍵複製結果。
- 手機響應式排版。

Web Liuyao 與 Python 使用相同：

```text
yin=2 / yang=3
→ three independent fair coins per line
→ 6/7/8/9
→ bottom-to-top six lines
```

## 驗證

Legacy snapshot 可執行：

```bash
python -m unittest -v
```

這些測試保留作 rollback／historical verification；current maintenance CI 位於 `ai-divination-playbook`。

## Retirement / provenance policy

- 此 Repo 不再接受新 feature development。
- Current runtime、API、Web、tests 與 contract maintenance 均在 `masini1491/ai-divination-playbook`。
- Git history 與既有 commits 保留，供歷史 `runtime_source_commit` 查核。
- `17cc4c84fd5c09b60de721b671c1d6511ab3d0e9` 是 monorepo migration 所 pin 的 legacy source baseline。
- 不刪除 Repo；若設為 GitHub Archived，仍保留 read-only history。
- rollback 若需要，可依 migration contract 暫時重新部署已知良好的 legacy commit；這不恢復此 Repo 的 feature authority。

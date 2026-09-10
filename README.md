# Divination Casting Randomizer｜占卜抽牌／起卦隨機器

一套給人類、ChatGPT／AI runtime 與其他程式使用的 **canonical stochastic casting tool**。

目前正式支援：

- **Tarot**：完整 78 張牌、每題 fresh shuffle、獨立正逆位。
- **Meihua**：雙數 A/B 起卦。
- **Liuyao**：三錢法六爻起卦，六爻由初爻至上爻依序產生。

本 Repo 只負責「需要隨機性的原始 Draw / Cast Fact」。它**不負責**完整六爻納甲、世應、六親、六神、奇門／六壬排盤或 AI 解讀；這些應由各自 deterministic engine／Playbook 負責。

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

- **線上 Web UI**：<https://tarot-plum-randomizer-masini1491-9205.vercel.app>
- `index.html`：瀏覽器／手機 Web UI。
- `randomizer.py`：Python / ChatGPT / AI runtime / CLI canonical implementation。
- `test_randomizer.py`：標準庫 invariant tests。

目前 Vercel deployment 仍沿用 Repo rename 前的 `tarot-plum-randomizer` URL；Repo rename 不影響既有部署網址的使用。

## Python / AI Runtime CLI

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

`source = divination-casting-randomizer-python` 表示結果來自 canonical runtime execution，而不是語言模型自行生成。

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

目前：

```text
algorithm_version: 2
schema_version: 4
```

- v2：新增 canonical Liuyao three-coin stochastic contract；Web rejection sampling 同步使用完整 `2^32` range。
- schema v4：新增 `supported_methods` 與 Liuyao result shape。
- 只改 README、UI 文案或其他不改變 runtime result contract 的內容，不應升 `algorithm_version`。

## Web UI

目前 Web UI 支援：

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

執行：

```bash
python -m unittest -v test_randomizer.py
```

最低 invariants 包含：

- 78 張牌唯一。
- Tarot 1～24 boundary。
- 單題無重複牌。
- 多題獨立 draw shape。
- Meihua A/B、動爻與 64 卦 mapping。
- Liuyao 四種爻值 mapping。
- Liuyao 六爻由初爻至上爻。
- 每爻三枚 coin value 只能為 2／3，且總和等於 6／7／8／9。
- 6／9 必為動爻；7／8 必為靜爻。
- Liuyao CLI JSON 可解析。
- package 版本與 `supported_methods` 正確。

## 與 AI Divination Playbook 的責任分工

- **本 Repo**：RNG、raw Tarot / Meihua / Liuyao Draw-Cast Fact、CLI/Web 與結果格式。
- **`masini1491/ai-divination-playbook`**：自然語言題目、method routing、Runtime governance、reading lifecycle、record、interpretation / reconciliation。

Randomizer 支援某個 casting method，**不代表 Playbook 已經正式啟用該方法的自動 routing／解讀**。方法要進入 Playbook，仍需有清楚的 method owner、judgment function、deterministic downstream engine boundary 與 behavioral regression。

## 專案結構

```text
.
├── index.html
├── randomizer.py
├── test_randomizer.py
└── README.md
```

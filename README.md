# Divination Casting Randomizer｜占卜抽取／起卦隨機器

`divination-casting-randomizer` 是給 ChatGPT、AI agent、CLI 與瀏覽器使用的 **canonical stochastic casting tool**。它只負責需要隨機抽樣的占卜輸入，不負責題目設計、術數排盤後續規則或 AI 解讀。

目前已實作的方法：

- **Tarot**：完整 78 張牌、單題 1～24 張、每題 fresh Fisher–Yates shuffle、每張獨立正逆位。
- **Meihua**：雙數 A/B 起卦；A、B 各為 `000～999`，依固定餘數規則取得上下卦與動爻。

未來若加入其他需要真正隨機抽樣的 casting method（例如六爻三錢法），也應沿用同一 RNG／provenance 邊界；奇門、大六壬等以時間或其他 deterministic input 排局的方法不屬於本 Repo 的 Randomizer scope。

## 入口

- `index.html`：瀏覽器／手機 Web UI。
- `randomizer.py`：ChatGPT／AI sandbox／CLI 的 canonical Python runtime implementation。

現行 Vercel 部署網址仍沿用舊 deployment 名稱：

<https://tarot-plum-randomizer-masini1491-9205.vercel.app>

GitHub canonical repository：

`masini1491/divination-casting-randomizer`

## Tarot contract

- 完整 78 張牌。
- 單題可抽 1～24 張。
- 同一題不重複。
- 每個 question identity 都重新建立完整牌組並重新洗牌。
- 正／逆位固定啟用，每張獨立抽取。
- 多題／多人物時，每題都是獨立 draw identity，不延續上一題剩餘牌組。

CLI：

```bash
python randomizer.py tarot --count 6
```

## Meihua contract

固定採雙數起卦：

- 隨機產生 A、B，各為 `000～999`。
- `A % 8` → 上卦。
- `B % 8` → 下卦。
- `(A + B) % 6` → 動爻。
- 八卦餘 0 → 坤；動爻餘 0 → 第 6 爻。

CLI：

```bash
python randomizer.py plum
```

同一題同時取得 Tarot + Meihua：

```bash
python randomizer.py both --count 6
```

多個獨立題目：

```bash
python randomizer.py batch --counts 5,5,6,3
python randomizer.py batch --counts 5,5,6,3 --method both
```

## JSON / provenance

AI／程式整合優先使用 JSON：

```bash
python randomizer.py both --count 6 --format json
```

目前 Python runtime source identity：

```text
source = divination-casting-randomizer-python
algorithm_version = 1
schema_version = 3
```

`source` 代表結果來自實際 runtime execution，不是語言模型自行報牌。`algorithm_version` 只在抽樣／起卦核心契約改變時升版；repository rename、source identity 或其他 metadata schema 變化只升 `schema_version`。

JSON 亦保存：

- `runtime_source_commit`
- `generated_at_utc`
- `generated_at_taipei`
- `timezone`
- RNG 說明
- 各題實際 Tarot／Meihua result

## RNG

### Python

`randomizer.py` 只使用 Python 標準庫：

- `secrets.randbits(32)` 作為系統級亂數來源。
- 32-bit rejection sampling 產生 bounded integer，避免簡單取模偏差。
- Tarot 使用 Fisher–Yates shuffle。
- 每張正逆位另做一次獨立二元抽取。

### Web

`index.html`：

- 優先使用 `crypto.getRandomValues()`。
- raw RNG 階段使用 rejection sampling。
- Tarot 使用 Fisher–Yates shuffle。
- 只有瀏覽器沒有 Web Crypto 時才退回 `Math.random()`。

Web 與 Python 不要求相同牌序；要求的是相同 casting contract 與無人工挑選。

## 驗證

```bash
python -m unittest -v test_randomizer.py
```

目前 invariant tests 包含：

- 78 張牌且唯一。
- 單題最大 24 張仍不重複。
- 多題各自形成獨立 draw。
- 梅花 A/B 固定三位數、動爻 1～6。
- 8×8 上下卦完整覆蓋 64 卦。
- 非法 Tarot count 會被拒絕。

## Authority boundary

```text
Divination Casting Randomizer
= stochastic Draw / Cast Fact acquisition

AI Divination Playbook
= question contract / method routing / runtime governance /
  interpretation / lifecycle / record / backtest

Method-specific deterministic engine
= 六爻納甲、奇門排局、大六壬起課等後續結構化計算
```

配套 Playbook：

`masini1491/ai-divination-playbook`

語言模型能寫出牌名，不等於已完成隨機抽牌。若 ChatGPT 宣稱使用 Runtime Draw，應能指出實際 execution source；執行環境不可用時必須 fail closed，而不是自行生成結果冒充 Randomizer。

## 專案結構

```text
.
├── index.html          # Web UI
├── randomizer.py       # Python / ChatGPT runtime CLI
├── test_randomizer.py  # standard-library invariant tests
└── README.md
```

Web 部署不需要 Python；Vercel 主要入口仍是 `index.html`。Python CLI 是獨立 runtime／AI 使用入口。

文件與 UI 以繁體中文（`zh-Hant`）為主；程式識別字保留英文。
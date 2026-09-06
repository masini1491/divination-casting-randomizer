# 塔羅牌＋梅花易數隨機抽取器

一套共用同一抽牌／起卦契約的塔羅牌與梅花易數隨機工具：

- `index.html`：瀏覽器／手機直接操作的 Web UI。
- `randomizer.py`：供 ChatGPT、AI sandbox、CLI 或其他 Python runtime 執行的標準庫版本。

兩種入口都維持相同的核心規則：完整 78 張塔羅牌、單題內不重複、每題重新洗完整牌組、固定正逆位隨機，以及梅花雙數 A/B 起卦契約。

## 線上使用

Vercel：<https://tarot-plum-randomizer-masini1491-9205.vercel.app>

## 功能

### 塔羅牌

- 使用完整 78 張塔羅牌組。
- 單題可抽 1～24 張。
- 固定啟用正位／逆位隨機，不提供關閉選項。
- 同一次抽牌不會出現重複牌。
- 支援多題連續抽牌，每題可獨立設定 1～24 張。
- 連續抽牌時，每一題都重新洗完整牌組；不同題目是獨立 draw identity。
- 使用精簡牌名輸出，例如：`杯后正`、`劍七逆`、`命輪正`。

### 梅花易數

- 固定採用「雙數起卦」。
- 隨機產生兩個 `000～999` 的數字 A、B。
- `A ÷ 8` 的餘數決定上卦。
- `B ÷ 8` 的餘數決定下卦。
- `(A + B) ÷ 6` 的餘數決定動爻。
- 八卦餘數為 0 時視為坤卦；動爻餘數為 0 時視為第 6 爻。
- 顯示上卦、下卦、動爻與完整六十四卦本卦名稱，例如：`水雷屯`、`乾為天`、`火水未濟`。

## Web UI

`index.html` 支援：

- 單題只抽塔羅、只起梅花或兩者同時取得。
- 多題連續塔羅。
- 一鍵複製結果。
- 複製內容依序為：題目 → 時間 → 結果。
- 手機版響應式排版。

### Web 隨機方式

- 優先使用瀏覽器 `crypto.getRandomValues()`。
- 在 raw RNG 階段使用拒絕取樣，避免簡單取模偏差。
- 塔羅使用 Fisher–Yates 洗牌。
- 只有瀏覽器沒有 Web Crypto 時才退回 `Math.random()`。

## Python / AI Runtime CLI

`randomizer.py` **只使用 Python 標準庫**，不需要安裝套件。主要用途是讓具有 Python 執行環境的 ChatGPT／AI agent 實際執行 canonical 抽牌程式，而不是由語言模型自行產生看似隨機的牌名。

### 單題塔羅

```bash
python randomizer.py tarot --count 6
```

### 單題梅花

```bash
python randomizer.py plum
```

### 同一題塔羅＋梅花

```bash
python randomizer.py both --count 6
```

### 多個獨立題目

例如四題分別抽 5、5、6、3 張：

```bash
python randomizer.py batch --counts 5,5,6,3
```

每一題都會重新執行一份完整 78 張牌的 Fisher–Yates 洗牌，不把上一題剩餘牌組延續到下一題。

若四題都需要塔羅＋梅花：

```bash
python randomizer.py batch --counts 5,5,6,3 --method both
```

### JSON 輸出

AI／程式整合優先使用：

```bash
python randomizer.py both --count 6 --format json
```

JSON 會包含：

- `source`
- `algorithm_version`
- `generated_at_utc`
- RNG 說明
- 每題 Tarot cards／orientation
- 梅花 A、B、本卦、上下卦與動爻

`source = tarot-plum-randomizer-python` 表示結果來自真正的 runtime execution，不是語言模型自行報牌。

## Python 隨機方式

- 使用標準庫 `secrets.randbits(32)` 取得系統級亂數來源。
- 以 32-bit rejection sampling 產生無簡單取模偏差的 bounded integer。
- 塔羅使用 Fisher–Yates 洗牌後取指定張數。
- 每張正／逆位另做一次獨立二元抽取。
- 每個 question identity 都建立新的完整牌組 shuffle。

Web 與 Python 使用不同平台 RNG API，因此不追求相同輸入產生相同牌序；它們追求的是**相同抽牌／起卦契約與無人工挑牌**。

## 驗證

執行：

```bash
python -m unittest -v test_randomizer.py
```

目前 invariant tests 檢查：

- 牌組恰為 78 張且無重複。
- 單題抽 24 張仍不重複。
- 多題可使用不同張數且各自形成獨立 draw。
- 梅花 A/B 固定三位數、動爻為 1～6。
- 8×8 上下卦組合完整覆蓋 64 卦。
- 0 張／25 張等非法 Tarot count 會被拒絕。

## 複製結果範例

```text
題目：這是範例問題
2026/08/31 13:30
塔羅（5 張）
杯后正，劍七逆，命輪正，杖三正，錢二逆

梅花易數｜雙數起卦
574，393
本卦：水天需
上卦：坎
下卦：乾
動爻：第 1 爻
取卦規則：A÷8→上卦；B÷8→下卦；(A+B)÷6→動爻；餘0分別視為坤／第6爻
```

## 專案結構

```text
.
├── index.html          # Web UI
├── randomizer.py       # Python / ChatGPT runtime CLI
├── test_randomizer.py  # 標準庫 unittest invariants
└── README.md
```

Web 部署不需要 Python；Vercel 主要入口仍是 `index.html`。Python CLI 是獨立的 runtime／AI 使用入口。

## 與 Playbook 的責任分工

- **本 Repo**：負責 deterministic algorithm implementation、抽牌／起卦與結果格式化。
- **`masini1491/tarot-meihua-question-playbook`**：負責題目契約、何時允許 ChatGPT 自行執行 runtime draw、來源紀錄、補占紀律與解讀治理。

語言模型能寫出牌名不等於已完成隨機抽牌。若 ChatGPT 宣稱使用 Runtime Draw，應能指出實際執行來源；執行環境不可用時，應回退到 Web UI／使用者自行抽牌，而不是假裝執行。

## 部署

GitHub `main` 分支與 Vercel 已連動；更新 `main` 後會自動觸發 Web UI 部署。`randomizer.py` 不參與瀏覽器頁面建置。

## 語言

使用者介面與專案文件以繁體中文（`zh-Hant`）為主。程式內部函式名稱與變數名稱保留英文識別字，以維持程式碼可讀性與維護便利性。

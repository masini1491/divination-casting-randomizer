# Casting API

`/api/cast` 是 `randomizer.py` 的薄 HTTP transport adapter。它不實作第二份 RNG、不接收占卜題目，也不負責 routing 或 interpretation。

## Request

```http
POST /api/cast
Content-Type: application/json
```

```json
{"method":"tarot","count":3,"repeat":1}
```

只接受：

- `method`: `tarot` / `plum` / `liuyao`
- `count`: `1..24`，預設 `3`
- `repeat`: `1..20`，預設 `1`

未知欄位會被拒絕，因此 `question`、人物姓名、關係內容、健康內容或其他 reading context 都不應送到此 API。Legacy `both` 不屬於受控 HTTP API contract。

## Response

成功時回傳 `compact_ai_payload()` 的低 token AI transport：

- canonical source / algorithm / schema identity
- `ai_schema_version`
- `runtime_source_commit`
- Taipei draw/cast timestamp
- 最低充分 Tarot / Meihua / Liuyao raw fact

Vercel deployment 會用 `VERCEL_GIT_COMMIT_SHA` 注入 `runtime_source_commit`；非 Vercel 本機執行則明確為 `unknown`。

所有 API response 都設定 `Cache-Control: no-store`；request body 上限 1024 bytes，單次 `repeat` 上限 20，以限制單次請求成本。這些是 request bounds，**不是跨 instance 的 rate limit**。

## OpenAPI

Machine contract 位於根目錄 `openapi.json`。

## Rate limiting boundary

跨 Vercel Function instance 的可靠 rate limit 應由 Vercel Firewall / rate-limit service 等 shared enforcement layer 提供，不使用 Python process global counter 假裝成 durable rate limit。啟用前應另外驗證目前 Vercel project / plan 可用的 enforcement path。

## Tests

```bash
python -m unittest -v
```

測試涵蓋原 Randomizer invariants、import API / compact projection、HTTP request validation / headers，以及 Web ↔ Python shared contract vectors。

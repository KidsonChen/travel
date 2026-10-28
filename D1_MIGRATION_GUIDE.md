# D1 資料庫遷移指南

## 概述
記帳功能已從 localStorage 遷移到 Cloudflare D1 資料庫，實現跨裝置同步。

## 已完成的修改

### Phase 1: D1 資料庫設定
- ✅ 建立 `d1-schema.sql` - 資料庫 Schema
- ✅ 建立 `wrangler.toml` - Worker 配置

### Phase 2: Cloudflare Worker API
- ✅ 建立 `worker/worker.js` - REST API 端點
  - `GET /api/expenses` - 取得所有支出
  - `POST /api/expenses` - 新增支出
  - `DELETE /api/expenses/:id` - 刪除支出
  - `POST /api/migrate` - 從 localStorage 遷移資料

### Phase 3: 前端整合
- ✅ 修改 `splitbill.html`
  - 新增 D1 API 整合
  - 雙寫策略（同時寫入 localStorage 和 D1）
  - 離線模式支援
  - 網路狀態指示器
  - 自動遷移現有資料

## 部署步驟

### 1. 建立 D1 資料庫
前往 Cloudflare Dashboard：
1. Workers & Pages → D1
2. 點擊 "Create Database"
3. 名稱：`split-billing`
4. 選擇離你最近的地區
5. **複製資料庫 ID**

### 2. 執行資料庫 Schema
1. 在 D1 資料庫頁面點擊 "Query Editor"
2. 貼上 `d1-schema.sql` 的內容
3. 點擊 "Run" 執行

### 3. 部署 Worker
**選項 A：使用 Cloudflare Dashboard**
1. Workers & Pages → Create Application → Create Worker
2. 名稱：`split-billing-api`
3. 將 `worker/worker.js` 的內容貼入編輯器
4. Save and Deploy
5. 在 Worker Settings → Variables → D1 Database Bindings
   - 選擇你的 `split-billing` 資料庫
   - 變數名稱：`D1`

**選項 B：使用 Wrangler CLI**
```bash
# 安裝 wrangler
npm install -g wrangler

# 登入 Cloudflare
wrangler login

# 更新 wrangler.toml 中的 database_id
# 然後部署
wrangler deploy
```

### 4. 更新前端 API URL
編輯 `splitbill.html`，找到這一行：
```javascript
const API_BASE_URL = 'https://split-billing-api.your-account.workers.dev';
```
替換為你的實際 Worker URL（例如：`https://split-billing-api.abc123.workers.dev`）

## 功能說明

### 雙寫策略
- 新增支出時，同時寫入 D1 和 localStorage
- 如果網路失敗，仍會保存到 localStorage
- 網路恢復時，自動同步到 D1

### 離線模式
- 自動偵測網路狀態
- 離線時顯示通知
- 所有操作仍可執行（使用 localStorage）
- 恢復連線時自動同步

### 自動遷移
- 首次開啟時，自動將 localStorage 資料遷移到 D1
- 遷移完成後設定 `splitbill_migrated` 標記
- 匯入 JSON 時也會自動遷移到 D1

## 測試清單

### 基本功能測試
- [ ] 新增支出（有網路）
- [ ] 新增支出（離線模式）
- [ ] 刪除支出
- [ ] 查看支出清單
- [ ] 查看結算明細

### 同步功能測試
- [ ] 從另一個裝置存取，確認資料同步
- [ ] 清除瀏覽器快取後重新載入，確認資料仍存在
- [ ] 匯出 JSON 後匯入，確認資料正確

### 離線模式測試
- [ ] 關閉網路，新增支出
- [ ] 恢復網路，確認資料同步到 D1
- [ ] 確認網路狀態指示器正確顯示

## 故障排除

### 無法連接到 Worker API
1. 檢查 Worker URL 是否正確
2. 確認 Worker 已成功部署
3. 檢查 D1 資料庫綁定是否正確

### 資料未同步
1. 檢查瀏覽器 Console 是否有錯誤訊息
2. 確認 `splitbill_migrated` 標記是否已設定
3. 嘗試手動呼叫 `syncToD1()` 函數

### 離線模式異常
1. 確認 localStorage 正常運作
2. 檢查 `isOnline` 變數狀態
3. 查看網路監聽器是否正確觸發

## 注意事項

1. **資料安全**：目前 CORS 設定為 `*`，生產環境建議限制允許的網域
2. **認證**：目前無身份驗證，所有資料公開，建議未來加入使用者認證
3. **資料備份**：建議定期匯出 JSON 備份
4. **D1 限制**：
   - 單一資料庫最大 10MB
   - 單一資料列最大 10MB
   - 查詢結果最大 2MB

## 檔案清單

```
奧捷旅遊/
├── d1-schema.sql          # D1 資料庫 Schema
├── wrangler.toml          # Worker 配置
├── worker/
│   └── worker.js          # Worker API 程式碼
├── splitbill.html         # 已修改的前端頁面
└── D1_MIGRATION_GUIDE.md  # 本說明文件
```

## 下一步建議

1. 加入使用者認證（Cloudflare Access 或自訂認證）
2. 實作即時同步（WebSocket 或 Polling）
3. 加入資料版本控制與衝突解決
4. 實作資料加密
5. 加入匯出 CSV/PDF 功能

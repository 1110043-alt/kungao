# ⚡ 快速參考卡 - 常用命令速查

## 📱 Discord 命令

```
/add 演唱會名稱 https://URL       → 開始監控
/list                             → 查看監控清單
/check                            → 立即檢查一次
/remove 演唱會名稱                → 停止監控
/test                             → 發送測試通知
/guide                            → 顯示命令說明
```

---

## 🖥️ Linux 伺服器命令

### 系統服務管理（systemd）

```bash
# 檢查狀態
sudo systemctl status discord-bot

# 啟動服務
sudo systemctl start discord-bot

# 重啟服務
sudo systemctl restart discord-bot

# 停止服務
sudo systemctl stop discord-bot

# 開機自動啟動
sudo systemctl enable discord-bot

# 檢查日誌
sudo journalctl -u discord-bot -f
```

### 日誌查看

```bash
# 查看最後 20 行
tail -20 /root/discord-bot/bot.log

# 實時監控
tail -f /root/discord-bot/bot.log

# 查看警報
grep "RED TEXT ALERT" /root/discord-bot/bot.log

# 查看錯誤
grep "ERROR" /root/discord-bot/bot.log

# 統計警報次數
grep -c "RED TEXT ALERT" /root/discord-bot/bot.log
```

### 進程管理（nohup 方式）

```bash
# 啟動
nohup python3 /root/discord-bot/bot.py > /root/discord-bot/bot.log 2>&1 &

# 查看進程
ps aux | grep bot.py

# 殺死進程
kill [PID]

# 強制殺死
kill -9 [PID]
```

### 進程管理（screen 方式）

```bash
# 建立新會話
screen -S discord-bot

# 附加到會話
screen -r discord-bot

# 分離會話
Ctrl + A，然後 D

# 列表所有會話
screen -ls

# 終止會話
screen -X -S discord-bot quit
```

---

## 📊 監控指標

| 檔案位置 | 用途 |
|---------|------|
| `/root/discord-bot/bot.py` | Bot 主程式 |
| `/root/discord-bot/bot.log` | 運行日誌 |
| `/root/discord-bot/concerts.json` | 監控配置 |
| `/etc/systemd/system/discord-bot.service` | systemd 服務檔 |

---

## 🔴 紅字偵測格式

✅ 可被偵測的格式：
- `A區剩餘5票`
- `特區剩餘12票`
- `綠406區剩餘57票`
- `VIP區剩餘1票`

❌ 無法偵測的格式：
- `A區 5票`（缺少「剩餘」）
- `剩餘5張`（缺少區域名稱）
- `熱銷中`（無數字）

---

## 🎯 常見操作

### 新增演唱會監控

1. 在 Discord 輸入：
   ```
   /add 五月天 https://tixcraft.com/ticket/area/26_mayday/22437
   ```

2. Bot 確認後開始監控

3. 等待 Discord 通知（通常在幾秒內）

### 檢查監控狀態

1. 輸入 `/list` 查看所有監控

2. 或查看 `/root/discord-bot/concerts.json`：
   ```bash
   cat /root/discord-bot/concerts.json | python -m json.tool
   ```

### 立即檢查一次

```
/check
```

會立即檢查所有監控 URL，不用等待循環時間。

### 移除監控

```
/remove 演唱會名稱
```

---

## 🔧 故障快速排查

### Bot 離線

```bash
# 步驟 1：檢查狀態
sudo systemctl status discord-bot

# 步驟 2：查看日誌
tail -20 /root/discord-bot/bot.log

# 步驟 3：重啟
sudo systemctl restart discord-bot

# 步驟 4：驗證
sudo systemctl status discord-bot
```

### 沒有收到通知

```bash
# 步驟 1：檢查紅字是否被偵測
grep "RED TEXT ALERT" /root/discord-bot/bot.log

# 步驟 2：檢查 Discord 頻道
# 確認 Bot 有權限發送訊息

# 步驟 3：發送測試通知
# 在 Discord 輸入 /test

# 步驟 4：檢查日誌
tail -f /root/discord-bot/bot.log
```

### 服務卡住/無回應

```bash
# 步驟 1：重啟服務
sudo systemctl restart discord-bot

# 步驟 2：查看進程狀態
ps aux | grep bot.py

# 步驟 3：強制重啟（如果重啟無效）
sudo systemctl stop discord-bot
sleep 5
sudo systemctl start discord-bot
```

---

## 📈 效能優化

### 降低 CPU 占用

```bash
# 編輯 bot.py，修改檢查間隔
CHECK_INTERVAL = 5  # 改為 5 秒（從 1 秒）
```

### 查看資源占用

```bash
# CPU 和記憶體占用
ps aux | grep bot.py

# 即時監控
top -p $(pgrep -f bot.py)

# 記憶體詳細信息
cat /proc/[PID]/status | grep VmRSS
```

---

## 🎓 教學視頻（模擬）

### 部署流程
```
1️⃣  SSH 連接伺服器
2️⃣  安裝 Python 和依賴
3️⃣  上傳 bot.py
4️⃣  設置 systemd 服務
5️⃣  啟動 Bot
6️⃣  在 Discord 添加演唱會
7️⃣  等待通知！
```

### 日常監控
```
1️⃣  每天早上檢查 Bot 狀態
    sudo systemctl status discord-bot

2️⃣  檢查是否收到警報
    grep "RED TEXT ALERT" /root/discord-bot/bot.log

3️⃣  根據需要添加/移除監控
    /add 新演唱會 URL
    /remove 舊演唱會

4️⃣  發現票券時立即購票！
```

---

## 📞 快速支援

| 問題 | 解決方案 |
|------|---------|
| Bot 離線 | `sudo systemctl restart discord-bot` |
| 無法發送命令 | 檢查 Bot 是否已同步命令 |
| 沒有收到通知 | 檢查 `/root/discord-bot/bot.log` |
| 記憶體占用高 | 檢查是否添加了太多 URL，增加 CHECK_INTERVAL |
| 被網站封禁 | 增加 CHECK_INTERVAL（如改為 10 秒） |

---

## 🎁 Pro 小技巧

1. **備份配置**
   ```bash
   cp /root/discord-bot/concerts.json concerts.json.bak
   ```

2. **查看所有演唱會**
   ```bash
   cat /root/discord-bot/concerts.json | python -m json.tool
   ```

3. **清空監控列表**
   ```bash
   rm /root/discord-bot/concerts.json
   ```

4. **檢查 Bot Token 是否有效**
   ```bash
   grep "Bot connected" /root/discord-bot/bot.log
   ```

5. **設置定時重啟（每天早上 3 點）**
   ```bash
   # 編輯 crontab
   crontab -e
   
   # 添加這一行
   0 3 * * * sudo systemctl restart discord-bot
   ```

---

**祝你購票成功！🎉 有任何問題查看 MONITORING_SETUP_GUIDE.md 詳細文檔**

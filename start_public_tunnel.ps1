# Cloudflare Tunnel - 將本地伺服器暴露到公網
Write-Host "🚀 啟動公網 Tunnel..." -ForegroundColor Green
Write-Host "本地伺服器: http://127.0.0.1:8888" -ForegroundColor Cyan
Write-Host "公網 URL 將在下方顯示..." -ForegroundColor Yellow
Write-Host ""

# 啟動 Cloudflare Tunnel（QuickTunnel - 無需登錄）
.\cloudflared.exe tunnel --url http://127.0.0.1:8888

Write-Host ""
Write-Host "💡 提示: 該 URL 每次重啟會改變。若需固定 URL，請登錄 Cloudflare 帳戶使用命名 Tunnel" -ForegroundColor Gray

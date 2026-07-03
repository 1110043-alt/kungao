# 🐳 台股預測儀表板 - Docker 容器化配置
# 適用於: Zeabur、Render、任何支援 Docker 的平台

FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 複製應用代碼
COPY . .

# 暴露端口（數值由環境變數覆蓋）
EXPOSE 5555

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5555/api/all-stocks').read()"

# 啟動應用
CMD ["python", "cloud_ready_app.py"]

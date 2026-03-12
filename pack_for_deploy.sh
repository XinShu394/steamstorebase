#!/bin/bash
# Steam Crawler - 一键打包脚本 (Linux/Mac)

PACK_NAME="steamcrawler_$(date +%Y%m%d_%H%M%S)"
PACK_DIR="./$PACK_NAME"

echo "====================================="
echo "Steam Crawler - Packaging Tool"
echo "====================================="

# 1. 创建打包目录
echo -e "\n[1/5] Creating package directory..."
mkdir -p "$PACK_DIR"

# 2. 复制核心文件
echo "[2/5] Copying source code..."
cp -r src "$PACK_DIR/"

echo "[3/5] Copying documentation..."
cp -r docs "$PACK_DIR/"

echo "[4/5] Copying scripts and configs..."
cp -r scripts "$PACK_DIR/"
cp requirements.txt "$PACK_DIR/"
cp *.md "$PACK_DIR/"
cp start_concurrent.* "$PACK_DIR/"
cp .gitignore "$PACK_DIR/"

# 3. 复制进度数据（可选）
echo -e "\n是否包含已抓取的数据和进度? (y/n) [默认: n]"
read -r INCLUDE_DATA
if [ "$INCLUDE_DATA" = "y" ]; then
    echo "[5/5] Copying data files..."
    if [ -d "data" ]; then
        cp -r data "$PACK_DIR/"
        echo "  ✓ Data included (断点续传)"
    else
        echo "  ⚠ data/ directory not found, skipping"
    fi
else
    echo "[5/5] Skipping data files..."
    echo "  ✓ Fresh start (全新开始)"
fi

# 4. 清理敏感信息
echo -e "\nCleaning sensitive files..."
rm -f "$PACK_DIR/.env"
echo "  ✓ Removed .env"

# 5. 创建配置模板
cat > "$PACK_DIR/.env.example" << 'EOF'
# Steam Crawler Configuration
# 请填入您的 Steam API Key

STEAM_API_KEY=YOUR_API_KEY_HERE
DATA_DIR=data
LOG_DIR=logs
REQUEST_TIMEOUT=10
MAX_RETRIES=3
RATE_LIMIT_DELAY=1.5
EOF

echo "  ✓ Created .env.example"

# 6. 压缩
echo -e "\nCompressing package..."
tar -czf "$PACK_NAME.tar.gz" -C "$PACK_DIR" .

# 7. 清理临时目录
rm -rf "$PACK_DIR"

# 完成
FILESIZE=$(du -sh "$PACK_NAME.tar.gz" | cut -f1)
echo ""
echo "====================================="
echo "Package created successfully!"
echo "====================================="
echo ""
echo "File: $PACK_NAME.tar.gz"
echo "Size: $FILESIZE"
echo ""
echo "Next steps:"
echo "  1. Copy $PACK_NAME.tar.gz to target machine"
echo "  2. Extract: tar -xzf $PACK_NAME.tar.gz"
echo "  3. Install: pip install -r requirements.txt"
echo "  4. Edit start_concurrent.sh to add your API Key"
echo "  5. Run: ./start_concurrent.sh"
echo ""

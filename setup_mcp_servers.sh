#!/bin/bash

# NeuroAgent Claude Code MCP 快速設置腳本
# AWS AI Agent Global Hackathon 2025

set -e

echo "🏥 NeuroAgent Claude Code MCP 設置開始..."
echo "⏰ 預計需要 10-15 分鐘完成"

# 檢查必要工具
echo "📋 檢查環境需求..."
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required. 請安裝 Node.js 18+"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python is required. 請安裝 Python 3.11+"; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "⚠️  AWS CLI not found. AWS Bedrock MCP will be installed but requires AWS CLI configuration."; }

# 創建 MCP 配置目錄
echo "📁 創建 MCP 配置目錄..."
mkdir -p ~/.config/claude-desktop
mkdir -p ./mcp-servers

# 1. 安裝 GitHub MCP Server (最高優先級)
echo "📦 安裝 GitHub MCP Server..."
cd ./mcp-servers
if [ ! -d "github" ]; then
  git clone https://github.com/shibdad/github-mcp-server.git github
fi
cd github
npm install
chmod +x start.sh index.js
echo "✅ GitHub MCP Server 安裝完成"
cd ..

# 2. 安裝 AWS Bedrock MCP Server
echo "📦 安裝 AWS Bedrock MCP Server..."
if [ ! -d "aws-bedrock" ]; then
  git clone https://github.com/aws-samples/sample-bedrock-mcp.git aws-bedrock
fi
cd aws-bedrock
python3 -m venv venv
./venv/bin/pip install uv
./venv/bin/uv sync --all-groups
echo "✅ AWS Bedrock MCP Server 安裝完成"
cd ..

# 3. 安裝 Filesystem MCP Server
echo "📦 安裝 Filesystem MCP Server..."
if [ ! -d "mcp-servers-official" ]; then
  git clone https://github.com/modelcontextprotocol/servers.git mcp-servers-official
fi
cd mcp-servers-official/src/filesystem
npm install
echo "✅ Filesystem MCP Server 安裝完成"
cd ../../../

# 4. 安裝 Claude Context (語義搜索)
echo "📦 安裝 Claude Context Server..."
if [ ! -d "claude-context" ]; then
  git clone https://github.com/zilliztech/claude-context.git claude-context
fi
cd claude-context
npm install
echo "✅ Claude Context Server 安裝完成"
cd ..

# 5. 安裝 Semgrep MCP (安全掃描)
echo "📦 安裝 Semgrep MCP Server..."
if [ ! -d "semgrep-mcp" ]; then
  git clone https://github.com/semgrep/mcp.git semgrep-mcp
fi
cd semgrep-mcp
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
echo "✅ Semgrep MCP Server 安裝完成"
cd ..

echo "🔧 生成 Claude Desktop 配置..."

# 生成 Claude Desktop 配置文件
cat > ~/.config/claude-desktop/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "github": {
      "command": "/bin/sh",
      "args": ["-c", "$(pwd)/mcp-servers/github/start.sh"],
      "env": {
        "GITHUB_TOKEN": "your-github-token-here"
      }
    },
    "filesystem": {
      "command": "node",
      "args": ["$(pwd)/mcp-servers/mcp-servers-official/src/filesystem/index.js"],
      "env": {
        "ALLOWED_DIRECTORIES": ["$(pwd)"]
      }
    },
    "claude-context": {
      "command": "node", 
      "args": ["$(pwd)/mcp-servers/claude-context/dist/index.js"],
      "env": {
        "OPENAI_API_KEY": "your-openai-key-here"
      }
    },
    "aws-bedrock": {
      "command": "$(pwd)/mcp-servers/aws-bedrock/venv/bin/python",
      "args": ["-m", "chainlit", "run", "$(pwd)/mcp-servers/aws-bedrock/app.py"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "your-aws-key-here",
        "AWS_SECRET_ACCESS_KEY": "your-aws-secret-here"
      }
    },
    "semgrep": {
      "command": "$(pwd)/mcp-servers/semgrep-mcp/venv/bin/python",
      "args": ["$(pwd)/mcp-servers/semgrep-mcp/server.py"],
      "env": {
        "SEMGREP_API_TOKEN": "your-semgrep-token-here"
      }
    }
  }
}
EOF

echo "📝 配置設置指南..."
cat > MCP_SETUP_INSTRUCTIONS.md << 'EOF'
# MCP 設置完成後續步驟

## 🔑 必要的 API Keys 設置

### 1. GitHub Token
1. 前往 https://github.com/settings/tokens
2. 生成新的 personal access token
3. 權限選擇: repo, issues, pull_requests
4. 複製 token 並更新配置中的 `your-github-token-here`

### 2. AWS Credentials  
```bash
aws configure
# 輸入你的 AWS Access Key ID
# 輸入你的 AWS Secret Access Key
# 區域設為 us-east-1
```

### 3. OpenAI API Key (用於 Claude Context)
1. 前往 https://platform.openai.com/api-keys
2. 生成新的 API key
3. 更新配置中的 `your-openai-key-here`

### 4. Semgrep Token (可選，用於安全掃描)
1. 前往 https://semgrep.dev/manage/settings/tokens
2. 生成新的 token
3. 更新配置中的 `your-semgrep-token-here`

## 🧪 測試 MCP 整合

### 啟動 Claude Desktop
1. 重新啟動 Claude Desktop 應用程式
2. 開啟新對話
3. 測試指令：
   ```
   Index this codebase
   Check GitHub repository status
   List files in current directory
   Scan for security vulnerabilities
   ```

### 在 Claude Code 中測試
```bash
claude
> /explore backend/main.py
> Check GitHub issues for this repo
> Index this codebase for semantic search
> /plan "Setup Bedrock integration"
```

## 🚀 開發工作流程

### 每日開發啟動
```bash
cd neuroagent
claude
> Index this codebase
> Check latest GitHub issues and PRs
> /plan "Today's development tasks"
```

### 代碼提交流程
```bash
> /commit "Feature: Add neurological diagnosis engine"
> Create PR with descriptive title and body
> Run security scan on changed files
```

### 故障排除
- 如果 MCP server 無法連接，檢查路徑和權限
- 確保所有 API keys 都已正確設置
- 查看 Claude Desktop 的錯誤日誌
- 驗證網路連接和防火牆設置

EOF

cd $(pwd)

echo ""
echo "🎉 MCP 設置完成！"
echo ""
echo "📋 後續步驟："
echo "1. 設置 API keys (參見 MCP_SETUP_INSTRUCTIONS.md)"
echo "2. 重新啟動 Claude Desktop"
echo "3. 測試 MCP 整合功能"
echo ""
echo "⚡ Claude Code MAX 現在已準備好加速你的 NeuroAgent 開發！"
echo ""

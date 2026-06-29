#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> 启动 Python 虚拟环境"
source .venv/bin/activate

echo "==> 安装后端依赖"
pip install -r backend/requirements.txt

if [ ! -f backend/.env ]; then
  echo "==> 创建 backend/.env（请编辑 MySQL 密码）"
  cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env ]; then
  cp frontend/.env.example frontend/.env
fi

echo "==> 安装前端依赖（需要 Node.js）"
if command -v npm >/dev/null 2>&1; then
  cd frontend && npm install && cd ..
else
  echo "⚠️  未检测到 npm，请先安装 Node.js：https://nodejs.org/"
fi

echo ""
echo "✅ 项目依赖安装完成"
echo ""
echo "下一步："
echo "  1. 启动 MySQL 8，执行 scripts/init_mysql.sql（创建 zyxt 库）"
echo "  2. 导入实验 1-6 表结构与数据到 zyxt"
echo "  3. 执行 scripts/sql/04_advanced_objects.sql（索引/存储过程/触发器/用户）"
echo "  4. 编辑 backend/.env，确认 DB_NAME=zyxt 及密码正确"
echo "  5. cd backend && python manage.py runserver   # http://127.0.0.1:8000"
echo "  6. cd frontend && npm run dev                 # http://localhost:5173"

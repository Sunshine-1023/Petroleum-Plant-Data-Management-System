#!/bin/bash
# 同時啟動前後端開發伺服器（需先完成 MySQL 配置與 migrate）

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

echo "啟動後端 Django (http://127.0.0.1:8000) ..."
cd "$ROOT/backend" && source "$ROOT/.venv/bin/activate" && python manage.py runserver &
BACKEND_PID=$!

sleep 2

echo "啟動前端 Vite (http://localhost:5173) ..."
cd "$ROOT/frontend" && npm run dev &
FRONTEND_PID=$!

echo ""
echo "後端 PID: $BACKEND_PID | 前端 PID: $FRONTEND_PID"
echo "按 Ctrl+C 停止所有服務"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

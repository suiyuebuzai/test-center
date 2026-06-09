#!/bin/bash
set -e

echo "=== 等待 PostgreSQL 启动 ==="
until pg_isready -U postgres; do sleep 1; done

echo "=== 初始化数据库 ==="
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres createdb test_center 2>/dev/null || echo "test_center 已存在"
sudo -u postgres createdb test_center_test 2>/dev/null || echo "test_center_test 已存在"

echo "=== 创建 .env ==="
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_center
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_center_test
SECRET_KEY=codespaces-dev-secret-key-not-for-production-32chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

echo "=== 安装 Python 依赖 ==="
pip install -r requirements.txt

echo "=== 执行数据库迁移 ==="
alembic upgrade head

echo "=== 安装前端依赖 ==="
cd frontend && npm install

echo ""
echo "=== 环境就绪！启动命令 ==="
echo "后端: uvicorn app.main:app --reload --port 8000"
echo "前端: cd frontend && npm run dev -- --host"

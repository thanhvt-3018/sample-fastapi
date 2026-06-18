#!/bin/bash
set -e  # Dừng nếu có lỗi

echo "🔍 Running Ruff format check..."
ruff format app/

echo "🔍 Running Ruff lint check..."
ruff check app/

echo "🔍 Running mypy type check..."
mypy app/

echo "✅ All checks passed!"
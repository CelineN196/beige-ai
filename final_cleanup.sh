#!/bin/bash
set -e

echo "🔐 Securing .env"
if ! grep -qxF ".env" .gitignore 2>/dev/null; then
  echo -e "\n# Security\n.env" >> .gitignore
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "🚨 .env was tracked. Removing from git..."
  git rm --cached .env
fi

echo "📦 Organizing files"
mkdir -p tests/migration_verification docs/internal

shopt -s nullglob
mv verify_*.py test_*.py tests/migration_verification/ 2>/dev/null || true
mv *SUMMARY.md *STATUS.md *FIX.md docs/internal/ 2>/dev/null || true
shopt -u nullglob

echo "🧹 Final structure:"
ls -a

echo "🚀 Committing changes"
git add .

if git diff --cached --quiet; then
  echo "No changes to commit"
else
  git commit -m "chore: final cleanup, security hardening, architecture sync"
  git push || echo "⚠️ No remote set. Run: git push -u origin <branch>"
fi

echo "✅ Done"

#! /bin/bash

LEGACY_COMMIT=90d4bc152f5b19c5b237ff105c75c3f7305738eb

git diff $LEGACY_COMMIT --name-only --diff-filter=ACMRTUXB | \
  { grep -E -v "ghidra_scripts" || true; } | \
  { grep -E "\.py$" || true; } 

git diff $LEGACY_COMMIT --name-only --diff-filter=ACMRTUXB | \
  { grep -E "(\.yml$|\.yaml$)" || true ;} 
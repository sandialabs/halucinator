#! /bin/bash

LEGACY_COMMIT=90d4bc152f5b19c5b237ff105c75c3f7305738eb

git diff $LEGACY_COMMIT --name-only --diff-filter=ACMRTUXB | \
  { grep -E "\.py$" || true;} | \
  xargs -t --no-run-if-empty black

git diff $LEGACY_COMMIT --name-only --diff-filter=ACMRTUXB |
      { grep -E "(\.c$|\.cpp$|\.h$|\.hpp$)" || true; } | \
      xargs -t --no-run-if-empty clang-format-10 --style=webkit -Werror -i
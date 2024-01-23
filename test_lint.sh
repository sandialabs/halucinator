#! /bin/bash

LEGACY_COMMIT=90d4bc152f5b19c5b237ff105c75c3f7305738eb

git diff $LEGACY_COMMIT --name-only --diff-filter=ACMRTUXB | \
  { grep -E "\.py$" || true; } | \
  xargs -t --no-run-if-empty pylint

git diff $LEGACY_COMMIT --name-only --diff-filter=ACMRTUXB | \
  { grep -E "(\.yml$|\.yaml$)" || true ;} | \
  xargs -t --no-run-if-empty yamllint -s

# git diff $LEGACY_COMMIT --name-only --diff-filter=ACMRTUXB |
#       { grep -E "(\.c$|\.cpp$|\.h$|\.hpp$)" || true; } | \
#       xargs -I % -t --no-run-if-empty clang-tidy-11  % -- -Isrc/halucinator/drivers/include
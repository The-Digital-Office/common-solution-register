#!/usr/bin/env bash
#
# One-time setup for a repository created from The-Digital-Office/repository-template.
# Run by .github/workflows/template.yml; removes itself when done.
#
# Environment:
#   REPO             owner/name of the new repository (required)
#   OWNER_LOGIN      GitHub login of the person who created it (required)
#   MAINTAINER_NAME  that person's full name, if known (optional)
#   TODAY            date as YYYY-MM-DD (optional, defaults to today)

set -euo pipefail

: "${REPO:?REPO is required}"
: "${OWNER_LOGIN:?OWNER_LOGIN is required}"
TODAY=${TODAY:-$(date -u +%F)}
YEAR=${TODAY:0:4}
REPO_NAME=${REPO#*/}
REPO_URL="https://github.com/$REPO"
MAINTAINER_NAME=${MAINTAINER_NAME:-"TODO: maintainer's full name"}

# Escape a value for use as a sed replacement.
esc() { printf '%s' "$1" | sed -e 's/[\\&|]/\\&/g'; }

render() {
  sed -i \
    -e "s|{{REPO_NAME}}|$(esc "$REPO_NAME")|g" \
    -e "s|{{REPO_URL}}|$(esc "$REPO_URL")|g" \
    -e "s|{{DATE}}|$(esc "$TODAY")|g" \
    -e "s|{{MAINTAINER_NAME}}|$(esc "$MAINTAINER_NAME")|g" \
    "$@"
}

render README.md CHANGELOG.md publiccode.yml

# Remove the note that only makes sense in the template itself.
sed -i '/<!-- template-only:start -->/,/<!-- template-only:end -->/d' README.md

# The person who created the repository becomes its code owner.
cat > .github/CODEOWNERS <<CODEOWNERS
# Code owners are requested for review on every pull request.
# Add a second maintainer on the same line if there is one, e.g.
#   * @first-maintainer @second-maintainer
* @$OWNER_LOGIN
CODEOWNERS

sed -i -E "s/^Copyright \(c\) [0-9]{4} /Copyright (c) $YEAR /" LICENSE

# Prepare the follow-up issue before this directory is removed.
render .github/template/setup-issue.md
cp .github/template/setup-issue.md "${RUNNER_TEMP:-/tmp}/setup-issue.md"

rm -rf .github/template

if leftovers=$(grep -rn --exclude-dir=.git '{{[A-Z_]*}}' .); then
  echo "Unrendered placeholders remain:" >&2
  echo "$leftovers" >&2
  exit 1
fi

echo "Setup complete for $REPO."

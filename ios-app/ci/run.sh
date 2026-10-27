#!/bin/bash
# run.sh <label> <command...>: runs a command, and on failure turns the useful log lines into GitHub annotations.
label=$1; shift
log="$RUNNER_TEMP/$label.log"
set +e; set +o pipefail
"$@" 2>&1 | tee "$log"
st=${PIPESTATUS[0]}
if [ "$st" -ne 0 ]; then
  { grep -E "error:|error -|ERROR|Error |failed|No profile|No signing|requires a provisioning|Code Signing" "$log" | grep -v "^note:" | tail -25; } > "$log.err"
  [ -s "$log.err" ] || tail -20 "$log" > "$log.err"
  while IFS= read -r l; do echo "::error title=$label::${l:0:600}"; done < "$log.err"
fi
exit "$st"

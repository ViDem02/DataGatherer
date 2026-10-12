#!/bin/bash
# Double-click in Finder to stop DataGatherer. Your data is kept.
cd "$(dirname "$0")" && ./stop.sh
echo
read -r -p "Press Enter to close this window."

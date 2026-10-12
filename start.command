#!/bin/bash
# Double-click in Finder to start DataGatherer.
cd "$(dirname "$0")" && ./start.sh
echo
read -r -p "Press Enter to close this window."

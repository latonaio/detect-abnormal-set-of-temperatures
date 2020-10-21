#!/bin/sh

python3 -m detect-abnormal-temps
/bin/sh -c "sleep 3"
curl -s -X POST localhost:10001/quitquitquit

#!/bin/bash
base=`pwd`
echo $base
file=server_app/test.env
echo $file
sed -i ".env" "s/dataset/$base/" "$file"
sed -i ".env" "s/logs/logs/" "$file"
cat server_app/test.env

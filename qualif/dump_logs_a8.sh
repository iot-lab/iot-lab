#!/bin/bash

logsdir=${*:-faillogs}

STEP() {
	txt=$1
	cmd=$2

	input=`sed 's: :/* :g' <<< "$logsdir "`
	res=`cat $input | eval $cmd \
		| sort -t '-' -k 3 -k 2 -n | uniq -c`
	txt="$txt: "`wc -l <<< "$res"`
	sep=${txt//?/=}
	echo "$sep"
	echo "$txt"
	echo "$sep"
	echo "$res"
}

STEP "Failed ssh to ok nodes" \
	"grep ssh | awk -F : '{print \$1}'"

STEP "Failed nodes" \
	"grep -v ssh | awk -F : '{print \$1}'"

STEP "Failures details" \
	'awk "/::/ {\$2=\$3=\$4=\$5=\$6=\"\"; print; next} {print}"'

# example usage with post-processing:
# ./dump_logs_a8.sh | grep FTDI | awk -F '[ .-]+' '{print $4}' | sort -nu | xargs echo
# ./dump_logs_a8.sh | grep ssh  | awk -F '[ .-]+' '{print $5}' | sort -nu | xargs echo

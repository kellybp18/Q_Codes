#/bin/bash
#
var=$(pwd)
infile=$var'/temp.txt'
#
count=0
while read line; do
	count=$count+1
	if [[ $count -eq 1 ]]
	then
		stn=$line
	elif [[ $count -eq 2 ]]
	then
		ofile=$line
		sgftops $var'/'$ofile $var'/Fig.'$stn'_11Spec.ps'
	elif [[ $count -eq 3 ]]
	then
		ofile=$line
		sgftops $var'/'$ofile $var'/Fig.'$stn'Gram.ps'
	elif [[ $count -eq 4 ]]
	then
		ofile=$line
		sgftops $var'/'$ofile $var'/Fig.'$stn'MAmp.ps'
	elif [[ $count -eq 5 ]]
	then
		ofile=$line
		sgftops $var'/'$ofile $var'/Fig.'$stn'Spec.ps'
	fi
done < $infile
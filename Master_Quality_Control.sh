#/bin/bash
#
cd /Volumes/External/Attenuation
infile='event_directories.txt'
counter=0
for (( i = 1 ; i < 24 ; i++ )) ; do
	if [[ $i -lt 10 ]]
	then
		if [[ $i -eq 1 ]]
		then
			stnname="IL01"
			eval $stnname=0
		else
			stnname="IL0${i}"
			eval $stnname=0
		fi
	else
		stnname="IL${i}"
		eval $stnname=0
	fi
done
#
while read line; do
	counter=$counter+1
	if [[ $counter -le 355 ]]
	then
		cd $line
		ls I*.out > temp1.txt
		infile2="temp1.txt"
		while read line2; do
			Stn=$(echo $line2 | tr -s ' ' | cut -f1 -d'.')
			rawQs=$(grep "t7: " $line2 | tr -s ' ' | cut -f7 -d' ')
			Qsval=$(echo $rawQs | tr -d 'e' | cut -f1 -d'+')
			Qsexp=$(echo $rawQs | tr -d 'e' | cut -f2 -d'+')
			Qs=$(echo "scale=0; $Qsval*(10^($Qsexp))/1" | bc -l)
			if [[ $Qs -lt 75 ]] || [[ $Qs -gt 1500 ]]
			then
				eval $Stn=$Stn+1
			fi
		done < $infile2
	fi
done < $infile
#
for (( i = 1 ; i < 24 ; i++ )) ; do
	if [[ $i -lt 10 ]]
	then
		if [[ $i -eq 1 ]]
		then
			stnname="IL01"
			echo "$stnname ${$stnname}"
		else
			stnname="IL0${i}"
			eval $stnname=0
		fi
	else
		stnname="IL${i}"
		eval $stnname=0
	fi
done
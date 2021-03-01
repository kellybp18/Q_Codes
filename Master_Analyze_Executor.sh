#/bin/bash
#
cd /Volumes/External/Attenuation
ls -d 1* > event_directories.txt
infile='event_directories.txt'
counter=0
read -sp "There are 10 event subsets for 710 total events. Which would you like to prep?" subset
ending=$(echo "scale=0; 710*$subset/10" | bc -l)
start=$(echo "scale=0; $ending-70" | bc -l)
echo "Prepping subset $subset, events $start to $ending"
while read line; do
	counter=$counter+1
	if [[ $counter -ge $start && $counter -le $ending ]]
	then
		if [[ $counter -eq $start ]]
		then
			echo $line > event_subset.txt
		else
			echo $line >> event_subset.txt
		fi
	fi
done < $infile
counter=0
infile2="event_subset.txt"
while read line2; do
	cd $line2
	for (( i = 1 ; i < 24 ; i++ )) ; do
		if [[ $i -lt 10 ]]
		then
			if [[ $i -eq 1 ]]
			then
				stnname="il01*"
				ls -m $stnname | tr ", " " " > stnlist.txt
			else
				stnname="il0${i}*"
				ls -m $stnname | tr ", " " " >> stnlist.txt
			fi
		else
			stnname="il${i}*"
			ls -m $stnname | tr ", " " " >> stnlist.txt
		fi
	done
	infile3="stnlist.txt"
	counter=$counter+1
	if [[ $counter -eq 1 ]]
	then
		echo "cd $line2" > /Volumes/External/Attenuation/superanalyze.m
	else
		echo "cd $line2" >> /Volumes/External/Attenuation/superanalyze.m
	fi
	while read line3; do
		east=$(echo $line3 | cut -f1 -d' ')
		north=$(echo $line3 | cut -f2 -d' ')
		vert=$(echo $line3 | cut -f3 -d' ')
		echo "m /Volumes/External/Data/Q_Codes/multiq2.m fz $vert fh1 $north fh2 $east pick no" >> /Volumes/External/Attenuation/superanalyze.m
	done < $infile3
	echo "cd .." >> /Volumes/External/Attenuation/superanalyze.m
	cd ..
done < $infile2		
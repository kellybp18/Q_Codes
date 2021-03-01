#/bin/bash
#
cd /Volumes/External/Attenuation
ls -d 1* > event_directories.txt
infile='event_directories.txt'
counter=0
while read line; do
	counter=$counter+1
	cd $line
	if [[ $counter -eq 1 ]]
	then
		echo "cd $line" > /Volumes/External/Attenuation/superprep.m
		cat prep.m >> /Volumes/External/Attenuation/superprep.m
		echo "cd .." >> /Volumes/External/Attenuation/superprep.m
	else
		echo "cd $line" >> /Volumes/External/Attenuation/superprep.m
		cat prep.m >> /Volumes/External/Attenuation/superprep.m
		echo "cd .." >> /Volumes/External/Attenuation/superprep.m
	fi
	cd ..
done < $infile
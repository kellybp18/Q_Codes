#/bin/bash
#
cd /Volumes/External/Data
ls -d service* > directories.txt
ls -d demob >> directories.txt
mkdir -p /Volumes/External/Data/Master_Data
mkdir -p /Volumes/External/Data/Master_Data/Y2015
mkdir -p /Volumes/External/Data/Master_Data/Y2016
infile='directories.txt'
while read line; do
	cd $line
	cd MSEED
	ls -d Y* > temp2.txt
	infile2='temp2.txt'
	while read line2; do
		cd $line2
		ls -d R* > temp3.txt
		infile3='temp3.txt'
		while read line3; do
			cd $line3
			ls -d 1* > temp4.txt
			infile4='temp4.txt'
			while read line4; do
				cd $line4
				dir="/Volumes/External/Data/Master_Data/${line2}/${line3}"
				mkdir -p $dir
				dir2="/Volumes/External/Data/Master_Data/${line2}/${line3}/${line4}"
				mkdir -p $dir2
				mv * $dir2
				cd ..
			done < $infile4
			rm temp4.txt
			cd ..
		done < $infile3
		rm temp3.txt
		cd ..
	done < $infile2
	rm temp2.txt
	cd ..
	cd ..
done < $infile
rm directories.txt
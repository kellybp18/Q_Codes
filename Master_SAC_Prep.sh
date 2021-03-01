#/bin/bash
#
#Master_SAC_Prep pulls event info from velo_vs_dist_mag4.txt, makes event folders in the 
#/Volumes/External/Attenuation directory, moves the relevant SAC hour files for an event
#to its folder, and writes a SAC macro, prep.m, tailored to prepare those sac files for
#each event for analysis by multiq2.m
#
#FOR FUTURE ITERATIONS: USING LASTSTN TO DETERMINE FIRSTP IS BAD PRACTICE, CHECK 
#LAT/LON/DEP INSTEAD
#
#10/12/2020
#
infile='velo_vs_dist_mag4.txt'
#
lastStn="00"
stnnum="00"
lastWave=""
pcounter=0
while read line; do
	pors=$(echo $line | tr -s ' ' | cut -f4 -d' ')
	if [[ $pors = 'P' ]]
	then
		Pyr=$(echo $line | tr -s ' ' | cut -f13 -d' ')
#		if [[ $Pyr -eq 2016 ]]
#		then
			Pdy=$(echo $line | tr -s ' ' | cut -f14 -d' ')
#			if [[ $Pdy -gt 7 && $Pdy -lt 32 ]]
#			then
				pcounter=$pcounter+1
				vp=$(echo $line | tr -s ' ' | cut -f2 -d' ')
				lat=$(echo $line | tr -s ' ' | cut -f5 -d' ')
				lon=$(echo $line | tr -s ' ' | cut -f6 -d' ')
				dep=$(echo $line | tr -s ' ' | cut -f7 -d' ')
				Oyr=$(echo $line | tr -s ' ' | cut -f8 -d' ')
				Ody=$(echo $line | tr -s ' ' | cut -f9 -d' ')
				Ohr=$(echo $line | tr -s ' ' | cut -f10 -d' ')
				Omin=$(echo $line | tr -s ' ' | cut -f11 -d' ')
				Osec=$(echo $line | tr -s ' ' | cut -f12 -d' ')
				Phr=$(echo $line | tr -s ' ' | cut -f15 -d' ')
				Pmin=$(echo $line | tr -s ' ' | cut -f16 -d' ')
				Psec=$(echo $line | tr -s ' ' | cut -f17 -d' ')
				Stn=$(echo $line | tr -s ' ' | cut -f18 -d' ')
				mag=$(echo $line | tr -s ' ' | cut -f19 -d' ')
				stnnum=$(echo $Stn | cut -f2 -d"L")
				if [[ $lastWave = 'P' ]]
				then
					echo "cut off" >> prep.m
				fi
				if [[ ${lastStn#0} -gt ${stnnum#0}  ||  $pcounter -eq 1 ]]
				then
					firstp=1
				else
					firstp=0
				fi
				datadir="/Volumes/External/Data/Master_Data/Y${Pyr}"
				cd $datadir
				if [[ $(echo ${#Pdy}) -eq 1 ]]
				then
					efolder="R00${Pdy}.01"
					cd $efolder
					shortyr=$(echo $Pyr | cut -f2 -d'0')
					julian="${shortyr}00${Pdy}"
				elif [[ $(echo ${#Pdy}) -eq 2 ]]
				then
					efolder="R0${Pdy}.01"
					cd $efolder
					shortyr=$(echo $Pyr | cut -f2 -d'0')
					julian="${shortyr}0${Pdy}"
				else
					efolder="R${Pdy}.01"
					cd $efolder
					shortyr=$(echo $Pyr | cut -f2 -d'0')
					julian="${shortyr}${Pdy}"
				fi
				cd $julian
				newdir="/Volumes/External/Attenuation/${julian}_${Ohr}_${Omin}_${Osec}"
				mkdir -p $newdir
				nextday=0
				prevday=0
				nexthour=0
				lasthour=0
				copy=""
				copyE=""
				copyN=""
				copyZ=""
				copy2E=""
				copy2N=""
				copy2Z=""
				mergevar=0
				omarker=0
				tzero=0
				tone=0
				ttwo=0
				if [[ $Stn = 'IL01' ]]
				then
					Stn="IL12"
				elif [[ $Stn = 'IL17' ]]
				then
					Stn="IL23"
				fi
				if [[ $(echo ${#Phr}) -eq 1 ]]
				then
					if [[ $Pmin -ge 58 || $Pmin -eq 0 ]]
					then
						if [[ $Pmin -ge 58 ]]
						then
							copyE="0${Phr}.00.00.${Stn}.bhe.sac"
							copyN="0${Phr}.00.00.${Stn}.bhn.sac"
							copyZ="0${Phr}.00.00.${Stn}.bhz.sac"
							cp $copyE $copyN $copyZ $newdir
							nexthour=$(echo "$Phr+1" | bc -l)
							if [[ $Phr -eq 9 ]]
							then
								copy2E="${nexthour}.00.00.${Stn}.bhe.sac"
								copy2N="${nexthour}.00.00.${Stn}.bhn.sac"
								copy2Z="${nexthour}.00.00.${Stn}.bhz.sac"
								cp $copy2E $copy2N $copy2Z $newdir
							else
								copy2E="0${nexthour}.00.00.${Stn}.bhe.sac"
								copy2N="0${nexthour}.00.00.${Stn}.bhn.sac"
								copy2Z="0${nexthour}.00.00.${Stn}.bhz.sac"
								cp $copy2E $copy2N $copy2Z $newdir
							fi
						elif [[ $Pmin -eq 0 ]]
						then
							if [[ $Phr -eq 0 ]]
							then
								copy2E="00.00.00.${Stn}.bhe.sac"
								copy2N="00.00.00.${Stn}.bhn.sac"
								copy2Z="00.00.00.${Stn}.bhz.sac"
								cp $copy2E $copy2N $copy2Z $newdir
								cd ..
								cd ..
								prevday=$(echo "$Pdy-1" | bc -l)
								if [[ $(echo ${#prevday}) -eq 1 ]]
								then
									efolder2="R00${prevday}.01"
									innerfolder="1600${prevday}"
								elif [[ $(echo ${#prevday}) -eq 2 ]]
								then
									efolder2="R0${prevday}.01"
									innerfolder="160${prevday}"
								else
									efolder2="R${prevday}.01"
									innerfolder="16${prevday}"
								fi
								cd $efolder2
								cd $innerfolder
								copyE="23.00.00.${Stn}.bhe.sac"
								copyN="23.00.00.${Stn}.bhn.sac"
								copyZ="23.00.00.${Stn}.bhz.sac"
								cp $copyE $copyN $copyZ $newdir
							else
								copy2E="0${Phr}.00.00.${Stn}.bhe.sac"
								copy2N="0${Phr}.00.00.${Stn}.bhn.sac"
								copy2Z="0${Phr}.00.00.${Stn}.bhz.sac"
								cp $copy2E $copy2N $copy2Z $newdir
								lasthour=$(echo "$Phr-1" | bc -l)
								copyE="0${lasthour}.00.00.${Stn}.bhe.sac"
								copyN="0${lasthour}.00.00.${Stn}.bhn.sac"
								copyZ="0${lasthour}.00.00.${Stn}.bhz.sac"
								cp $copyE $copyN $copyZ $newdir
							fi
						else
							copy="0${Phr}.00.00.${Stn}.*"
							cp $copy $newdir
						fi
					else
						copy="0${Phr}.00.00.${Stn}.*"
						cp $copy $newdir
					fi
				elif [[ $(echo ${#Phr}) -eq 2 ]]
				then
					if [[ $Pmin -ge 58 || $Pmin -eq 0 ]]
					then
						if [[ $Pmin -ge 58 ]]
						then
							if [[ $Phr -eq 23 ]]
							then
								copyE="23.00.00.${Stn}.bhe.sac"
								copyN="23.00.00.${Stn}.bhn.sac"
								copyZ="23.00.00.${Stn}.bhz.sac"
								cp $copyE $copyN $copyZ $newdir
								cd ..
								cd ..
								nextday=$(echo "$Pdy+1" | bc -l)
								if [[ $(echo ${#nextday}) -eq 1 ]]
								then
									efolder2="R00${nextday}.01"
									innerfolder="1600${nextday}"
								elif [[ $(echo ${#nextday}) -eq 2 ]]
								then
									efolder2="R0${nextday}.01"
									innerfolder="160${nextday}"
								else
									efolder2="R${nextday}.01"
									innerfolder="16${nextday}"
								fi
								cd $efolder2
								cd $innerfolder
								copy2E="00.00.00.${Stn}.bhe.sac"
								copy2N="00.00.00.${Stn}.bhn.sac"
								copy2Z="00.00.00.${Stn}.bhz.sac"
								cp $copy2E $copy2N $copy2Z $newdir
							else
								copyE="${Phr}.00.00.${Stn}.bhe.sac"
								copyN="${Phr}.00.00.${Stn}.bhn.sac"
								copyZ="${Phr}.00.00.${Stn}.bhz.sac"
								cp $copyE $copyN $copyZ $newdir
								nexthour=$(echo "$Phr+1" | bc -l)
								copy2E="${nexthour}.00.00.${Stn}.bhe.sac"
								copy2N="${nexthour}.00.00.${Stn}.bhn.sac"
								copy2Z="${nexthour}.00.00.${Stn}.bhz.sac"
								cp $copy2E $copy2N $copy2Z $newdir
							fi
						elif [[ $Pmin -eq 0 ]]
						then
							copy2E="${Phr}.00.00.${Stn}.bhe.sac"
							copy2N="${Phr}.00.00.${Stn}.bhn.sac"
							copy2Z="${Phr}.00.00.${Stn}.bhz.sac"
							cp $copy2E $copy2N $copy2Z $newdir
							lasthour=$(echo "$Phr-1" | bc -l)
							if [[ $Phr -eq 10 ]]
							then
								copyE="0${lasthour}.00.00.${Stn}.bhe.sac"
								copyN="0${lasthour}.00.00.${Stn}.bhn.sac"
								copyZ="0${lasthour}.00.00.${Stn}.bhz.sac"
								cp $copyE $copyN $copyZ $newdir
							else
								copyE="${lasthour}.00.00.${Stn}.bhe.sac"
								copyN="${lasthour}.00.00.${Stn}.bhn.sac"
								copyZ="${lasthour}.00.00.${Stn}.bhz.sac"
								cp $copyE $copyN $copyZ $newdir
							fi
						else
							copy="${Phr}.00.00.${Stn}.*"
							cp $copy $newdir
						fi
					else
						copy="${Phr}.00.00.${Stn}.*"
						cp $copy $newdir
					fi
				fi
				cd $newdir
				if [[ $copy2E = "" ]]
				then
					mergevar=0
				else
					mergevar=1
				fi
				if [[ $mergevar -eq 0 && $firstp -eq 1 ]]
				then
					if [[ $Stn = 'IL05' && $julian -lt 16204 ]]
					then
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec-1" | bc -l)
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					else
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec" | bc -l)
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					fi
					echo "rh *.sac" > prep.m
					echo "ch evla $lat" >> prep.m
					echo "ch evlo $lon" >> prep.m
					echo "ch evdp $dep" >> prep.m
					echo "ch evel $mag" >> prep.m
					echo "wh" >> prep.m
					echo "m /Volumes/External/Data/Q_Codes/cmp.m" >> prep.m
					echo "wh" >> prep.m
					echo "r *${Stn}*" >> prep.m
					echo "ch o $omarker" >> prep.m
					echo "ch t0 $tzero" >> prep.m
					echo "wh" >> prep.m
					echo "cut t0 -60 100" >> prep.m
					echo "r *${Stn}*" >> prep.m
					echo "ch a $amarker" >> prep.m
					echo "ch f $fmarker" >> prep.m
					echo "ch t1 $tone" >> prep.m
					echo "ch t2 $ttwo" >> prep.m
				elif [[ $mergevar -eq 0 && $firstp -eq 0 ]]
				then
					if [[ $Stn = 'IL05' && $julian -lt 16204 ]]
					then
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec-1" | bc -l)
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					else
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec" | bc -l)
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					fi
					echo "r *${Stn}*" >> prep.m
					echo "ch o $omarker" >> prep.m
					echo "ch t0 $tzero" >> prep.m
					echo "wh" >> prep.m
					echo "cut t0 -60 100" >> prep.m
					echo "r *${Stn}*" >> prep.m
					echo "ch a $amarker" >> prep.m
					echo "ch f $fmarker" >> prep.m
					echo "ch t1 $tone" >> prep.m
					echo "ch t2 $ttwo" >> prep.m
				elif [[ $mergevar -eq 1 && $firstp -eq 0 ]]
				then
					if [[ $Stn = 'IL05' && $julian -lt 16204 ]]
					then
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec-1" | bc -l)
						if [[ $Pmin -eq 0 && $Pmin -eq $Omin ]]
						then
							omarker=$(echo "scale=3; $omarker+3600" | bc -l)
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						elif [[ $Pmin -eq 0 && $Pmin -ne $Omin ]]
						then
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						fi
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					else
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec" | bc -l)
						if [[ $Pmin -eq 0 && $Pmin -eq $Omin ]]
						then
							omarker=$(echo "scale=3; $omarker+3600" | bc -l)
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						elif [[ $Pmin -eq 0 && $Pmin -ne $Omin ]]
						then
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						fi
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					fi
					echo "r $copyE" >> prep.m
					echo "merge $copy2E" >> prep.m
					echo "w ${Stn}merged.bhe.sac" >> prep.m
					echo "r $copyN" >> prep.m
					echo "merge $copy2N" >> prep.m
					echo "w ${Stn}merged.bhn.sac" >> prep.m
					echo "r $copyZ" >> prep.m
					echo "merge $copy2Z" >> prep.m
					echo "w ${Stn}merged.bhz.sac" >> prep.m
					echo "r *${Stn}merged*" >> prep.m
					echo "ch o $omarker" >> prep.m
					echo "ch t0 $tzero" >> prep.m
					echo "wh" >> prep.m
					echo "cut t0 -60 100" >> prep.m
					echo "r *${Stn}merged*" >> prep.m
					echo "ch a $amarker" >> prep.m
					echo "ch f $fmarker" >> prep.m
					echo "ch t1 $tone" >> prep.m
					echo "ch t2 $ttwo" >> prep.m
				elif [[ $mergevar -eq 1 && $firstp -eq 1 ]]
				then
					if [[ $Stn = 'IL05' && $julian -lt 16204 ]]
					then
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec-1" | bc -l)
						if [[ $Pmin -eq 0 && $Pmin -eq $Omin ]]
						then
							omarker=$(echo "scale=3; $omarker+3600" | bc -l)
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						elif [[ $Pmin -eq 0 && $Pmin -ne $Omin ]]
						then
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						fi
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					else
						omarker=$(echo "scale=3; ($Omin*60)+$Osec" | bc -l)
						tzero=$(echo "scale=3; ($Pmin*60)+$Psec" | bc -l)
						if [[ $Pmin -eq 0 && $Pmin -eq $Omin ]]
						then
							omarker=$(echo "scale=3; $omarker+3600" | bc -l)
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						elif [[ $Pmin -eq 0 && $Pmin -ne $Omin ]]
						then
							tzero=$(echo "scale=3; $tzero+3600" | bc -l)
						fi
						amarker=$(echo "scale=3; $tzero-10" | bc -l)
						fmarker=$(echo "scale=3; $tzero-8" | bc -l)
						tone=$(echo "scale=3; $tzero+1" | bc -l)
						ttwo=$(echo "scale=3; $tzero+2" | bc -l)
					fi
					echo "rh *.sac" > prep.m
					echo "ch evla $lat" >> prep.m
					echo "ch evlo $lon" >> prep.m
					echo "ch evdp $dep" >> prep.m
					echo "ch evel $mag" >> prep.m
					echo "wh" >> prep.m
					echo "m /Volumes/External/Data/Q_Codes/cmp.m" >> prep.m
					echo "wh" >> prep.m
					echo "r $copyE" >> prep.m
					echo "merge $copy2E" >> prep.m
					echo "w ${Stn}merged.bhe.sac" >> prep.m
					echo "r $copyN" >> prep.m
					echo "merge $copy2N" >> prep.m
					echo "w ${Stn}merged.bhn.sac" >> prep.m
					echo "r $copyZ" >> prep.m
					echo "merge $copy2Z" >> prep.m
					echo "w ${Stn}merged.bhz.sac" >> prep.m
					echo "r *${Stn}merged*" >> prep.m
					echo "ch o $omarker" >> prep.m
					echo "ch t0 $tzero" >> prep.m
					echo "wh" >> prep.m
					echo "cut t0 -60 100" >> prep.m
					echo "r *${Stn}merged*" >> prep.m
					echo "ch a $amarker" >> prep.m
					echo "ch f $fmarker" >> prep.m
					echo "ch t1 $tone" >> prep.m
					echo "ch t2 $ttwo" >> prep.m
				fi
				lastWave=$pors
#			fi
#		fi
	elif [[ $pors = 'S' ]]
	then
		Syr=$(echo $line | tr -s ' ' | cut -f13 -d' ')
#		if [[ $Syr -eq 2016 ]]
#		then
			Sdy=$(echo $line | tr -s ' ' | cut -f14 -d' ')
#			if [[ $Sdy -gt 7 && $Sdy -lt 32 ]]
#			then
				vs=$(echo $line | tr -s ' ' | cut -f2 -d' ')
				lat=$(echo $line | tr -s ' ' | cut -f5 -d' ')
				lon=$(echo $line | tr -s ' ' | cut -f6 -d' ')
				dep=$(echo $line | tr -s ' ' | cut -f7 -d' ')
				Oyr=$(echo $line | tr -s ' ' | cut -f8 -d' ')
				Ody=$(echo $line | tr -s ' ' | cut -f9 -d' ')
				Ohr=$(echo $line | tr -s ' ' | cut -f10 -d' ')
				Omin=$(echo $line | tr -s ' ' | cut -f11 -d' ')
				Osec=$(echo $line | tr -s ' ' | cut -f12 -d' ')
				Shr=$(echo $line | tr -s ' ' | cut -f15 -d' ')
				Smin=$(echo $line | tr -s ' ' | cut -f16 -d' ')
				Ssec=$(echo $line | tr -s ' ' | cut -f17 -d' ')
				Stn=$(echo $line | tr -s ' ' | cut -f18 -d' ')
				mag=$(echo $line | tr -s ' ' | cut -f19 -d' ')
				stnnum=$(echo $Stn | cut -f2 -d"L")
				echo $lastWave $lastStn $stnnum
				if [[ $lastWave = 'P'  &&  ${lastStn#0} -eq ${stnnum#0} ]]
				then
					if [[ $Stn = 'IL05' && $julian -lt 16204 ]]
					then
						tthree=$(echo "scale=3; ($Smin*60)+$Ssec-1" | bc -l)
						if [[ $mergevar -eq 1 && $Smin -lt 10 ]]
						then
							tthree=$(echo "scale=3; $tthree+3600" | bc -l)
						fi
						tfour=$(echo "scale=3; $tthree+1" | bc -l)
						tfive=$(echo "scale=3; $tthree+2" | bc -l)
					else
						tthree=$(echo "scale=3; ($Smin*60)+$Ssec" | bc -l)
						if [[ $mergevar -eq 1 && $Smin -lt 10 ]]
						then
							tthree=$(echo "scale=3; $tthree+3600" | bc -l)
						fi
						tfour=$(echo "scale=3; $tthree+1" | bc -l)
						tfive=$(echo "scale=3; $tthree+2" | bc -l)
					fi
					echo "ch t3 $tthree" >> prep.m
					echo "ch t4 $tfour" >> prep.m
					echo "ch t5 $tfive" >> prep.m
					echo "synch" >> prep.m
					echo "w il${stnnum}.e il${stnnum}.n il${stnnum}.z" >> prep.m
					echo "cut off" >> prep.m
					if [[ $firstp -eq 1 ]]
					then
						vratio=$(echo "scale=5; ($vp/$vs)" | bc -l)
						ratiofile="${julian}_VpVs.txt"
						echo "$vratio $vs $Stn" > $ratiofile
					else
						vratio=$(echo "scale=5; ($vp/$vs)" | bc -l)
						ratiofile="${julian}_VpVs.txt"
						echo "$vratio $vs $Stn" >> $ratiofile
					fi
				elif [[ $lastWave = 'P'  &&  ${lastStn#0} -ne ${stnnum#0} ]]
				then
					echo "cut off" >> prep.m
				fi
				lastWave=$pors
#			fi
#		fi
	fi
	if [[ $pors = 'S' && ${lastStn#0} -gt ${stnnum#0} ]]
	then
		echo "False starting S at $Oyr $Ody $Ohr $Omin $Osec"
	else
		lastStn=$stnnum
	fi
done < $infile
	
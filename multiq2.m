* Multiq macro builds input and runs the Qs measurement program multiple
* times to produce a robust estimate of Qs from a suite of P and S wave
* measurement windows.  Uses SAC formatted amplitude-phase spectra of P and
* S waves from vertical and transverse seismograms and calculates seismic
* attenuation, Qs, for multiple P and S wave windows (limits set by
* user) via the spectral ratio method.  Two estimates of the Qs for
* the S/P spectral ratio are produced:  One based on the statistical
* mean of each individual Qs estimate produced during the code
* run, and a second produced by finding the slope of the best-fit
* line to the stacked (arithmetic sum in frequency domain, divided
* by the number of spectral ratios calculated for the P and S windows.
* The drop files generated contain info for the plots used to make
* the measurement and to verify the results.
*
* Assumes t0 header variable in file header set to begin of P wave window,
* t1 header variable set to minimum length of P wave window, and t2 header
* variable set to maximum length of P wave window.  These values chosen by
* user via plotpk interactive picking command.  Likewise, t3, t4, and t5
* header variables used to set time of S wave start, minimum, and maximum
* window length.  Header variables A and F used to set bounds of pre-signal
* noise window.  If these variables not set, then you are prompted.
*
* For 20 increasingly long intervals the spectral ratio code multispec.f
* is run to produce a new Qs estimate each time on a slightly different
* P and/or S wave window.  For each window, a single estimate of the Qs
* is saved for later estimation of statistical robustness (mean Qs for
* 100 estimates, plus standard deviation).  A stack (sum/total number of
* estimates) of the spectral amplitudes versus frequency is also
* constructed, to which a best-fit line corresponding to the same bounds
* of min and max frequency (user-defined via plotpk, and stored as header
* variable t7, t8) used for each single estimate of Qs, is used to find
* Qs of the summed and averaged set of spectral amplitudes vs. frequency.
* This summed Qs estimate can then be compared to the mean Qs of the
* individual measurements to get an idea of the effect of window length
* (indirectly related to phase multipathing, for example).
*
* Other parameters:
*    file xxxx - prefix to file names
*    plot yes - make SGF plot file and plot to screen
*    plot no - plot only to screen
*    pick [ yes | maybe ] - If yes, force re-picking of seismogram
*
* A standard in-line call command of the macro could be:
* m multiq2.m fz ev1.z fh1 ev1.n fh2 ev1.e pick yes
*
****   NOTE before opening any windows type the following command to get
*      proper windowing:
*
*      window 1 x 0.05 0.80 y 0.05 0.74
*
*      Then type 'bd xwindow' or 'bd sunwindow'.
****
* RMR April 1999
* 
* Modified to use SH window for S spectrum,
* RMR June 2000
* 
* Modified from qcalc_sh3.m to produce the multiple Qs estimates
* described above.
* RMR and VIM March 2003
*
$keys fz fh1 fh2 plot xlim pick
$default plot yes
$default xlim off
$default pick maybe
setbb pick $pick
message $fz $fh1 $fh2
qdp off
line solid increment off list standard
rh $fz
if &1,a eq UNDEFINED
   setbb pick yes
endif
if &1,t0 eq UNDEFINED
   setbb pick yes
endif
if &1,t3 eq UNDEFINED
   setbb pick yes
endif
if &1,kstnm eq A094
   rh $fz $fh1 $fh2
   ch kstnm IL05
   wh
endif
if %pick% eq yes
   message " "
   message "Pick P wave window [top trace] - t0 for window start time,"
   message "t1 for minimum P wave window limit; t2 for maximum P wave."
   message "window limit."
   message "Then pick SH wave window [bottom trace] - t3 for S wave begin"
   message "time, t4 for S wave minimum window length, and t5 for max"
   message "S wave window length."
   message "Finally, pick pre-signal noise window -"
   message "type A to begin window, F to end it."
   message " "
   r $fh1 $fh2 ; rotate to gcp ; w sac radial.sv transv.sh
   message "Hello"
   r $fz radial.sv transv.sh
   rmean; rtr; taper; bp bu co 0.3 40 np 2 p 2
   plotpk zero markall on; copyhdr from $fz a f t0 t1 t2 t3 t4 t5; wh
   if &1,t0 eq UNDEFINED
      $break
   endif
   setbb begP &1,t0& ; setbb Pmin &1,t1& ; setbb Pmax &1,t2&
   setbb begS &1,t3& ; setbb Smin &1,t4& ; setbb Smax &1,t5&
   setbb noise1 &1,a& ; setbb noise2 &1,f&
else
   r $fh1 $fh2 ; rotate to gcp ; w sac radial.sv transv.sh
   r $fz radial.sv transv.sh
   rmean; rtr; taper; bp bu co 0.3 40 np 2 p 2
   copyhdr from $fz a f t0 t1 t2 t3 t4 t5; wh
   setbb begP &1,t0& ; setbb Pmin &1,t1& ; setbb Pmax &1,t2&
   setbb begS &1,t3& ; setbb Smin &1,t4& ; setbb Smax &1,t5&
   setbb noise1 &1,a& ; setbb noise2 &1,f&
endif
*
setbb evtnm &1,kevnm&
*setbb edate &1,kzdate&
setbb elat &1,evla&
setbb elon &1,evlo&
setbb edep &1,evdp&
setbb emag &1,evel&
setbb slat &1,stla&
setbb slon &1,stlo&
setbb sname &1,kstnm&
setbb distkm &1,dist&
setbb gca &1,gcarc&
setbb azm &1,az&
setbb bazm &1,baz&
*
sc echo "%elat% %elon% %edep% %emag% %evtnm%" > qs.out
sc echo " " >> qs.out
sc echo "%sname% %slat% %slon% %distkm% %gca% %azm% %bazm%" >> qs.out
sc echo " " >> qs.out
sc echo "     Qs           t\*        sigma b       sigma m       chisq        begP         endP         begS         endS" >> qs.out
*
evaluate to Pinc (%Pmax - %Pmin) / 20.0 
evaluate to Sinc (%Smax - %Smin) / 20.0
message "Pinc: %Pinc% Sinc: %Sinc%"
*
setbb delta &1,delta&
evaluate to inctest %delta * 2.0
if %Pinc LT %inctest
   evaluate to Pinc %inctest
   evaluate to Pnlast (%Pmax - %Pmin) / %Pinc
else
   setbb Pnlast 20
endif
if %Sinc LT %inctest
   evaluate to Sinc %inctest
   evaluate to Snlast (%Smax - %Smin) / %Sinc
else
   setbb Snlast 20
endif
*
evaluate to icount %Snlast * %Pnlast
message "icount = %icount%"
*
* begin loop over P, S windows
*
mkdir /tmp/%sname%
do icountP from 1 to %Pnlast
*
   evaluate to endcutP ($icountP * %Pinc) + %Pmin
   cut %begP %endcutP
   r $fz ; taper ; fft womean
   w sac P.spec ; w alpha P.spec.a 
*   w alpha /tmp/%sname%/$icountP$.Pspec.a
   ch iftype itime ; w sac /tmp/P.spec
*
   do icountS from 1 to %Snlast
*
      message "Iteration:  $icountP$ $icountS$"
*
      evaluate to endcutS ($icountS * %Sinc) + %Smin
      message "endcutP: %endcutP% endcutS: %endcutS%"
      cut %begS %endcutS
      r transv.sh ; taper ; fft womean
      w sac S.spec ; w alpha S.spec.a
*      w alpha /tmp/%sname%/$icountS$.Sspec.a
      ch iftype itime ; w sac /tmp/S.spec
* 
      cut %noise1 %noise2
      r $fz ; taper ; fft womean ; w sac pnoise.spec
      r transv.sh ; fft womean ; w sac snoise.spec
      cut off
*
      r pnoise.spec snoise.spec
      ch t2 UNDEFINED t3 UNDEFINED kevnm "Noise Spectrum"
      wh
*
* Build input file for Q measurement program, then invoke it.
*
      sc cat /dev/null > /tmp/qcalc_drop
      sc echo "P.spec.a S.spec.a" >> /tmp/qcalc_drop
*
      sc /Volumes/External/Data/Q_Codes/multispec
      r /tmp/ratio.yy
      w alpha $icountP$.$icountS$.%sname%.asc
*
* After multispec produces the S/P spectral ratio file, we need to
* pick the bounds of frequency that we'll be using in this set of
* measurements for calculating the spectral slope (and t*, Qs).
* This is done interactively ONCE, at the start of the measurements.'
*
      if $icountP eq 1
*
         if $icountS eq 1
*
            message "Pick bounds of spectral slope - t7 for start t8 for end"
*
            cut 0 40.0
            r /tmp/ratio.yy
            cut off
            setbb begslope 3.0 ; setbb endslope 12.0
            r /tmp/ratio.yy ; ch t7 %begslope t8 %endslope ; w sac /tmp/ratio.yy
*
*			if %pick% eq yes
*
*            	plotpk
*
*            	setbb begslope &1,t7& ; setbb endslope &1,t8&
*            	r /tmp/ratio.yy ; ch t7 %begslope t8 %endslope ; w /tmp/ratio.yy
*
*			else
*
*			setbb begslope 4.0 ; setbb endslope 12.0
*			r /tmp/ratio.yy ; ch t7 %begslope t8 %endslope ; w /tmp/ratio.yy
*
*			endif
*            
            bd x sgf
            xvport 0.1 0.9; yvport 0.15 0.8
            cut 0 40.0
            r /tmp/ratio.yy
            p1
            cut off
*
         endif
*
         if $icountS ge 1
*
            r /tmp/ratio.yy ; ch t7 %begslope t8 %endslope ; w sac /tmp/ratio.yy
*
         endif
*
      endif
*
      if $icountP ge 2
*
         if $icountS ge 1
*
            r /tmp/ratio.yy ; ch t7 %begslope t8 %endslope ; w sac /tmp/ratio.yy
*
         endif
*
      endif
*
      if $icountP eq 1
*
         if $icountS eq 1
*
            sc cp /tmp/ratio.yy ratio.sum
*
            sc cp /tmp/P.spec /tmp/P.spec.sum
*
            sc cp /tmp/S.spec /tmp/S.spec.sum
*
         endif
*
      endif
*
* Sum the new spectral file and the previous spectral files.
* First, make it possible to ignore potential mismatched in
* number of points in files to be summed, and also their
* interpolation interval (delta).
*
      binoperr npts warning
      binoperr delta warning
*
      r ratio.sum
      message "Hello"
      addf /tmp/ratio.yy
      w over
*
      r P.spec
      ch iftype itime
      addf /tmp/P.spec.sum
      w /tmp/P.spec.sum
*
      r S.spec
      ch iftype itime
      addf /tmp/S.spec.sum
      w /tmp/S.spec.sum
*
* Next run multiqcalc on the individual spectral ratio file, ratio.yy,
* calculate t* and Qs from the slope of the spectral ratio between
* frequencies picked above (t7, t8), and save the results plus some
* statistical info from the line fitting to a new drop file, qs.out,
* which will hold the complete list of Qs and t* measurements we make
* on individual P and S wave windows.
*
      sc /Volumes/External/Data/Q_Codes/multiqcalc
*
      r /tmp/ratio.yl
      setbb tstar &/tmp/ratio.yl,user0&
      setbb qs &/tmp/ratio.yl,user1&
      setbb siga &/tmp/ratio.yl,user2&
      setbb sigb &/tmp/ratio.yl,user3&
      setbb chi2 &/tmp/ratio.yl,user4&
*
      sc echo "%qs% %tstar% %siga% %sigb% %chi2% %begP% %endcutP% %begS% %endcutS%" >> qs.out
*
* Check to see if we've done all the measurements, and if we have,
* divide the summed spectral ratios in file /tmp/ratio.sum by the
* total number of files we've summed; set up for the output plotting.
*
      if $icountP eq %Pnlast
*
         if $icountS eq %Snlast
*
            message "Calculating t*, Qs for summed spectra"
*
            r ratio.sum ; div %icount% ; w over
            sc cp ratio.sum /tmp/ratio.yy
*
            r /tmp/P.spec.sum ; div %icount% ; w over
            r /tmp/S.spec.sum ; div %icount% ; w over                      
*
            sc /Volumes/External/Data/Q_Codes/multiqcalc
*
            sc cp /tmp/ratio.yl ratio.yline_sum
*
         endif
*
      endif
*
      cut %begS %endcutS
      r transv.sh ; fft womean ; w /tmp/S.spec

   enddo
*
   cut %begP %endcutP
   r $fz ; fft womean ; w sac /tmp/P.spec
*
enddo
*
* If we're really done, find max value in the ratio.yy spectrum
* run qsmean to get the final Qs values.'
*
cut off
r /tmp/ratio.yy
markptp length 48 to t0
w %sname%.yy
w alpha %sname%.asc
*
r ratio.yline_sum
setbb ststar &ratio.yline_sum,user0&
setbb sqs &ratio.yline_sum,user1&
*
sc echo "t7:  %begslope% t8:  %endslope%  Summed Qs:  %sqs%  Summed tstar %ststar%" >> qs.out
sc cp qs.out %sname%.out
*
sc /Volumes/External/Data/Q_Codes/qsmean
sc cp qs.stats %sname%.stats
*
***********************************************************************
* Finally plot output.
*
* echo on
qdp off
if no ne $plot
  message "Generating plot..."
*  bd x sgf
endif
* Plot results of measurement.
* Panel 1:  Seismogram with P and S windows
message "Seismogram with P and S windows"
cut off
beginframe
vspace full; xvport 0.1 0.9; yvport 0.1 0.9
xlabel "&1,nzyear& &1,nzjday& &1,kztime& &1,evla&N &1,evlo&E &1,evdp&km &1,kstnm& BAZ: &1,baz& DEL: &1,gcarc&" location TOP size small
cut a -10 t5 +25
r $fz radial.sv transv.sh
fileid on
ylim all; p1
*if 'off' eq $xlim$
*   ylim all; m /Volumes/External/Data/Q_Codes/ttsac
*else
*   ylim all; m /Volumes/External/Data/Q_Codes/ttsac xlim $xlim$
*endif
cut off
endframe
pause
* Panel 2:  
message "P and S wave spectra"
beginframe
vspace full; xvport 0.05 0.95; yvport 0.1 0.9
picks off; xlabel off; fileid off
r ratio.sum
setbb id "&1,kzdate& &1,kstnm& Mean Spectrum"
plabel 1 on "%id%" p 0.28 0.85 size medium
plabel 2 on "Mean P Amplitude Spectrum:" p 0.22 0.78 size small
plabel 3 on "t0 %begP% t1 %Pmin% t2 %Pmax%" p 0.20 0.71 size tiny
plabel 4 on "Mean S Amplitude Spectrum:" p 0.55 0.78 size small
plabel 5 on "t3 %begS% t4 %Smin% t5 %Smax%" p 0.55 0.71 size tiny
* vspace 1.0
yvport 0.30 0.65
xlim 0 20.0
r /tmp/P.spec.sum pnoise.spec
xvport 0.20 0.45; line inc list 1 2; linlog; p2
* xvport 0.05 0.45; psp am linlog
xlim 0 20.0
r /tmp/S.spec.sum snoise.spec
xvport 0.55 0.80; line inc list 1 2; linlog; p2
* xvport 0.55 0.95; psp am linlog
xlim off
color off; linlin
endframe
pause 
* Panel 3:  
message "Log ratio of amplitude spectrum vs. frequency"
beginframe
xvport 0.1 0.9; yvport 0.15 0.8
plabel 1 on "%id%" p 0.36 0.85 size medium
plabel 4 off; plabel 5 off
r /tmp/ratio.yl
setbb tstar &1,user0&
setbb qs &1,user1&
plabel 2 on "t-star: %tstar%" p 0.25 0.22 size medium
plabel 3 on "Mean Qs: %qs%" p 0.25 0.18 size medium
xlabel "Frequency @(Hz@)" loc bottom size small
ylabel "Log ratio of amplitude spectrum" loc left size small
cut 0.01 40.0 
line list 1 1 3 increment
r ratio.sum /tmp/ratio.yl
picks on T8 vertical T9 vertical 
p2
endframe
pause
*
* Convert sgf files to .ps files
*
sc echo "%sname%" > temp.txt
ls *.sgf >> temp.txt
/Volumes/External/Data/Q_Codes/sgftops.sh
sc rm *.sgf
*
****************************************************************
* Clean up.
*
* sc /bin/rm -f /tmp/ratio.yy /tmp/ratio.yline /tmp/qcalc_drop /tmp/qcalc_line
*
* sc rm P.spec S.spec P.spec.a S.spec.a pnoise.spec snoise.spec
*
cut off
plabel 1 off; plabel 2 off; plabel 3 off; plabel 4 off; plabel 5 off
xlabel off; ylabel off
line solid list standard
*
unset bb begP endP begS endS Pmin Smin Pmax Smax noise1 noise2
unset bb delta tstar qs begslope endslope id pause pick
unset bb siga sigb chi2 Pnlast Snlast Pinc Sinc inctest icount
unset bb endcutP endcutS
bd x

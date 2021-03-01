C	Program qcalc.f						19 April 99
C
C	This program reads in SAC Formatted amplitude-phase spectra of P and S
C	waves from vertical seismograms and calculates seismic attenuation, Q,
C	via the spectral ratio method.
C
C	This program is the second of two which interact with SAC2000 to yield
C	Q.  First program is called specrat.f.
C
C	RMR Sept. 1998-Apr. 1999 to run with SAC2000.
C
C
	Dimension ryy(1025),ayy(1025),xfreq(1025),freqs(1025),yline(1025)
C
	Character*10 astnm
	Character*13 ofile, anomen, kevnm
	Character*16 ofile2
C
	max = 1025
	pi = 3.141592654
	tstar = 0.0
	slope = 0.0
	ofile = '/tmp/ratio.yy'
	ofile2 = '/tmp/ratio.yl'
C
C	Resume program after picking slope calculation window.
C	Get t7 and t8 - begin and end times of window markers - from
C	sac file.
C
	Call rsac1(ofile,ayy,nlen,begf,delta,max,nerr)
	Call getnhv('NPTS',ntot,nerr)
	Call getfhv('t7',fstart,nerr)
	Call getfhv('t8',fstop,nerr)
	Call getfhv('DELTA',delta,nerr)
C        Call getnhv('NZYEAR',nzyear,nerr)
C        Call getnhv('NZJDAY',nzjday,nerr)
C        Call getnhv('NZHOUR',nzhour,nerr)
C        Call getnhv('NZMIN',nzmin,nerr)
C        Call getnhv('NZSEC',nzsec,nerr)
C        Call getnhv('NZMSEC',nzmsec,nerr)
        Call getkhv('KSTNM',astnm,nerr)
        write(6,*) 'astnm =', astnm
C        Call getkhv('KEVNM',anomen,nerr)
	Call getfhv('USER2',tp,nerr)
	Call getfhv('USER3',ts,nerr)
	Call getfhv('USER4',aob2p,nerr)
c	Write(6,*) 'fstart = ',fstart,' fstop = ',fstop
C
C	Now, extract linear sloped region of spectral ratio from
C	ofile and find slope via linear least-squares.  First,
C	construct arrays that contain only frequency-log (amplitude
C	ratio) pairs we want.
C
	freq = 0.0
C
	Do 5 ijk = 1,ntot
		freq = freq + delta
		xfreq(ijk) = freq
5	Continue
C
	Do 10 i = 1,ntot
		If(xfreq(i).LE.fstart) Then
			imin1 = i
			freqmin1 = xfreq(i)
		Endif
		If(xfreq(i).LE.fstop) Then
			imin2 = i
			freqmin2 = xfreq(i)
		Endif
10	Continue
C
	Do 11 j = ntot,1,-1
c		write(6,*) xfreq(j)
		If(xfreq(j).GT.fstart) Then
			imax1 = j
			freqmax1 = xfreq(j)
		Endif
		If(xfreq(j).GT.fstop) Then
			imax2 = j
			freqmax2 = xfreq(j)
		Endif
11	Continue
C
c	write(6,*) 'freqmin1 = ',freqmin1,' freqmax1 = ',freqmax1
c	write(6,*) 'freqmin2 = ',freqmin2,' freqmax2 = ',freqmax2
C
	diff1 = fstart - freqmin1
	diff2 = freqmax1 - fstart
	diff3 = fstop - freqmin2
	diff4 = freqmax2 - fstop
C
	If(diff1.GE.diff2) Then
		nfirstfreq = imax1
	Else
		nfirstfreq = imin1
	Endif
C
	If(diff3.GE.diff4) Then
		nlastfreq = imax2
	Else
		nlastfreq = imin2
	Endif
C
	If(nlastfreq.GT.ntot) Then
		nlastfreq = ntot
	Endif
C
c	write(6,*) 'nfirstfreq = ',nfirstfreq,' nlastfreq = ',nlastfreq
C
	kcount = 0
C
	Do 20 n = nfirstfreq,nlastfreq
C
		kcount = kcount + 1
		ryy(kcount) = ayy(n)
		freqs(kcount) = xfreq(n)
c		write(6,*) ayy(n),freqs(kcount),ryy(kcount)
C
20	Continue
C
c	write(6,*) freqs(1),freqs(kcount)
C
C	Call fit subroutine to find slope and intercept.
C
        mwt = 0
        Call fit(freqs,ryy,kcount,sig,mwt,A,slope,siga,sigb,chi2,q)
C
C	Write best fit line to drop file.
C
	Open(unit = 3, file = '/tmp/qcalc_line')
C
	Do 30 kk = 1,kcount
		yline(kk) = slope * freqs(kk) + A
c		write(3,*) freqs(kk),yline(kk)
c		write(6,*) freqs(kk),yline(kk)
30	Continue
C
	Close(3)
C
	Write(6,*) 'Slope, intercept: ',slope, A
	Write(6,*) 'Standard deviation: ',sig
	Write(6,*) 'Slope probable uncertainty: ',siga
	Write(6,*) 'Intercept probable uncertainty: ',sigb
	Write(6,*) 'Chi squared: ',chi2
	Write(6,*) 'Goodness-of-fit: ',q
C
C	Calculate apparent t-star
C
	tstar = -slope/3.141592654
C
	Write(6,*) 'Apparent t-star: ',tstar
C
C	Calculate Q.
C
	qs = (ts - 4.0*tp/(3.0*aob2p))/tstar
C
	Write(6,*) 'Estimated Q =  ',qs
C
C	Write t-star and Q to sac output file /tmp/ratio.yline for
C	use in plotting results.
C
	Call newhdr
C	call setnhv("nvhdr", 7, nerr)
	Call setnhv('NPTS',ntot,nerr)
        Call setfhv('B',xfreq(nfirstfreq),nerr)
        Call setfhv('E',xfreq(kcount),nerr)
c       Call setihv('IFTYPE','ITIME',nerr)
        Call setlhv('LEVEN',.TRUE.,nerr)
	Call setfhv('T7',fstart,nerr)
	Call setfhv('T8',fstop,nerr)
	Call setfhv('DELTA',delta,nerr)
	Call setfhv('USER0',tstar,nerr)
	Call setfhv('USER1',qs,nerr)
	Call setfhv('USER2',siga,nerr)
	Call setfhv('USER3',sigb,nerr)
	Call setfhv('USER4',chi2,nerr)
	Call wsac0(ofile2,xfreq,yline,nerr)
C
C
C
	Stop
	End
C
C
C
C
C
C	Program fit						22 July 90
C
C	This program calculates slope and intercept, A, and B, respectively
C	for the ndata points, X and Y, by linear least-squares.  Uncertainties
C	siga and sigb are returned as are chisq and q (goodness-o-fit) if
C	standard deviations, sig, are available.  If not, set mwt = 0, for
C	equally weighted standard deviations (q returned as 1.0)  Ref. is
C	Numerical Recipes, P 508.
C
C
	Subroutine fit(X,Y,ndata,sig,mwt,A,B,siga,sigb,chi2,q)
C
	Dimension X(ndata), Y(ndata), sig(ndata)
C
C	Initialize sums to zero.
C
	sx = 0.0
	sy = 0.0
	st2 = 0.0
	B = 0.0
C
C	Accumulate sums.
C
	If(mwt.NE.0) Then
C
		ss = 0.0
		Do 10 I = 1,ndata
			wt = 1.0/(sig(I)**2)
			ss = ss + wt
			sx = sx + X(I)*wt
			sy = sy + Y(I)*wt
 10		Continue
C
	Else
C
		Do 20 I = 1,ndata
			sx = sx + X(I)
			sy = sy + Y(I)
 20		Continue
C
		ss = float(ndata)
C
	Endif
C
C
	sxoss = sx/ss
C
	If(mwt.NE.0) Then
C
		Do 30 I = 1,ndata
			t = (X(I) - sxoss)/sig(I)
			st2 = st2 + t*t
			B = B + t*Y(I)/sig(I)
 30		Continue
C
	Else
C
		Do 40 I = 1,ndata
			t = X(I) - sxoss
			st2 = st2 + t*t
			B = B + t*Y(I)
 40		Continue
C
	Endif
C
C	Solve for slope and intercept, statistical values.
C
	B = B/st2
	A = (sy - sx*B)/ss
C
	siga = sqrt((1.0 + sx*sx/(ss*st2))/ss)
	sigb = sqrt(1.0/st2)
C
C	Calculate chisq.
C
	chi2 = 0.0
C
C	For unweighted data evaluate typical sig using chi2, and adjust
C	the standard deviations.
C
	If(mwt.EQ.0) Then
C
		Do 50 I = 1,ndata
			chi2 = chi2 + (Y(I) - A - B*X(I))**2
 50		Continue
C
		q = 1.0
		fdata = float(ndata)
		sigdat = sqrt(chi2/(fdata - 2.0))
		siga = siga*sigdat
		sigb = sigb*sigdat
C
	Else
C
		Do 60 I = 1,ndata
		  chi2 = chi2 + ((Y(I) - A - B*X(I))/sig(I))**2
 60		Continue
C
C		q = gammq(0.5*(ndata - 2),0.5*chi2)
C
	Endif
C
C
C
	Return
	End

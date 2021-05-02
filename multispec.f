C	Program multispec.f					9 March 03
C
C	This program reads in SAC formatted amplitude-phase spectra of P and S
C	waves from vertical seismograms and calculates seismic attenuation, Q,
C	via the spectral ratio method.
C
C	This program is the first of two which interact with SAC2000 to yield
C	Q.  Second program is called multiqcalc.f.
C
C	RMR March 2003.
C
	Dimension dfa(2),begf(2),endf(2)
	Dimension z(11000,2),nx(2),xdummy(11000)
	Dimension yy(11000),ysend(11000),xsend(11000)
	Dimension xnew(11000),ynew(11000)
	Dimension xends(2),yends(2)
C
C	Double Precision dfa
C
	Integer io
	Integer julian
	Integer kwave
C
	Character*1 ajunk
	Character*4 kstnm, stn
	Character*5 ajulian
	Character*13 ofile
	Character*18 anomen
	Character*25 dropfile(2)
C
	anomen = 'S/P spec ratio'
	ofile = '/tmp/ratio.yy'
C
C	Open file dropped by complementary SAC macro qcalc.m.
C	This file is written in /tmp by the macro and includes the
C	name of the spectra file dropped by the macro.  Spectra file
C	name is data specific in order to save spectra for later figure
C	making.  Read file name.
C
	Open(unit=1,file='/tmp/qcalc_drop',status='old')
C
	Read(1,*) dropfile(1), dropfile(2)
C
	Close(1)
C
C	Now Open the spectra file pointed to by the macro drop file.
C	For clarity's sake, these are written by the macro in a subdirectory
C	of the working/data directory called `spectra'.
C
C	Parameters read in from the spectra file as follows:
C
C		df = sample interval of frequencies in the spectrum
C		begf = frequency of first point in spectrum (should be zero)
C		endf = last frequency in spectrum
C		omarker = time (sec) from origin to beginning of record
C		t0p = time (sec) from beginning of record to P
C		t1s = time (sec) from beginning of record to S
C		sdelta = sampling interval (sec) of original seismogram
C		nzyear,nzjday,nzhour,nzmin,nzsec,nzmsec:  origin time
C		kstnm:  station name
C		kwave = phase indicator
C		z(j,kwave) = data frequencies in the spectrum;
C				kwave = 1 for first phase (e.g., P)
C				kwave = 2 for second phase (e.g., S)
C
C
	Do 10 kwave = 1,2
C
		Open(unit = 2, file = dropfile(kwave))
		Rewind 2
C
		Read(2,11) df
c		Write(6,11) df
 11		Format(G15.7)
C
		dfa(kwave) = df
C
		Read(2,12) begf(kwave),endf(kwave),omarker,amarker
C		Write(6,12) begf(kwave),endf(kwave),omarker,amarker
 12		Format(4G15.7)
C
		Read(2,13) t0p,t0s
		Write(6,*) t0p
		Write(6,*) t0s
 13		Format(G15.5,37x,G8.5)
C
C		Read(2,13) t0s
C		Write(6,13) t0s
C
		Do 14 i = 1,7
			Read(2,*) garbage
C			Write(6,*) garbage
 14		Continue
C
		Read(2,37) dist
 37	    Format(G15.5)
C
		Read(2,*) sdelta
C		write(6,*) sdelta
C
		Read(2,*) garbage
		Read(2,*) garbage
C
		Read(2,15) nzyear,nzjday,nzhour,nzmin,nzsec
C		Write(6,15) nzyear,nzjday,nzhour,nzmin,nzsec
 15		Format(5I10)
C
		Read(2,16) nzmsec,npts
		Write(6,16) nzmsec,npts
 16		Format(I10,30x,I10)
C
		nx(kwave) = npts
C
		sec = real(nzsec + nzmsec/1000)
C
c		Read(2,*) junk
c		Read(2,*) junk
		Do 17 i = 1,6
			Read(2,199) junk
 17		Continue
199             format(i4)
c		Read(2,*) junk
C
		Read(2,18) kstnm,julian
C		Write(6,18) kstnm,julian
 18		Format(a4,4x,i5)
C
		Do 19 i = 1,6
			Read(2,*) junk
 19		Continue
		Read(2,*) ajunk
C
		apoints = REAL(npts)
		alines = apoints/5.0
		head = AINT(alines)
		rem = alines - head
C
		nlines = INT(apoints/5.0)
		nleft = INT(5.0 * rem)
C
		If(rem.EQ.0.0) Then
C
			ncount = 0
			Do 20 j = 1,nlines
				Read(2,*) (z(ncount + i,kwave),i = 1,5)
C				Write(6,*) (z(ncount + i,kwave),i = 1,5)
				ncount = ncount + 5
 20			Continue
C
		Else
C
			ncount = 0
			Do 22 j = 1,nlines
				Read(2,*) (z(ncount + i,kwave),i = 1,5)
C				Write(6,*) (z(ncount + i,kwave),i = 1,5)
				ncount = ncount + 5
 22			Continue
C
			Read(2,*) (z(ncount + i,kwave),i = 1,nleft)
C			Write(6,*) (z(ncount + i,kwave),i = 1,nleft)
C
		Endif
C
		Close(2)
C
C Actual Vp/Vs ratio
C
		Write(ajulian,'(i5)') julian
		Open(unit = 3, file = ajulian//'_VpVs.txt', status='old')
		Rewind 3
C
		nlines2 = 0
		Do
			Read(3,*,iostat=io) holder
			If(io.EQ.0) then
				nlines2 = nlines2 + 1 
			else
				exit
			end if
		End Do
C
C		Read(julian,*) ijulian
C
		If(julian .LT. 16005 .and. kstnm .EQ. 'IL12') Then
			kstnm = 'IL01'
		Else If(julian .LT. 16007 .and. kstnm .EQ. 'IL23') Then
			kstnm = 'IL17'
		End If
C
		Rewind 3
		Do 23 hold = 1,nlines2
			Read(3,*) vratio, vs, stn
C 51			Format(10x,f7.5,9x,f7.5,1x,a4)			
			If(stn .EQ. kstnm) Then
				EXIT
			End if
 23		Continue
C
		Close(3)
C
C Actual Vp/Vs ratio
C
C Expected Vp/Vs ratio
C
C		vratio = 1.6152 + 0.000127*dist
C
C Expected Vp/Vs ratio
c		Write(6,*) 'Frequency interval: ',df,' No. of points: ',
c    &		nx(kwave)
c		Write(6,25) nzyear,nzjday,nzhour,nzmin,sec
 25		Format('Origin time: ',i4,1x,i3.3,1x,i2.2,':',i2.2,':',f4.1)
c		Write(6,*) 'Station: ',kstnm
C
 10	Continue
c	Write(6,*) ' '
C
C	Calculate max frequency for spectrum
C
C	If(kwave.EQ.2) Then
C		fmax(kwave) = 0.5 * (1.0/sdelta)
C	Else
C		fmax(kwave) = 0.5 * (1.0/sdelta) * vratio
C	Endif
C
c	Write(6,*) 'Maximum frequency: ',fmax
C
C	Calculate travel times of P and S
C
	tp = t0p - omarker
	ts = t0s - omarker
C
c	Write(6,30) kstnm, tp,ts
c 30	Format('Travel time to ',a4,':   P ',f15.7,'   S ',f15.7)
C
C	Calculate S to P travel time ratio, and its square.
C	This param used in Q calculation below.
C
	aob = ts/tp
	aob2p = aob*aob
C
C	Resample frequency/amplitude determinations to have
C       1024 points.  New spectra are written to array
C	ysend, and then overwrites original spectrum in array z.
C
	Do 39 kwave = 1,2
C
		delta = dfa(kwave)
		nsend = nx(kwave)/2
		Write(6,*) nsend
		If(kwave.EQ.2) Then
			delta2 = (endf(kwave) - begf(kwave))/1024.0
		Else
			delta2 = (endf(kwave) - begf(kwave))*vratio/1024.0
		Endif
		factor = delta/delta2
C
		ifac = INT(factor)
C
		xsend(1) = 0.0
C
		Do 40 l = 1,nsend
C
C			Write(6,*) 'Working!',l
			ysend(l) = z(l,kwave)
			If(l.GE.2) Then
				xsend(l) = xsend(l - 1) + delta
			Endif
C			Write(6,*) 'Working.',l
c			Write(6,*) 'xsend(l), ysend(l)',
c     &                              xsend(l), ysend(l)
C
 40		Continue
C		write(6,*) ' '
C
		npoly = 2
		icount = 0
C
		Do 41 m = 1,nsend
C
			icount = icount + 1
C
			xends(1) = xsend(m)
			xends(2) = xsend(m + 1)
			yends(1) = ysend(m)
			yends(2) = ysend(m + 1)
C
			xnew(icount) = xends(1)
			ynew(icount) = yends(1)
C
c			write(6,*) 'xnew(',icount,'), ynew(',
c     &                             icount,')',xnew(icount),
c     &                             ynew(icount)
C
			Do 42 n = 1, ifac - 1
C
			   xinc = REAL(n)
			   xint = xends(1) + xinc * delta2
C
			   Call polint(xends,yends,npoly,xint,yint,dy)
C
			   icount = icount + 1
C
			   xnew(icount) = xint
			   ynew(icount) = yint
C
c			   write(6,*) 'xnew(',icount,'),
c     &            ynew(',icount,')',xnew(icount),ynew(icount)
C
 42			Continue
C
 41		Continue
C
		Do 43 ii = 1,icount
C
			z(ii,kwave) = ynew(ii)
c			write(6,*) 'xnew(ii),z(ii,kwave)',
c     &                              xnew(ii),z(ii,kwave)
C
 43		Continue
C
 39     Continue
C
	ntot = 1024
C
C	Calculate natural log of amplitude spectral ratio and write
C	it to array yy.
C
	xdummy2 = 0.0
C
	Do 50 m = 1,ntot
C
		val = z(m,2) - z(m,1)
		If(ABS(val) .LE. 0.000000001) Then
			val = 0.000000001
		Endif
		yy(m) = LOG(ABS(val))
		xdummy2 = xdummy2 + delta2
c		Write(6,*) 'z(m,2), z(m,1)',z(m,2), z(m,1)
c		Write(6,*) 'xdummy2,yy(m)',xdummy2,yy(m)
		xdummy(m) = 0.0
C
 50	Continue
C
C	Write out yy array in SAC Format so we can pick begin and end
C	points for the slope calculation
C
	Call newhdr
	Call setnhv('NPTS',ntot,nerr)
	Call setfhv('B',0.,nerr)
c	Call setihv('IFTYPE','ITIME',nerr)
	Call setlhv('LEVEN',.TRUE.,nerr)
	Call setfhv('DELTA',delta2,nerr)
	Call setnhv('NZYEAR',nzyear,nerr)
	Call setnhv('NZJDAY',nzjday,nerr)
	Call setnhv('NZHOUR',nzhour,nerr)
	Call setnhv('NZMIN',nzmin,nerr)
	Call setnhv('NZSEC',nzsec,nerr)
	Call setnhv('NZMSEC',nzmsec,nerr)
	Call setkhv('KSTNM',kstnm,nerr)
	Call setkhv('KEVNM',anomen,nerr)
	Call setfhv('USER2',tp,nerr)
	Call setfhv('USER3',ts,nerr)
	Call setfhv('USER4',aob2p,nerr)
	Call wsac0(ofile,xdummy,yy,nerr)
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
      SUBROUTINE POLINT(XA,YA,N,X,Y,DY)
C
C       Numerical recipes, p. 82
C
C      PARAMETER (NMAX=10)
      DIMENSION XA(2),YA(2),C(10),D(10)
      SAVE
	  N=2
      NS=1
      DIF=ABS(X-XA(1))
      DO 11 I=1,N
        DIFT=ABS(X-XA(I))
        IF (DIFT.LT.DIF) THEN
          NS=I
          DIF=DIFT
        ENDIF
        C(I)=YA(I)
        D(I)=YA(I)
11    CONTINUE
      Y=YA(NS)
      NS=NS-1
      DO 13 M=1,N-1
        DO 12 I=1,N-M
          HO=XA(I)-X
          HP=XA(I+M)-X
          W=C(I+1)-D(I)
          DEN=HO-HP
          IF(DEN.EQ.0.)PAUSE
          DEN=W/DEN
          D(I)=HP*DEN
          C(I)=HO*DEN
12      CONTINUE
        IF (2*NS.LT.N-M)THEN
          DY=C(NS+1)
        ELSE
          DY=D(NS)
          NS=NS-1
        ENDIF
        Y=Y+DY
13    CONTINUE
      RETURN
      END

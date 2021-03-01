C	Program qs2gmt.f					28 March 03
C
C	This program reads Qs measurement info stored in qs.stats
C       formatted files (e.g., 99118.vri), and produced by multiq.m SAC
C       macro and fortran codes (multispec.f, multiqcalc.f) and
C       reformats and organizes these results for input into GMT
C       plotting routines.
C
C       Three types of output files are produced:
C
C       eq.loc,     which includes one line describing the source event
C
C       q.stations, which includes one line for each recording station;
C                   each line includes station lat, lon, name, distance,
C                   delta, azim, baz, Qs from stacked spectra, mean Qs
C                   from 400 multiq2.m estimates (qsmean output), and
C                   the standard deviation of the mean Qs estimates.
C
C       q.paths_100-200, etc., which include event and station lats and
C                   lons for GMT plotting, plus recapitulates info found
C                   in two drop files described above.
C
C	Written by RMR.
C
C
	Dimension qs(1000),tstar(1000),qsm(1000),sigmaqs(1000)
	Dimension tstarm(1000), sigmatsm(1000)
	Dimension stnm(1000), slat(1000), slon(1000)
	Dimension dist(1000), gca(1000), azm(1000), baz(1000)
        Dimension ihit(8), binx(50)
        Dimension bin1(50), bin2(50), bin3(50), bin4(50)
        Dimension bin5(50), bin6(50), bin7(50), bin8(50)
C
        Integer emonth,eyr,eday,ejday,ehr,emin
C
	Character*1 ajunk,gmtn
	Character*6 efile
	Character*9 ifile
	Character*10 sfile
	Character*16 qfile
C
	efile = 'eq.loc'
	sfile = 'q.stations'
	qfile(1:8) = 'q.paths_'
C
        gmtn = 'n'
C
C	Find out name of event Qs summary file and open it.
C
        Write(6,*) 'What is name of input file?'
        Read(5,*) ifile
C
	Open(unit=1,file=ifile)
C
C       Find out how many stations we have data for.
C
        icount = 0
C
        Do 1 I = 1,1000
           Read(1,99,end = 1) ajunk
           icount = icount + 1
 1      Continue
C
 99     Format(a1)
C
        Rewind 1
C
C       Should be 4 lines for each station's entry in the input
C       file, so the total number of Qs we have is icount/4.
C
        ntot = icount/4
C
C       Now reread input file and get the info from it.
C
        Do 2 J = 1,ntot
C
           If(J.eq.1) Then
C
	      Read(1,3) elat,elon,edep,emag,emonth,eday,eyr,ejday,
     &            ehr,emin,esec
C
c	      Write(6,3) elat,elon,edep,emag,emonth,eday,eyr,ejday,
c     &             ehr,emin,esec
C
 3            Format(f7.3,1x,f8.3,1x,f5.1,1x,f3.1,2x,i2,1x,i2,1x,
     &               i4,1x,i3,1x,i2,1x,i2,1x,f4.1)
C
           Else
C
	      Read(1,99) ajunk
C
           Endif
C
	   Read(1,99) ajunk
c	   Write(6,*) ajunk
C
           Read(1,4) stnm(J),slat(J),slon(J),dist(J),gca(J),
     &               azm(J),baz(J)
C
c           Write(6,4) stnm(J),slat(J),slon(J),dist(J),gca(J),
c     &                azm(J),baz(J)
C
 4         Format(a3,1x,f10.6,1x,f11.6,1x,f6.1,1x,f6.3,2x,
     &            f5.1,1x,f5.1)
C
           Read(1,5) qs(J),tstar(J),qsm(J),sigmaqs(J),
     &               tstarm(J),sigmatsm(J)
C
c           Write(6,5) qs(J),tstar(J),qsm(J),sigmaqs(J),
c     &                tstarm(J),sigmatsm(J)
C
 5         Format(f5.0,1x,f10.8,1x,f5.0,1x,f4.0,1x,f12.10,
     &            1x,f12.10)
C
 2      Continue
C
	Close(1)
C
C	Write eq.loc.
C
        Open(unit = 2, file = efile)
C
        Write(2,6) elat,elon,edep,emag,emonth,eday,eyr,ejday,
     &             ehr,emin,esec
C
 6      Format(f7.3,1x,f8.3,10x,f5.1,1x,f3.1,2x,i2.2,1x,i2.2,
     &         1x,i4,1x,i3.3,1x,i2.2,':',i2.2,':',f4.1)
C
        Close(2)
C
C	Write q.stations.
C
        Open(unit = 3, file = sfile)
C
        Do 7 K = 1,ntot
C
           Write(3,8) slat(K),slon(K),stnm(K),dist(K),gca(K),
     &                azm(K),baz(K),qs(K),qsm(K),sigmaqs(K)
C
 8         Format(f10.6,1x,f12.6,5x,a3,1x,f6.1,1x,f6.3,2x,
     &            f5.1,1x,f5.1,1x,f5.0,1x,f5.0,1x,f4.0)
C
 7      Continue
C
        Close(3)
C
C	Find out how many output files we'll need for q.paths.
C       Populate the output index arrays with necessary info.
C
        nbin1 = 0
        nbin2 = 0
        nbin3 = 0
        nbin4 = 0
        nbin5 = 0
        nbin6 = 0
        nbin7 = 0
        nbin8 = 0
C
        Do 9 L = 1,ntot
C
           If(qs(L).GE.100.0.AND.qs(L).LT.200.0) Then
C
              ihit(1) = 1
              nbin1 = nbin1 + 1
              bin1(nbin1) = L
C
           Else If(qs(L).GE.200.0.AND.qs(L).LT.300.0) Then
C
              ihit(2) = 1
              nbin2 = nbin2 + 1
              bin2(nbin2) = L
C
           Else If(qs(L).GE.300.0.AND.qs(L).LT.400.0) Then
C
              ihit(3) = 1
              nbin3 = nbin3 + 1
              bin3(nbin3) = L
C
           Else If(qs(L).GE.400.0.AND.qs(L).LT.500.0) Then
C
              ihit(4) = 1
              nbin4 = nbin4 + 1
              bin4(nbin4) = L
C
           Else If(qs(L).GE.500.0.AND.qs(L).LT.600.0) Then
C
              ihit(5) = 1
              nbin5 = nbin5 + 1
              bin5(nbin5) = L
C
           Else If(qs(L).GE.600.0.AND.qs(L).LT.750.0) Then
C
              ihit(6) = 1
              nbin6 = nbin6 + 1
              bin6(nbin6) = L
C
           Else If(qs(L).GE.750.0.AND.qs(L).LT.1000.0) Then
C
              ihit(7) = 1
              nbin7 = nbin7 + 1
              bin7(nbin7) = L
C
           Else If(qs(L).GE.1000.0) Then
C
              ihit(8) = 1
              nbin8 = nbin8 + 1
              bin8(nbin8) = L
C
           Endif
C
 9      Continue
C
        nhit = 0
C
        Do 10 M = 1,8
C
           nhit = nhit + ihit(M)
C
 10     Continue
C
C	Write to output files.
C
        Do 11 N = 1,nhit
C
           If(ihit(N).EQ.1.AND.N.LE.5) Then
C
              If(N.EQ.1) Then
C
                 nbinx = nbin1
                 Do 110 ire = 1,nbinx
                    binx(ire) = bin1(ire)
 110             Continue
C
                 qfile(9:15) = '100-200'
C
              Else If(N.EQ.2) Then
C
                 nbinx = nbin2
                 Do 111 ire = 1,nbinx
                    binx(ire) = bin2(ire)
 111             Continue
C
                 qfile(9:15) = '200-300'
C
              Else If(N.EQ.3) Then
C
                 nbinx = nbin3
                 Do 112 ire = 1,nbinx
                    binx(ire) = bin3(ire)
 112             Continue
C
                 qfile(9:15) = '300-400'
C
              Else If(N.EQ.4) Then
C
                 nbinx = nbin4
                 Do 113 ire = 1,nbinx
                    binx(ire) = bin4(ire)
 113             Continue
C
                 qfile(9:15) = '400-500'
C
              Else If(N.EQ.5) Then
C
                 nbinx = nbin5
                 Do 114 ire = 1,nbinx
                    binx(ire) = bin5(ire)
 114             Continue
C
                 qfile(9:15) = '500-600'
C
              Endif
C
              Open(unit = 4, file = qfile)
C
              Write(4,99) gmtn
C
              Do 12 ii = 1,nbinx
C
                 Write(4,13) elat,elon,edep,emag,emonth,eday,eyr,
     &                    ejday,ehr,emin,esec
C
 13              Format(f7.3,4x,f8.3,8x,f5.1,1x,f3.1,2x,i2.2,1x,
     &             i2.2,1x,i4,1x,i3.3,1x,i2.2,':',i2.2,':',f4.1)
C
                 Write(4,14) slat(binx(ii)),slon(binx(ii)),
     &                       stnm(binx(ii)),dist(binx(ii)),
     &                       gca(binx(ii)),azm(binx(ii)),
     &                       baz(binx(ii)),qs(binx(ii)),
     &                       qsm(binx(ii)),sigmaqs(binx(ii))
C
 14              Format(f10.6,1x,f11.6,5x,a3,1x,f6.1,1x,f6.3,2x,
     &                     f5.1,1x,f5.1,1x,f5.0,1x,f5.0,1x,f4.0)
C
                 Write(4,99) gmtn
C
 12           Continue
C
              Close(4)
C
           Else If(ihit(N).EQ.1.AND.N.EQ.6) Then
C
              qfile(9:12) = '600-750'
C
              Open(unit = 4, file = qfile)
C
              Write(4,99) gmtn
C
              Do 15 jj = 1,nbin6
C
                 Write(4,13) elat,elon,edep,emag,emonth,eday,eyr,
     &                    ejday,ehr,emin,esec
C
                 Write(4,14) slat(bin6(jj)),slon(bin6(jj)),
     &                       stnm(bin6(jj)),dist(bin6(jj)),
     &                       gca(bin6(jj)),azm(bin6(jj)),
     &                       baz(bin6(jj)),qs(bin6(jj)),
     &                       qsm(bin6(jj)),sigmaqs(bin6(jj))
C
                 Write(4,99) gmtn
C
 15           Continue
C
              Close(4)
C
           Else If(ihit(N).EQ.1.AND.N.EQ.7) Then
C
              qfile(9:16) = '750-1000'
C
              Open(unit = 4, file = qfile)
C
              Write(4,99) gmtn
C
              Do 16 kk = 1,nbin7
C
                 Write(4,13) elat,elon,edep,emag,emonth,eday,eyr,
     &                    ejday,ehr,emin,esec
C
                 Write(4,14) slat(bin7(kk)),slon(bin7(kk)),
     &                       stnm(bin7(kk)),dist(bin7(kk)),
     &                       gca(bin7(kk)),azm(bin7(kk)),
     &                       baz(bin7(kk)),qs(bin7(kk)),
     &                       qsm(bin7(kk)),sigmaqs(bin7(kk))
C
                 Write(4,99) gmtn
C
 16           Continue
C
              Close(4)
C
           Else If(ihit(N).EQ.1.AND.N.EQ.8) Then
C
              qfile(9:13) = '1000+'
C
              Open(unit = 4, file = qfile)
C
              Write(4,99) gmtn
C
              Do 17 ll = 1,nbin8
C
                 Write(4,13) elat,elon,edep,emag,emonth,eday,eyr,
     &                    ejday,ehr,emin,esec
C
                 Write(4,14) slat(bin8(ll)),slon(bin8(ll)),
     &                       stnm(bin8(ll)),dist(bin8(ll)),
     &                       gca(bin8(ll)),azm(bin8(ll)),
     &                       baz(bin8(ll)),qs(bin8(ll)),
     &                       qsm(bin8(ll)),sigmaqs(bin8(ll))
C
                 Write(4,99) gmtn
C
 17           Continue
C
              Close(4)
C
           Endif
C
  11    Continue
C
C
C
	Stop
	End

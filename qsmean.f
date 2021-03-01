C	Program qsmean.f					11 March 03
C
C	This program reads Qs measurements produced by multiq.m SAC
C       macro and fortran codes (multispec.f, multiqcalc.f) and
C       calculates the mean Qs from the total number of estimates
C       produced by the codes mentioned for the P and S data windows
C       defined by the user.
C
C       Code also calculates a `mean' Qs weighted by the proportion
C       of the total P and S time windows that the Qs estimate is
C       made for, i.e., each estimate is for a slightly longer
C       P or S window (or both) than the previous, after the first
C       estimate, which is made on the Pmin/Smin time window.
C
C	Written by RMR.
C
C
	Dimension qs(400), tstar(400), sigmab(400)
	Dimension sigmam(400), chisq(400)
	Dimension begP(400), endP(400)
	Dimension begS(400), endS(400)
	Dimension months(12)
C
	Character*1 ajunk,emsec
	Character*2 ehr
	Character*3 ajday,months,amonth
	Character*4 ayr,stnm
	Character*6 ifile
	Character*8 ofile
	Character*10 ofile2
C
        Integer emin,esec
C
        Data months /'JAN','FEB','MAR','APR','MAY','JUN',
     &               'JUL','AUG','SEP','OCT','NOV','DEC'/
C
	ifile = 'qs.out'
	ofile = 'qs.stats'
C
        istat = -99
C
C	Open file dropped by complementary SAC macro multiq.m.
C	This file is written in the run directory by the macro
C       and includes the run output we want.
C
	Open(unit=1,file=ifile)
C
	Read(1,19,iostat = istat) elat,elon,edep,emag,iehr,
     &       iemin,iesec,amonth,iday,jday,iyr
C
C	Write(6,19) elat,elon,edep,emag,iehr,iemin,iesec,
C     &             amonth,iday,jday,iyr
C
 1      Format(G12.6,1x,G12.6,1x,G12.6,1x,G12.6,1x,a2,
     &         i2,i2,1x,a3,1x,i2,2x,i3,3x,i4)
C
 19     Format(G12.6,1x,G12.6,1x,G12.6,1x,G12.6,1x,i2,
     &         i2,i2,1x,a3,1x,i2,2x,i3,3x,i4)
C
	Read(1,99,iostat = istat) ajunk
	Write(6,*) ajunk
 99     Format(a1)
C
        Read(1,2,iostat = istat) stnm,slat,slon,dist,gca,azm,bazm
        Write(6,2) stnm,slat,slon,dist,gca,azm,bazm
C
 2      Format(a4,1x,G12.6,1x,G12.6,1x,G12.6,1x,G12.6,1x,
     &         G12.6,1x,G12.6)
C
	Read(1,99,iostat = istat) ajunk
C	Write(6,*) ajunk
	Read(1,99,iostat = istat) ajunk
C	Write(6,*) ajunk
C
        icount = 0
C
        Do 3 I = 1,400
C
           Read (1,4,iostat = istat) qs(I),tstar(I),sigmab(I),sigmam(I),
     &                chisq(I),begP(I),endP(I),begS(I),endS(I)
C
c          Write (6,4) qs(I),tstar(I),sigmab(I),sigmam(I),
c    &                chisq(I),begP(I),endP(I),begS(I),endS(I)
C
           icount = icount + 1
C
 3      Continue
C
 4      Format(G12.6,1x,G12.6,1x,G12.6,1x,G12.6,1x,G12.6,
     &         1x,G12.6,1x,G13.7,1x,G12.6,1x,G13.7)
C
        Read(1,5,iostat = istat) t7,t8,sqs,ststar
C
 5      Format(5x,G12.6,6x,G12.6,14x,G12.6,15x,G12.6)
C
	Close(1)
C
        Do 6 K = 1,12
                If(months(K).EQ.amonth) Then
                        imonth = K
                Endif
 6      Continue
C
C       Determine mean values and other statistics
C
	Call moment(qs,icount,qave,qadev,qsdev,qvar,qskew,qcurt)
	Call moment(tstar,icount,tave,tadev,tsdev,tvar,tskew,tcurt)
C
C	Write out to screen and to output files
C
c       ofile2(1:2) = ayr(3:4)
c       ofile2(3:5) = ajday(1:3)
c       ofile2(6:6) = '.'
c       ofile2(7:8) = ehr(1:2)
c       ofile2(9:9) = '.'
c       ofile2(10:13) = stnm(1:4)
C
        ofile2 = 'qsmean.out'
C
        Open(unit = 3, file = ofile2)
C
        Write(3,7) elat,elon,edep,emag,imonth,iday,ayr,
     &              iehr,iemin,iesec
C
 7      Format(f7.3,1x,f8.3,1x,f5.1,1x,f3.1,2x,i2.2,1x,
     &         i2.2,1x,a4,1x,i2,':',i2.2,':',i2.2)
C
        Write(3,*) ajunk
C
        Write(3,8) stnm,slat,slon,dist,gca,azm,bazm
C
 8      Format(a3,1x,f10.6,1x,f11.6,1x,f6.1,1x,f6.3,2x,
     &         f5.1,1x,f5.1)
C
        Write(3,9) sqs,ststar,qave,qsdev,tave,tsdev
C
 9      Format(f5.0,1x,f10.8,1x,f5.0,1x,f4.0,1x,f12.10,
     &         1x,f12.10)
C
        Close(3)
C
        Write(6,10) 'Qs:'
        Write(6,11) 'Mean Qs = ',qave
        Write(6,*) 'Mean absolute deviation of Qs = ',qadev
        Write(6,*) 'Standard deviation of Qs = ',qsdev
        Write(6,*) 'Variance of Qs = ',qvar
        Write(6,*) 'Skewness of Qs = ',qskew
        Write(6,*) 'Kurtosis of Qs = ',qcurt
C
        Write(6,10) ' '
        Write(6,10) 't*:'
        Write(6,12) 'Mean t* = ',tave
        Write(6,*) 'Mean absolute deviation of t* = ',tadev
        Write(6,*) 'Standard deviation of t* = ',tadev
        Write(6,*) 'Variance of t* = ',tvar
        Write(6,*) 'Skewness of t* = ',tskew
        Write(6,*) 'Kurtosis of t* = ',tcurt
C
        Open(unit = 2, file = ofile)
C
        Write(2,*) 'Station: ',stnm
        Write(2,*) 'Date: ',amonth,iday,ajday,ayr
        Write(2,*) 'Origin: ',iehr,emin,esec
        Write(2,10) 'Qs:'
        Write(2,11) 'Mean Qs = ',qave
        Write(2,11) 'Mean absolute deviation of Qs = ',qadev
        Write(2,11) 'Standard deviation of Qs = ',qsdev
        Write(2,11) 'Variance of Qs = ',qvar
        Write(2,11) 'Skewness of Qs = ',qskew
        Write(2,11) 'Kurtosis of Qs = ',qcurt
C
        Write(2,10) 't*:'
        Write(2,12) 'Mean t* = ',tave
        Write(2,12) 'Mean absolute deviation of t* = ',tadev
        Write(2,12) 'Standard deviation of t* = ',tadev
        Write(2,12) 'Variance of t* = ',tvar
        Write(2,12) 'Skewness of t* = ',tskew
        Write(2,12) 'Kurtosis of t* = ',tcurt
C
        Close(2)
C
 10     Format(a3)
 11     Format(a32,f10.2)
 12     Format(a32,f12.10)
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
      subroutine moment(data,n,ave,adev,sdev,var,skew,curt)
      dimension data(n)
      if(n.le.1)pause 'n must be at least 2'
      s=0.
      do 11 j=1,n
        s=s+data(j)
11    continue
      ave=s/n
      adev=0.
      var=0.
      skew=0.
      curt=0.
      do 12 j=1,n
        s=data(j)-ave
        adev=adev+abs(s)
        p=s*s
        var=var+p
        p=p*s
        skew=skew+p
        p=p*s
        curt=curt+p
12    continue
      adev=adev/n
      var=var/(n-1)
      sdev=sqrt(var)
      if(var.ne.0.)then
        skew=skew/(n*sdev**3)
        curt=curt/(n*var**2)-3.  
      else
        Write(6,*) 'no skew or kurtosis when zero variance'
      endif
      return
      end

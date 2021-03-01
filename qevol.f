C	Program qevol.f					12 March 03
C
C	This program reads Qs and t* measurements produced by
C       multiq.m SAC macro and fortran codes (multispec.f,
C       multiqcalc.f) and produces input files for a 3-d
C       histogram of individual Qs/t* estimates' evolution
C       with P and S wave window length (from Pmin, Smin
C       to Pmax, Smax).  Input file is qs.out of multiq.m.
C
C	Written by RMR.
C
C
	Dimension qs(1000),tstar(1000),sigmab(1000)
	Dimension sigmam(1000),chisq(1000)
	Dimension begP(1000),endP(1000)
	Dimension begS(1000),endS(1000)
C
	Character*1 ajunk
	Character*6 ifile
	Character*8 ofile
C
	ifile = 'qs.out'
	ofile = 'qs.stats'
C
C	Open file dropped by complementary SAC macro multiq.m.
C	This file is written in the run directory by the macro
C       and includes the run output we want.
C
	Open(unit=1,file=ifile)
C
	Read(1,*) ajunk
c	Write(6,*) ajunk
C
        icount = 0
C
        Do 1 I = 1,1000
C
           Read (1,2,end = 1) qs(I),tstar(I),sigmab(I),sigmam(I),
     &                chisq(I)
C
           Write (6,2) qs(I),tstar(I),sigmab(I),sigmam(I),
     &                chisq(I)
C
           icount = icount + 1
C
 1      Continue
C
 2      Format(G12.6,1x,G12.6,1x,G12.6,1x,G12.6,1x,G12.6)
C
	Close(1)
C
C       Determine mean values and other statistics
C
	Call moment(qs,icount,qave,qadev,qsdev,qvar,qskew,qcurt)
	Call moment(tstar,icount,tave,tadev,tsdev,tvar,tskew,tcurt)
C
C	Write out to screen and to output file
C
C
        Write(6,3) 'Qs:'
        Write(6,4) 'Mean Qs = ',qave
        Write(6,*) 'Mean absolute deviation of Qs = ',qadev
        Write(6,*) 'Standard deviation of Qs = ',qsdev
        Write(6,*) 'Variance of Qs = ',qvar
        Write(6,*) 'Skewness of Qs = ',qskew
        Write(6,*) 'Kurtosis of Qs = ',qcurt
C
        Write(6,3) ' '
        Write(6,3) 't*:'
        Write(6,5) 'Mean t* = ',tave
        Write(6,*) 'Mean absolute deviation of t* = ',tadev
        Write(6,*) 'Standard deviation of t* = ',tadev
        Write(6,*) 'Variance of t* = ',tvar
        Write(6,*) 'Skewness of t* = ',tskew
        Write(6,*) 'Kurtosis of t* = ',tcurt
C
        Open(unit = 2, file = ofile)
C
        Write(2,3) 'Qs:'
        Write(2,4) 'Mean Qs = ',qave
        Write(2,4) 'Mean absolute deviation of Qs = ',qadev
        Write(2,4) 'Standard deviation of Qs = ',qsdev
        Write(2,4) 'Variance of Qs = ',qvar
        Write(2,4) 'Skewness of Qs = ',qskew
        Write(2,4) 'Kurtosis of Qs = ',qcurt
C
        Write(2,3) 't*:'
        Write(2,5) 'Mean t* = ',tave
        Write(2,5) 'Mean absolute deviation of t* = ',tadev
        Write(2,5) 'Standard deviation of t* = ',tadev
        Write(2,5) 'Variance of t* = ',tvar
        Write(2,5) 'Skewness of t* = ',tskew
        Write(2,5) 'Kurtosis of t* = ',tcurt
C
        Close(2)
C
 3      Format(a3)
 4      Format(a32,f10.2)
 5      Format(a32,f12.10)
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
        pause 'no skew or kurtosis when zero variance'
      endif
      return
      end

C	Program qsiter.f					12 March 03
C
C	This program reads Qs measurements produced by multiq.m SAC
C       macro and fortran codes (multispec.f, multiqcalc.f) and
C       plots reformats them for use in GMT scripts.  The Qs values
C       are rewritten as column 3 of an x,y,z triple set, where
C       x and y are the iteration numbers of the loops over P and
C       S time series windows used to create spectral ratios for
C       Qs measurements.
C
C	Written by RMR.
C
C
	Dimension qs(1000),tstar(1000),sigmab(1000)
	Dimension sigmam(1000),chisq(1000)
	Dimension begP(1000),endP(1000)
	Dimension begS(1000),endS(1000)
	Dimension weight(1000)
C
	Character*1 ajunk
	Character*8 ifile
	Character*17 ofile
C
	Write(6,*) 'What is name of input file?'
        Read(5,*) ifile
C
C	Open file dropped by complementary SAC macro multiq.m.
C	This file is written in the run directory by the macro
C       and includes the run output we want.
C
	Open(unit=1,file=ifile)
C
	Read(1,99) ajunk
 	Write(6,*) ajunk
	Read(1,99) ajunk
 	Write(6,*) ajunk
	Read(1,99) ajunk
 	Write(6,*) ajunk
	Read(1,99) ajunk
 	Write(6,*) ajunk
	Read(1,99) ajunk
 	Write(6,*) ajunk
 99	Format(a1)
C
        icount = 0
C
        Do 1 I = 1,400
C
           Read (1,2,end = 1) qs(I),tstar(I),sigmab(I),sigmam(I),
     &                chisq(I),begP(I),endP(I),begS(I),endS(I)
C
           Write (6,2) qs(I),tstar(I),sigmab(I),sigmam(I),
     &                chisq(I),begP(I),endP(I),begS(I),endS(I)
C
           icount = icount + 1
C
 1      Continue
C
 2      Format(G12.6,1x,G12.6,1x,G12.6,1x,G12.6,1x,G12.6,
     &         1x,G12.6,1x,G13.7,1x,G12.6,1x,G13.7)
C
	Close(1)
C
        Write(6,*) 'What is name of output file?'
        Read(5,*) ofile
C
        Open(unit = 2, file = ofile)
C
        total = REAL(icount)
        totalp = SQRT(total)
        incp = INT(totalp)
        incs = incp
C
        ncount = 1
C
        Do 10 J = 1,incp
C
                piter = REAL(J)
C
                Do 11 K = 1,incs
C
                   siter = REAL(K)
C
                   write(2,3) piter,siter,qs(ncount)
                   write(6,*) piter,siter,qs(ncount)
C
                   ncount = ncount + 1
C
 11             Continue
C
 10     Continue
C
        Close(2)
C
 3      Format(f4.1,2x,f4.1,2x,f10.4)
C
C
C
	Stop
	End

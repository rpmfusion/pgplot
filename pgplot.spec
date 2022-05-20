%{!?tcl_version: %define tcl_version %(echo 'puts $tcl_version' | tclsh)}
%{!?tcl_sitearch: %define tcl_sitearch %{_libdir}/tcl%{tcl_version}}
Name: pgplot 
%define lvmajor 5
Version: 5.2.2
Release: 52%{?dist}
Summary: Graphic library for making simple scientific graphs

License: freely available for non-commercial use

URL: http://www.astro.caltech.edu/~tjp/pgplot
Source0: ftp://ftp.astro.caltech.edu/pub/pgplot/pgplot5.2.tar.gz
Source1: pgplot.pc
Source2: cpgplot.pc
Source3: tk-pgplot.pc
Source4: pgplot-pkgIndex.tcl
Source5: README.fedora
Source6: motif-pgplot.pc

# Make pgplot find files in standard locations such as
# /usr/libexec/pgplot and /usr/share/pgplot
Patch0: pgplot5.2-fsstnd.patch
# Fix the location of perl 
Patch1: pgplot5.2-makefile.patch
# make the compiler script accept FFLAGS and FC
Patch2: pgplot5.2-g77_gcc_conf.patch
# Needed by the (disabled) png driver
Patch3: pgplot5.2-pngdriver.patch
# Needed to have a loadable tcl package
Patch4: pgplot5.2-tclpackage.patch
# Fix format error 
Patch5: pgplot5.2-formaterror.patch
Patch6: pgplot5.2-tcl86.patch

BuildRequires: tk-devel
BuildRequires: libX11-devel
BuildRequires: gcc-gfortran
BuildRequires: perl
BuildRequires: motif-devel

Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
The PGPLOT Graphics Subroutine Library is a Fortran- or C-callable, 
device-independent graphics package for making simple scientific graphs. 
It is intended for making graphical images of publication quality with 
minimum effort on the part of the user. For most applications, 
the program can be device-independent, and the output can be directed to 
the appropriate device at run time.

%package devel
Summary: Libraries, includes, etc. used to develop an application with %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libX11-devel

%description devel
These are the header files and static libraries needed to develop a %{name} 
application.

%package demos
Summary: Demo applications of %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
%description demos
Demonstration applications for PGPLOT, a FORTRAN-callable,
device-independent graphics package for making simple scientific graphs.

%package -n tcl-%{name}
Summary: Tcl/Tk driver for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: tcl(abi) = 8.6 
Provides: tk-%{name} = %{version}-%{release}

%description -n tcl-%{name}
Tcl/Tk driver for %{name}

%package -n tcl-%{name}-devel
Summary: Tcl/Tk driver for %{name} devel files 
Requires: tcl-%{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
Requires: tk-devel
Provides: tk-%{name}-devel = %{version}-%{release}

%description -n tcl-%{name}-devel
Libraries, includes, etc. used to develop an application using
the %{name} Tcl/Tk driver.

%package -n motif-%{name}
Summary: MOTIF driver for %{name}
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
#Requires: tcl(abi) = 8.5
Provides: motif-%{name} = %{version}-%{release}

%description -n motif-%{name}
MOTIF driver for %{name}

%package -n motif-%{name}-devel
Summary: MOTIF driver for %{name} devel files
Group: Development/Libraries
Requires: motif-%{name} = %{version}-%{release}
Requires: %{name}-devel = %{version}-%{release}
Provides: motif-%{name}-devel = %{version}-%{release}

%description -n motif-%{name}-devel
Libraries and h files used to develop an application using
the %{name} MOTIF driver.

%prep
%setup -q -n %{name}

%patch0 -p1
%patch1 -p1
%patch2 -p1
# PNG disabled
#%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} pkgIndex.tcl
cp %{SOURCE5} .
cp %{SOURCE6} .

# Enabling the following drivers:
# PS, TCL/TK and X
%{__sed} \
-e 's/! PSDRIV/  PSDRIV/g' \
-e 's/! XWDRIV/  XWDRIV/g' \
-e 's/! TKDRIV/  TKDRIV/g' \
-e 's/! PPDRIV/  PPDRIV/g' \
-e 's/! GIDRIV/  GIDRIV/g' \
-e 's/! XMDRIV/  XMDRIV/g' -i drivers.list

# Creating pkgconfig files from templates
%{__sed} -e 's|archlibdir|%{_libdir}|g' -i pgplot.pc
%{__sed} -e 's|archlibdir|%{_libdir}|g' -i cpgplot.pc
%{__sed} -e 's|archlibdir|%{_libdir}|g' -i tk-pgplot.pc
%{__sed} -e 's|archlibdir|%{_libdir}|g' -i pkgIndex.tcl

# Version files stored in one Changelog
(for i in $(find . -name "ver*.txt" |sort -r); do iconv -f "ISO-8859-1" -t "utf8" $i; done) > ChangeLog

%build
./makemake . linux g77_gcc
# Parallel make not supported
%{__make} FC="f95" CC="%{__cc}" CFLAGS="%{optflags}" FFLAGS="%{optflags} -std=legacy" \
   NLIBS="-lgfortran -lm -lX11 -lz"

# Creating dynamic library for C
%{make_build} \
   FC=f95 CC="%{__cc}" CFLAGS="%{optflags}" FFLAGS="%{optflags} -std=legacy" cpg
%{__ar} x libcpgplot.a
%{__cc} %{optflags} -shared -o libc%{name}.so.%{version} \
    -Wl,-soname,libc%{name}.so.%{lvmajor} \
    cpg*.o -L . -l%{name} -lgfortran -lm -lX11 -lz

# Creating dynamic library for TK
%{__ar} x libtkpgplot.a
%{__cc} %{optflags} -shared -o libtk%{name}.so.%{version} \
    -Wl,-soname,libtk%{name}.so.%{lvmajor} \
    tkpgplot.o -L . -l%{name} -ltk -ltcl -lX11

# Creating dynamic library for MOTIF
%{__ar} x libXmPgplot.a
%{__cc} %{optflags} -shared -o libXmPgplot.so.%{version} \
    -Wl,-soname,libXmPgplot.so.%{lvmajor} \
    XmPgplot.o -L . -l%{name} -lX11


for i in lib*.so.%{version}; do
  chmod 755 $i
done

%{__ln_s} lib%{name}.so.%{version} lib%{name}.so.%{lvmajor}
%{__ln_s} lib%{name}.so.%{version} lib%{name}.so
%{__ln_s} libc%{name}.so.%{version} libc%{name}.so.%{lvmajor}
%{__ln_s} libc%{name}.so.%{version} libc%{name}.so
%{__ln_s} libtk%{name}.so.%{version} libtk%{name}.so.%{lvmajor}
%{__ln_s} libtk%{name}.so.%{version} libtk%{name}.so
%{__ln_s} libXmPgplot.so.%{version} libXmPgplot.so.%{lvmajor}
%{__ln_s} libXmPgplot.so.%{version} libXmPgplot.so


%{make_build} pgplot-routines.tex
%{make_build} pgplot.html

%install
%{__mkdir_p} %{buildroot}/%{_bindir}
%{__mkdir_p} %{buildroot}/%{_libdir}/pkgconfig
%{__mkdir_p} %{buildroot}/%{_includedir}
%{__mkdir_p} %{buildroot}/%{_datadir}/%{name}
%{__mkdir_p} %{buildroot}/%{_libexecdir}/%{name}
%{__mkdir_p} %{buildroot}/%{tcl_sitearch}/%{name}
%{__cp} -a  lib*%{name}.so* %{buildroot}/%{_libdir}
%{__cp} -a  libXmPgplot.so* %{buildroot}/%{_libdir}
%{__install} -p -m 644 XmPgplot.h %{buildroot}/%{_includedir}
%{__install} -p -m 644 cpgplot.h %{buildroot}/%{_includedir}
%{__install} -p -m 644 tkpgplot.h %{buildroot}/%{_includedir}
%{__install} -p -m 644 rgb.txt %{buildroot}/%{_datadir}/%{name}
%{__install} -p -m 644 grfont.dat %{buildroot}/%{_datadir}/%{name}
%{__install} -p -m 755 pgxwin_server %{buildroot}/%{_libexecdir}/%{name}
%{__install} -p -m 755 pgdemo* cpgdemo %{buildroot}/%{_bindir}
%{__install} -p -m 644 *.pc %{buildroot}/%{_libdir}/pkgconfig
%{__install} -p -m 644 pkgIndex.tcl %{buildroot}/%{tcl_sitearch}/%{name}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post -n tcl-%{name} -p /sbin/ldconfig

%postun -n tcl-%{name} -p /sbin/ldconfig

%files
%doc ChangeLog README.fedora
%license  copyright.notice
%{_libdir}/lib%{name}.so.*
%{_libdir}/libc%{name}.so.*
%{_datadir}/%{name}
%{_libexecdir}/%{name}

%files devel
%doc aaaread.me pgplot-routines.tex pgplot.html
%license copyright.notice
%{_libdir}/lib%{name}.so
%{_libdir}/libc%{name}.so
%{_includedir}/cpgplot.h
%{_libdir}/pkgconfig/pgplot.pc
%{_libdir}/pkgconfig/cpgplot.pc

%files -n tcl-%{name}
%license copyright.notice
%{_libdir}/libtk%{name}.so.*
%{tcl_sitearch}/%{name}

%files -n tcl-%{name}-devel
%license copyright.notice
%{_libdir}/libtk%{name}.so
%{_includedir}/tkpgplot.h
%{_libdir}/pkgconfig/tk-pgplot.pc

%files -n motif-%{name}
%doc copyright.notice
%{_libdir}/libXmPgplot.so.*

%files -n motif-%{name}-devel
%doc copyright.notice
%{_libdir}/libXmPgplot.so
%{_includedir}/XmPgplot.h
%{_libdir}/pkgconfig/motif-pgplot.pc

%files demos
%license copyright.notice
%{_bindir}/*

%changelog
* Wed Aug 04 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 5.2.2-52
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Thu Feb 04 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 5.2.2-51
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Aug 19 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 5.2.2-50
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun May 17 2020 Leigh Scott <leigh123linux@gmail.com> - 5.2.2-49
- Fix FTBFS

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 5.2.2-48
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Jan 12 2020 Leigh Scott <leigh123linux@gmail.com> - 5.2.2-47
- Spec file clean up

* Sat Aug 10 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 5.2.2-46
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Mar 05 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 5.2.2-45
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sun Aug 19 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 5.2.2-44
- Rebuilt for Fedora 29 Mass Rebuild binutils issue

* Fri Jul 27 2018 RPM Fusion Release Engineering <sergio@serjux.com> - 5.2.2-43
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Mar 02 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 5.2.2-42
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Feb 04 2018 Sérgio Basto <sergio@serjux.com> - 5.2.2-41
- Rebuild (gfortran-8.0.1)

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 5.2.2-40
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Mar 26 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 5.2.2-39
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Oct 26 2014 Sergio Pascual <sergio.pasra@gmail.com> - 5.2.2-38
- Update tcl abi to 8.6

* Sat Oct 25 2014 Sérgio Basto <sergio@serjux.com> - 5.2.2-37
- Rebuild for new tcl-8.6

* Mon Sep 01 2014 Sergio Pascual <sergio.pasra@gmail.com> - 5.2.2-36
- Fix wrong dates in changelog
- Fix compilation errors

* Tue Mar 12 2013 Nicolas Chauvet <kwizart@gmail.com> - 5.2.2-35
- https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Mar 08 2012 Sergio Pascual <sergio.pasra@gmail.com> - 5.2.2-34
- EVR bump for rebuild

* Sun Feb 12 2012 Sergio Pascual <sergio.pasra@gmail.com> - 5.2.2-33
- Disabled png support
- Added README.fedora listing the enabled drivers

* Thu Feb 09 2012 Nicolas Chauvet <kwizart@gmail.com> - 5.2.2-32
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun May 03 2009 Sergio Pascual <sergio.pasra@gmail.com> - 5.2.2-31
- PPM doesn't work in EL, with gcc < 4.3

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 5.2.2-30
- rebuild for new F11 features

* Sat Dec 06 2008 Sergio Pascual <sergio.pasra@gmail.com> 5.2.2-29
- Fixing bz #228. Multilib conflict produced by pgplot-routines.pdf

* Tue Nov 18 2008 Sergio Pascual <sergio.pasra@gmail.com> 5.2.2-28
- Fixing bz #168. There was a typo in patch0

* Thu Nov 13 2008 Sergio Pascual <sergio.pasra@gmail.com> 5.2.2-27
- Patch0 adapted to the buildsystem of fedora 10

* Thu Nov 13 2008 Sergio Pascual <sergio.pasra@gmail.com> 5.2.2-26
- Provides includes release

* Wed Nov 12 2008 Sergio Pascual <sergio.pasra@gmail.com> 5.2.2-25
- Fixed non-standard-executable-perm in libcpgplot and libtkpgplot
- Included version files in one Changelog
- Parallel make works only with make cpg
- Removed macro lvfull, using version instead
- copyright.notice in all subpackages
- Patched tk driver to have a loadable package
- Tk driver follows tcl guidelines

* Sun Nov 09 2008 Sergio Pascual <sergio.pasra@gmail.com> 5.2.2-24
- Using sed to enable the drivers instead of patch
- Removed docs package
- Added pkgconfig files
- Package tcl renamed as tk
- Create pdf doc from latex routines description

* Wed Nov 05 2008 Sergio Pascual <sergio.pasra@gmail.com> 5.2.2-23
- Fixing weak symbols in libcpgplot
- Poststages for libtkpgplot
- pgplot-tcl-devel requires pgplot-tcl

* Fri Jun 27 2008 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-22
- Spec cleanup
- Building againts el5

* Thu Jun 05 2008 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-21
- Readded gif
- Spec cleanup

* Thu Jun 05 2008 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-21
- Readded gif
- Spec cleanup

* Thu Sep 06 2007 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-20
- Adding png

* Fri Jul 20 2007 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-19
- Demos compiled with debug flags
- Test to compile with gfortran

* Thu Dec 14 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-18
- Added Tcl/Tk driver. 
- New subpackges pgplot-tcl and pgplot-tcl-devel.

* Wed Nov 01 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-17
- Rebuild for fc6.

* Fri Oct 13 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-16
- Added correct Requires in devel subpackage.

* Mon Sep 25 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-15
- Extra documentation added.

* Fri Jul 28 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-14
- New m4 macros.

* Wed Jul 26 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-13
- Honors FFLAGS and CFLAGS, can not be built with gfortran.
- Rebuild for FC5.

* Fri Mar 17 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-12
- Removed pgplot-acentos.tar.gz.

* Wed Mar 15 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-11
- Unpacking correctly pgplot-m4.tar.gz and pgplot-acentos.tar.gz.

* Wed Mar 15 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-10
- Added Requires for devel package.

* Tue Feb 21 2006 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-9
- Minor fixes.
- Excluded static libraries.

* Mon Nov 28 2005 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-8
- Adding soname to the shared libs.
- Minor fixes.

* Wed Apr 27 2005 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-7
- Using dist tags. Adding pgplot.m4 and grfont with accented characters.

* Wed Apr 20 2005 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-6
- Rebuild for FC3. Removed grfont with accented characters.

* Fri Nov 21 2003 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-5
- Added docs package.

* Tue Feb 25 2003 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-4
- Added demos.

* Wed Feb 12 2003 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-3
- Splited devel part.

* Tue Feb 11 2003 Nicolas Cardiel <ncl@astrax.fis.ucm.es> 5.2.2-2
- Added suport for accents.

* Mon May 27 2002 Sergio Pascual <spr@astrax.fis.ucm.es> 5.2.2-1
- Initial RPM release.

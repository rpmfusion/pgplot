#!/bin/sh
# collect up all the "base" files into a tar file
# that is used to build an rpm

# usage: maketar.sh tarfile [version] [release] [releasedate]


name=pgplot
startdir=$(pwd)
me=$(realpath -e -L $0)
distdir=$(dirname $me)
basedir=$(realpath -e -L $distdir/..)
echo "startdir $startdir"
echo "distdir $distdir"
echo "basedir $basedir"

echo "ls -l \$startdir"
ls -l $startdir


tarfile=$1
if test "x$tarfile" = "x" ;
then
    tarfile=${name}.tar
fi
echo "tarfile: $tarfile"

VERSION=$2
CVER=$(awk '/^Version/ {print $2}' $basedir/${name}.spec)
if test "x${VERSION}" = "x"  ;
then
    VERSION=$CVER
    echo "VERSION ($VERSION) from ${name}.spec"
elif test "${VERSION}" != "${CVER}"  ;
then
    echo "$0 version requested $VERSION mismatch ${name}.spec $CVER"
    exit 1
fi
    
RELEASE=$3
if test "x${RELEASE}" = "x"  ;
then
    RELEASE=$(awk '/^Release=/{print $2}' $basedir/${name}.spec | cut -d'%' -f1)
    echo "RELEASE ($RELEASE) from ${name}.spec"
fi

RELDATE=$4
if test "x${RELDATE}" = "x"  ;
then
    RELDATE=$(date -I)
    echo "RELDATE ($RELDATE) from current date"
fi

echo "Version $VERSION Release $RELEASE Date $RELDATE"

tmpdir=$(mktemp -p "/tmp" -d "${name}DIST_XXXXXXXX")
echo "tmpdir $tmpdir"
if test ! -e "$tmpdir" ;
then
    echo "failed to create $tmpdir"
    exit 1
fi
cd $tmpdir

#directory for dist
tardir=$(basename "$tarfile" .tar) 
mkdir ${tardir}
cd ${tardir}

#populate with symbolic links from main code directory

for f in $basedir/* ; 
do
    fn=$(basename $f)
    case "$fn" in
        *.pc)
            cp $f ./$fn
            sed -i "s/@VERSION@/${VERSION}/" $fn
            sed -i "s/@RELEASE@/${RELEASE}/" $fn
            sed -i "s/@RELDATE@/${RELDATE}/" $fn
            echo "edit $fn"
            ;;
        ${name}.spec | ci)
            continue
            ;;
        *)
            ln -s $f .
            echo "ln -s $f ."
            ;;
    esac    
done
ls -l .

cd ..


#make the tar archive, rereferencing symbolic links
tar chf ${tarfile} --exclude-backups ${tardir}
mv ${tarfile} $distdir
ls -l $distdir

cd $startdir
# clean up temp directory
rm -rf $tdir



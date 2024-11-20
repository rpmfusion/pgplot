#!/bin/sh
# collect up all the "base" files into a tar file
# exclude the stuff that gets created during a build

# usage: maketar.sh [version] [release] [releasedate]

# also makes a zip file

name=pgplot
startdir=$(pwd)
me=$(realpath -e -L $0)
distdir=$(dirname $me)
basedir=$(realpath -e -L $distdir/..)
#echo "distdir $distdir"
#echo "basedir $basedir"

VERSION=$1
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
    
RELEASE=$2
if test "x${RELEASE}" = "x"  ;
then
    RELEASE=$(awk '/^Release=/{print $2}' $basedir/${name}.spec | cut -d'%' -f1)
    echo "RELEASE ($RELEASE) from ${name}.spec"
fi

RELDATE=$3
if test "x${RELDATE}" = "x"  ;
then
    RELDATE=$(date -I)
    echo "RELDATE ($RELDATE) from current date"
fi

echo "Version $VERSION Release $RELEASE Date $RELDATE"

tdir=$(mktemp -p "/tmp" -d "${name}DIST_XXXXXXXX")
#echo "tempdir $tdir"
cd $tdir

#directory for dist
nv=${name}-${VERSION}
mkdir ${nv}}

#populate with symbolic links from main code directory
cd ${nv}

for f in $basedir/* ; 
do
    fn=$(basename $f)
    case "$fn" in
        *.pc)
            cp $f .
            sed -i "s/@VERSION@/${VERSION}/" $fn
            sed -i "s/@RELEASE@/${RELEASE}/" $fn
            sed -i "s/@RELDATE@/${RELDATE}/" $fn
            ;;
        *)
            ln -s $f .
            ;;
    esac    
done

cd ..

#GNU makefile 'dist' guideline is that files in the archive
#should have world rx permissions
chmod 0755 -R ${nv}

#make the tar archive, rereferencing symbolic links
tar chzf ${nv}.tgz -X dist.exclude --exclude-backups ${nv}
mv ${nv}.tgz $distdir

zip -r -q ${nv}.zip  ${nv}/ -x\*~ -x\*\# -x\@dist.exclude
mv ${nv}.zip $distdir
cd $startdir
# clean up temp directory
rm -rf $tdir



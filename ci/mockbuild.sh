#!/bin/sh

echo "running $0 $1"
TARFILE=$1
NAME=pgplot
if test "x${TARFILE}" = "x" ;
then
    TARFILE=${NAME}.tgz
fi
echo "tarfile: ${TARFILE}"
VERSION=$(grep '^Version: ' ${NAME}.spec | cut -d ':' -f2 | awk -F'%' '{print $1}' | tr -d ' ')
RELEASE=$(grep '^Release: ' ${NAME}.spec | cut -d ':' -f2 | awk -F'%' '{print $1}' | tr -d ' ')

dnf install -y epel-release
dnf install -y mock

echo "VERSION = ${VERSION}"
echo "RELEASE = ${RELEASE}"

tar xavf ${TARFILE}
# in case tarfile uses a different main directory:
pkgf=$(find . -name pgplot.pc)
SOURCES=$(dirname $x)
mkdir outputs
ls -l
cp ${NAME}.spec ${NAME}.spec.base


# want to use the plain-vanilla pgplot.spec so that
# it's the one that is included in the srpm

BREL="${RELEASE}.alma%{?dist}"
sed "/^Release:/c\
Release:        ${BREL}" <${NAME}.spec.base >${NAME}.spec

config='alma+epel-8-x86_64'
mock -v -r $config  \
     --additional-package=libpng-devel \
     --additional-package=tk-devel \
     --additional-package=libX11-devel \
     --additional-package=gcc-gfortran \
     --additional-package=perl \
     --additional-package=glibc-common \
     --additional-package=openssl \
     --spec=${NAME}.spec \
     --sources=${SOURCES} \
     --resultdir=./outputs -N

cp ${NAME}.spec.base ${NAME}.spec
config='fedora-40-x86_64'
mock -v -r $config \
     --additional-package=libpng-devel \
     --additional-package=tk-devel \
     --additional-package=libX11-devel \
     --additional-package=gcc-gfortran \
     --additional-package=perl \
     --additional-package=glibc-common \
     --additional-package=openssl \
     --spec=${NAME}.spec \
     --sources=${SOURCES} \
     --resultdir=./outputs -N

ls -lR .

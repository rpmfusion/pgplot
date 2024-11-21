#!/bin/sh

NAME=pgplot
VERSION=$(grep '^Version: ' ${NAME}.spec | cut -d ':' -f2 | awk -F'%' '{print $1}' | tr -d ' ')
RELEASE=$(grep '^Release: ' ${NAME}.spec | cut -d ':' -f2 | awk -F'%' '{print $1}' | tr -d ' ')

dnf install -y epel-release
dnf install -y mock

echo "VERSION = ${VERSION}"
echo "RELEASE = ${RELEASE}"
mkdir outputs
cp ../${NAME}.spec ${NAME}.spec.base

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
     --sources=${NAME}-${VERSION}.tgz \
     --resultdir=./outputs -N

cp ${NAME}.spec.base ${NAME}.spec
config='fedora-38-x86_64'
mock -v -r $config \
     --additional-package=libpng-devel \
     --additional-package=tk-devel \
     --additional-package=libX11-devel \
     --additional-package=gcc-gfortran \
     --additional-package=perl \
     --additional-package=glibc-common \
     --additional-package=openssl \
     --spec=${NAME}.spec \
     --sources=${NAME}-${VERSION}.tgz --resultdir=./outputs -N


ls -lR .

#!/usr/bin/bash -l
# Dummy script generated by esm-tools, to be removed later: 
set -e
module --force purge
module use $OTHERSTAGES
module load Stages/2019a
module load Intel/2019.5.281-GCC-8.3.0
module load IntelMPI/2019.6.154
module load CMake
module load Python/3.6.8
module load imkl/2019.3.199

export LC_ALL=en_US.UTF-8
export PROJECT=/p/project/hirace
export FC=mpiifort
export F77=mpiifort
export MPIFC=mpiifort
export FCFLAGS=-free
export CC=mpiicc
export CXX=mpiicpc
export MPIROOT="$(mpiifort -show | perl -lne 'm{ -I(.*?)/include } and print $1')"
export MPI_LIB="$(mpiifort -show |sed -e 's/^[^ ]*//' -e 's/-[I][^ ]*//g')"
export IO_LIB_ROOT=$PROJECT/HPC_libraries/intel2019.3.199_impi2019.6.154_20200703
export PATH=$IO_LIB_ROOT/bin:$PATH
export LD_LIBRARY_PATH=$IO_LIB_ROOT/lib:$LD_LIBRARY_PATH
export SZIPROOT=$IO_LIB_ROOT
export HDF5ROOT=$IO_LIB_ROOT
export HDF5_ROOT=$HDF5ROOT
export NETCDFROOT=$IO_LIB_ROOT
export NETCDFFROOT=$IO_LIB_ROOT
export ECCODESROOT=$IO_LIB_ROOT
export HDF5_C_INCLUDE_DIRECTORIES=$HDF5_ROOT/include
export NETCDF_Fortran_INCLUDE_DIRECTORIES=$NETCDFFROOT/include
export NETCDF_C_INCLUDE_DIRECTORIES=$NETCDFROOT/include
export NETCDF_CXX_INCLUDE_DIRECTORIES=$NETCDFROOT/include
export OASIS3MCT_FC_LIB="-L$NETCDFFROOT/lib -lnetcdff"
export ENVIRONMENT_SET_BY_ESMTOOLS=TRUE


cd nemo-ORCA05_LIM2_KCM_AOW/CONFIG/ORCA05_LIM2_KCM_AOW
echo Compilation is handled by nemobasemodel.yaml
cd ..

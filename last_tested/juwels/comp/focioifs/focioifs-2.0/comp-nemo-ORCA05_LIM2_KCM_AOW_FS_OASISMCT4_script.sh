#!/usr/bin/bash -l
# Dummy script generated by esm-tools, to be removed later: 
set -e
module --force purge
module use $OTHERSTAGES
module load Stages/2020
module load Intel/2020.2.254-GCC-9.3.0
module load ParaStationMPI/5.4.7-1
module load CMake
module load Python/3.8.5
module load imkl/2020.2.254

export LC_ALL=en_US.UTF-8
export PROJECT=/p/project/hirace
export FC=mpifort
export F77=mpifort
export MPIFC=mpifort
export FCFLAGS=-free
export CC=mpicc
export CXX=mpic++
export MPIROOT="$(mpifort -show | perl -lne 'm{ -I(.*?)/include } and print $1')"
export MPI_LIB="$(mpifort -show |sed -e 's/^[^ ]*//' -e 's/-[I][^ ]*//g')"
export IO_LIB_ROOT=$PROJECT/HPC_libraries/intel2020.2.254_parastation_5.4.7-1_20210427
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


cd nemo-ORCA05_LIM2_KCM_AOW_FS_OASISMCT4/CONFIG/ORCA05_LIM2_KCM_AOW_FS_OASISMCT4
echo Compilation is handled by nemobasemodel.yaml
cd ..

#!/usr/bin/bash -l
# Dummy script generated by esm-tools, to be removed later: 
set -e
module purge
module load cmake
module load udunits
module load gribapi/1.28.0
module unload intel.compiler
module load intel.compiler
module unload netcdf
module load hdf5
module load centoslibs cdo nco netcdf/4.6.2_intel
module load automake
module load python3/3.7.7_intel2020u2
module load git
module list
module unload intel.mpi
module load intel.mpi

export LC_ALL=en_US.UTF-8
export FC="mpiifort -mkl"
export F77="mpiifort -mkl"
export MPIFC=mpiifort
export MPICC=mpiicc
export CC=mpiicc
export CXX=mpiicpc
export HDF5ROOT=$HDF5_ROOT
export NETCDFFROOT=$NETCDF_DIR
export NETCDFROOT=$NETCDF_DIR
export NETCDF_Fortran_INCLUDE_DIRECTORIES=$NETCDFROOT/include
export NETCDF_CXX_INCLUDE_DIRECTORIES=$NETCDFROOT/include
export NETCDF_CXX_LIBRARIES=$NETCDFROOT/lib
export PERL5LIB=/usr/lib64/perl5
export LAPACK_LIB="-lmkl_intel_lp64 -lmkl_core -mkl=sequential -lpthread -lm -ldl"
export LAPACK_LIB_DEFAULT="-L/global/AWIsoft/intel/2018/compilers_and_libraries_2018.5.274/linux/mkl/lib/intel64 -lmkl_intel_lp64 -lmkl_core -lmkl_sequential"
export XML2ROOT=/usr
export ZLIBROOT=/usr
export MPIROOT=${I_MPI_ROOT}/intel64
export MPI_LIB=$(mpiifort -show |sed -e 's/^[^ ]*//' -e 's/-[I][^ ]*//g')
export PATH=/work/ollie/jhegewal/sw/cmake/bin:$PATH
export ENVIRONMENT_SET_BY_ESMTOOLS=TRUE


cd echam-6.3.04p1
mkdir -p build; cd build; cmake ..;   make install -j `nproc --all`
cd ..

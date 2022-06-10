cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(ColocZStats)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/ColocZStats")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Xiang Chen (Memorial University of Newfoundland.)")
set(EXTENSION_DESCRIPTION "This is a 3D slicer module for computing the percentage of colocalization(Spatial overlap between different channels) of Z-stack images.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/ColocZStats.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/ColocZStats/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ColocZStats)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(ColocZStats)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/ChenXiang96/SlicerColoc-Z-Stats")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Xiang Chen (Memorial University of Newfoundland), Oscar Meruvia-Pastor (Memorial University of Newfoundland), Touati Benoukraf (Memorial University of Newfoundland)")
set(EXTENSION_DESCRIPTION "This is an extension for computing the percentage of colocalization(Spatial overlap between different channels) of Z-stack images.")
set(EXTENSION_ICONURL "https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/ColocZStats/Resources/Icons/ColocZStats.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Screenshots.png")
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

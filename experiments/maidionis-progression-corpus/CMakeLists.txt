cmake_minimum_required(VERSION 3.24)
project(MousaProgressionCorpus LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
find_package(Torch 2.5.1 EXACT REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
add_subdirectory(${MAIDIONIS_SOURCE} core)
add_executable(progression_model model.cpp)
target_link_libraries(progression_model PRIVATE maidionis_core)

# Separate immutable task compiled from the same music-specific composition.
add_executable(progression_local_model model.cpp)
target_compile_definitions(progression_local_model PRIVATE MOUSA_PROGRESSION_CONTEXT=2)
target_link_libraries(progression_local_model PRIVATE maidionis_core)

cmake_minimum_required(VERSION 4.2)

project(Snacks)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(SnacksTest)

target_sources(SnacksTest
PRIVATE
    main.cpp)
cmake_minimum_required(VERSION 3.0)
project(PokerLib)

set(CMAKE_CXX_STANDARD 11)

add_library(pokerlib SHARED eval.cpp)

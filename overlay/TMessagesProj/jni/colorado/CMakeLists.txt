# Stub: the "colorado" native component is not present in the public
# Cherrygram source. Provide an empty target so tmessages.49 can link.
cmake_minimum_required(VERSION 3.10)

if(NOT TARGET colorado)
    add_library(colorado INTERFACE)
endif()

#!/bin/bash
#Run this in terminal
#+ Command to compile c++ program. here i used common one
g++   -Wall tree.cpp -std=c++11 -O4 -fopenmp 
read -p "Press enter to continue"
./a.out
exit 0
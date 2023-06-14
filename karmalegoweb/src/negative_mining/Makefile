CXX = g++
CXXFLAGS = -O3 -std=c++11
all: NegativeRanges

NegativeRanges: Sequence.o NegativeRanges.o main.o
	$(CXX) $(CXXFLAGS) -o NegativeRanges main.o Sequence.o NegativeRanges.o
	
Sequence.o: Sequence.cpp Sequence.h
	$(CXX) $(CXXFLAGS) -c Sequence.cpp
	
NegativeRanges.o: NegativeRanges.cpp NegativeRanges.h
	$(CXX) $(CXXFLAGS) -c NegativeRanges.cpp
	
main.o: main.cpp
	$(CXX) $(CXXFLAGS) -c main.cpp
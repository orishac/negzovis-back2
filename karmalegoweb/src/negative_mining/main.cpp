#include "NegativeRanges.h"

#include <chrono>
#include <string>
#include <cstring>
using namespace std;
using namespace std::chrono;



int main(int argc, char** argv) {
    //auto start = high_resolution_clock::now();

    char* fout;
    string input;
    ofstream fileout;
    float relative_support;
    int max_gap = 0;
    int max_negative = 0;
    bool allowsame = false;
    bool boundary_constraint = false;
    bool oneforone = false;

    int i = 1;
    while (i < argc) {
        if (!strcmp(argv[i], "-o")) {
            i++;
            fout = argv[i];
        }
        else if (!strcmp(argv[i], "-ms")) {
            i++;
            relative_support = stof(argv[i]);
        }
        else if (!strcmp(argv[i], "-i")) {
            i++;
            input = argv[i];
        }
        else if (!strcmp(argv[i], "-mg")) {
            i++;
            max_gap = stoi(argv[i]);
        }
        else if (!strcmp(argv[i], "-as")) {
            allowsame = true;
        }
        else if (!strcmp(argv[i], "-bc")) {
            boundary_constraint = true;
        }
        else if (!strcmp(argv[i], "-ofo")) {
            oneforone = true;
        }
        else if (!strcmp(argv[i], "-mn")) {
            i++;
            max_negative = stoi(argv[i]);
        }
        i++;
    }

    //auto start = high_resolution_clock::now();

    fileout.open(fout);
    NegativeRanges* nr = new NegativeRanges(relative_support, max_gap, max_negative, allowsame, boundary_constraint, input, true, oneforone, fileout);

    nr->run();

    //auto stop = high_resolution_clock::now();
    //auto duration = duration_cast<microseconds>(stop - start);
    //fileout << duration.count() << endl;
    delete nr;
    return 0;
}

//TODO: Patterns that start with negative events are not correct at the moment. 
//TODO: Multiple negatives doesn't work correctly (missing a few in E-Shop 0.6 for example)
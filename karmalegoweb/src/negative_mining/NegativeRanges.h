#pragma once

#include "Sequence.h"

#include <vector>
#include <string>
#include <unordered_set>
#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;


struct zone {
	vector<tuple<int, int, int, int, int>> curr_range;
	vector<vector<pair<int, int>>> durations; // For each zone in curr_range, for each element in curr_seq. 
	int sup = 0;
	double curr_mean = 0;
	double final_mean = 0;
	int hs = 0;
	vector<double> temp_durations;
	vector<double> temp_gap;
	vector<double> final_durations;
	vector<double> final_gaps;
	void clear() {
		curr_range.clear();
		durations.clear();
		sup = 0;
		curr_mean = 0;
		final_mean = 0;
		hs = 0;
		temp_durations.clear();
		temp_gap.clear();
		final_durations.clear();
		final_gaps.clear();
	}
};

struct transaction {
	vector<int> events;
	transaction(vector<int> evs) {
		events = evs;
	}
	transaction() {};
	int size() { return events.size(); };
	void set_events(vector<int> evs) {
		events = evs;
	}
};

class NegativeRanges {
public:
	float relative_min_sup;
	int min_sup;
	int max_gap;
	bool allow_same;
	bool boundary_constraint;
	bool erase;
	bool oneforone;
	int max_negative;
	string input_file;
	ostream& _os;
	//TODO: Maybe the db should be: unordered_map<int, vector<pair<int,transaction*>>>? 
	//unordered_map<int, map<int, transaction*>> db;
	vector<vector<pair<int, transaction*>>> db;
	//map<int, Sequence*> frequent_positives;
	map<int, map<int, vector<pair<int,transaction*>>>> frequent_positives;
	//set<Sequence*> frequent_negatives;
	set<int> frequent_items;
	map<int, pair<int, int>> sid_ranges;

	Sequence curr_seq;

	vector<tuple<int, int, int, int, int>> read_file(string);
	void set_frequent_items();

	NegativeRanges(float rs, int mg, int mn, bool same, bool boundary, string input_f, bool er, bool ofo, ostream& os) : _os(os) {
		relative_min_sup = rs;
		max_gap = mg;
		allow_same = same;
		boundary_constraint = boundary;
		erase = er;
		oneforone = ofo;
		input_file = input_f;
		max_negative = mn;
	}

	Sequence* create_one_sized_negative(Sequence &);
	void run();
	void project_positive(zone &curr_zone);
	void project_negative(zone &curr_zone);
	//void add_to_set(unordered_map<int, unordered_map<int, set<tuple<int, int>>>>*, tuple<int, int>, int, int);

	double calculate_metrics(zone& curr_zone, Sequence& curr_seq);
	void update_temp_metrics(zone& curr_zone);
	void update_final_metrics(zone& curr_zone);

};

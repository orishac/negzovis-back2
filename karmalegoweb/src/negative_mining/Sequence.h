#pragma once
#include <vector>
#include <set>
#include <iostream>
#include<map>
#include "json.hpp"


using namespace std;

/*struct location {
	int start, end, last_positive;
	// Should it represent the range of the sequence, or the range to scan?
	// Range to scan might be more complicated, as it depends on many different things.
	location(int s, int en, int lp) {
		start = s; end = en; last_positive = lp;
	}
};*/

class Sequence {
public:
	vector<vector<int>> elements;
	vector<bool> negatives;
	vector<tuple<int, int, int>> sequence_range; //End, Last Positive

	int support = 0;
	double mean_horizontal_support = 0;
	double mean_mean_duration = 0;
	double curr_mean = 0;
	vector<double> durations;
	vector<double> gaps;
	int curr_sid = 0;

	Sequence() {};

	Sequence(vector<vector<int>> elems, vector<bool> negs) {
		elements = elems;
		negatives = negs;
	}

	Sequence(Sequence& other) {
		elements = other.elements;
		negatives = other.negatives;

	}
	~Sequence() {
		sequence_range.clear();
		vector<bool>().swap(negatives);
		vector<vector<int>>().swap(elements);
		//sequence_range.clear();
	};
	int get_support();
	void add_new_element(int, bool);
	void add_new_event(int);
	void remove_element();
	void remove_event();
	void add_range(vector<tuple<int, int, int>>&);
	void set_metrics(int, int, double);
	bool all_neg();
	bool operator==(const Sequence&);
	bool operator<(const Sequence&) const;
};

ostream& operator<<(ostream&, Sequence&);





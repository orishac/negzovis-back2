#include "Sequence.h"
#include <algorithm>

using json = nlohmann::json;

bool Sequence::operator==(const Sequence& other) {
	if (this->elements.size() != other.elements.size() || this->negatives.size() != other.negatives.size()) {
		return false;
	}
	for (int i = 0; i < this->elements.size(); i++) {
		if (this->negatives[i] != other.negatives[i]) {
			return false;
		}
		int this_i = 0;
		int other_i = 0;

		while (this_i < this->elements[i].size() && other_i < other.elements[i].size()) {
			if (this->elements[i][this_i] != other.elements[i][other_i]) {
				return false;
			}
			this_i++;
			other_i++;
		}
	}
	return true;
}

bool Sequence::operator<(const Sequence& other) const {
	if (elements.size() != other.elements.size()) {
		return elements.size() < other.elements.size();
	}
	for (int i = 0; i < elements.size(); i++) {
		if (elements[i].size() != other.elements[i].size()) {
			return elements[i].size() < other.elements[i].size();
		}
		if (negatives[i] != other.negatives[i]) {
			return negatives[i];
		}

		int this_i = 0;
		int other_i = 0;

		while (this_i < this->elements[i].size() && other_i < other.elements[i].size()) {
			if (this->elements[i][this_i] != other.elements[i][other_i]) {
				return this->elements[i][this_i] < other.elements[i][other_i];
			}
			this_i++;
			other_i++;
		}
	}
	return false;
}

void Sequence::add_new_element(int elem, bool neg) {
	elements.push_back(vector<int> {elem});
	negatives.push_back(neg);
}

void Sequence::add_new_event(int e) {
	if (elements.back().size() == 0) {
		elements.back() = { e };
		negatives.push_back(true);
	}
	else {
		elements.back().push_back(e);
	}
}

void Sequence::add_range(vector<tuple<int, int, int>>&range) {
	sequence_range = range;
}

bool Sequence::all_neg() {
	return (find(negatives.begin(), negatives.end(), false) == negatives.end());
}

void Sequence::remove_element() {
	elements.pop_back();
	negatives.pop_back();
}

void Sequence::remove_event() {
	(elements.back()).erase(prev(elements.back().end()));
	if (elements.back().size() == 0) {
		negatives.erase(prev(negatives.end()));
	}
}

void Sequence::set_metrics(int sup, int hs, double mmd) {
	support = sup;
	mean_horizontal_support = hs / (double) sup;
	mean_mean_duration = mmd;
}

int Sequence::get_support() {
	return support;
}

ostream& operator<<(ostream& os, Sequence& seq) {
	json j;

	j["elements"] = seq.elements;
	j["negatives"] = seq.negatives;
	j["support"] = seq.support;
	j["mean horizontal support"] = seq.mean_horizontal_support;
	j["mean mean duration"] = seq.mean_mean_duration;
	j["durations"] = seq.durations;
	j["gaps"] = seq.gaps;
	/*os << "pattern: ";

	if (seq.negatives[0]) {
		os << "-";
	}
	os << "(" << (*seq.elements[0].begin());
	for (vector<int>::iterator it = next(seq.elements[0].begin()); it != seq.elements[0].end(); it++) {
		os << "," << (*it);
	}
	os << ")";
	for (int i = 1; i < seq.elements.size(); i++) {
		os << ",";
		if (seq.negatives[i]) {
			os << "-";
		}
		os << "(" << (*seq.elements[i].begin());
		for (vector<int>::iterator it = next(seq.elements[i].begin()); it != seq.elements[i].end(); it++) {
			os << "," << (*it);
		}
		os << ")";
	}
	os << ": " << seq.get_support() << endl;*/
	os << j;
	return os;
}



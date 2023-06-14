#include <algorithm>

#include "NegativeRanges.h"

using namespace std;

//Scans the database and counts the number of transactions that contain each event type.
vector<tuple<int, int, int, int, int>> NegativeRanges::read_file(string input_file) {
	string line;
	ifstream f(input_file.c_str());

	int sid, eid, nitems, event;
	vector<int> events;

	int last_sid = -1;
	vector<tuple<int, int, int, int, int>> range = {};
	while (getline(f, line)) {
		stringstream iss(line.c_str());

		iss >> sid;
		iss >> eid;
		iss >> nitems;

		transaction* curr_t = new transaction();
		pair<int, transaction*> db_entry = { eid, curr_t };

		events.clear();

		if (sid != last_sid) {
			db.push_back(vector<pair<int, transaction*>> {});
			sid_ranges[sid].first = eid;
			if (last_sid != -1) {
				get<0>(range.back()) = db[last_sid].size() - 1;
			}
			range.push_back(tuple<int, int, int, int, int> { make_tuple(-1, 0, sid, 0, 0) });
		}
		sid_ranges[sid].second = eid;

		for (int i = 0; i < nitems; i++) {
			iss >> event;
			events.push_back(event);

			frequent_positives[event][sid].push_back(db_entry);
		}
		curr_t->set_events(events);
		db.back().push_back(db_entry);

		last_sid = sid;
	}
	get<0>(range.back()) = db[last_sid].size() - 1;
	return range;
}

//Checks which of the event types is frequent in relation to the minimum support threshold.
//Important: Non-frequent events are being deleted from the database at this point. This can be done because we still index the timestamps of each event.
void NegativeRanges::set_frequent_items() {
	for (map<int, map<int, vector<pair<int, transaction*>>>>::iterator it = frequent_positives.begin(); it != frequent_positives.end();) {
		if (it->second.size() < min_sup) {
			for (map<int, vector<pair<int, transaction*>>>::iterator sid_it = it->second.begin(); sid_it != it->second.end(); sid_it++) {
				int sid = sid_it->first;
				for (int i = 0; i < sid_it->second.size(); i++) {
					transaction* eid = get<1>(sid_it->second[i]);
					eid->events.erase(find(eid->events.begin(), eid->events.end(), it->first));
					if (eid->events.size() == 0) {
						db[sid].erase(find(db[sid].begin(), db[sid].end(), sid_it->second[i]));
					}
				}
			}
		}
		else {
			frequent_items.insert((*it).first);
		}
		it++;
	}
}

//Algorithm 1 in the paper. 
//Reads the db, finds frequent event types, creates a projection that represent the whole database and calls to Algorithm 2.
void NegativeRanges::run() {
	curr_seq = Sequence();
	zone z;

	z.curr_range = read_file(input_file);
	min_sup = relative_min_sup * db.size();
	set_frequent_items();
	z.sup = 0;
	project_positive(z);
	// TODO: Hide this again when I work on Hepatitis: !!
	if (!boundary_constraint) {
		curr_seq.elements.push_back({});
		project_negative(z);
	}
}

//project_positive represents projections for patterns that end with a positive element. 
//In this case, there are 3 possible expansions: positive composition, positive extension, and negative extension. 
void NegativeRanges::project_positive(zone &curr_zone) {

	zone opt_exten;

	bool positive_expansion = false;
	bool zero_sized_pattern = (curr_seq.elements.size() == 0);
	int last_sid = -1;
	map<int, int> freq;


	for (vector<tuple<int, int, int, int, int>>::iterator proj_it = curr_zone.curr_range.begin(); proj_it != curr_zone.curr_range.end(); proj_it++) {
		int sid = get<2>(*proj_it);
		if (last_sid == sid) { continue; };
		const vector<pair<int, transaction*>> curr_sid = db[sid];
		for (int i = get<1>((*proj_it)) + !zero_sized_pattern; i < curr_sid.size(); i++) {
			for (int j = 0; j < curr_sid[i].second->events.size(); j++) {
				int item = curr_sid[i].second->events[j];
				freq[item] += 1;
			}
		}
		last_sid = sid;
	}

	if (!zero_sized_pattern) {
		int last_item = *curr_seq.elements.back().rbegin();
		for (set<int>::reverse_iterator freq_item = frequent_items.rbegin(); *freq_item > last_item && freq_item != frequent_items.rend(); freq_item++) {
			int expand_item = *freq_item;
			int last_cmps = -1;
			int cmps_sup = 0;
			int proj_track = 0;

			for (vector<tuple<int, int, int, int, int>>::iterator proj_it = curr_zone.curr_range.begin(); proj_it != curr_zone.curr_range.end(); proj_it++) { // For each range in sid that contains the sequence seq
				int sid = get<2>(*proj_it);
				int event_size = db[sid][get<1>(*proj_it)].second->size();
				for (int j = get<3>(*proj_it); j < event_size && db[sid][get<1>(*proj_it)].second->events[j] <= expand_item; j++) { // Possible compositions (iterating through the last element)
					int item = db[sid][get<1>((*proj_it))].second->events[j];
					if (item == expand_item) {

						if (last_cmps != sid) {
							if (last_cmps != -1) {
								update_final_metrics(opt_exten);
							}
							last_cmps = sid;
							cmps_sup += 1;
						}
						opt_exten.curr_range.push_back(tuple<int, int, int, int, int>{make_tuple(get<1>(*proj_it), get<1>(*proj_it), sid, j+1, get<4>(*proj_it))});
						opt_exten.durations.push_back(curr_zone.durations[proj_track]);
						update_temp_metrics(opt_exten);
						break;
					}
				}
				proj_track++;
			}
			if (last_cmps != -1) {
				update_final_metrics(opt_exten);
			}
			if (cmps_sup >= min_sup) {
				curr_seq.add_new_event(expand_item);
				opt_exten.sup = cmps_sup;
				project_positive(opt_exten);
				curr_seq.remove_event();
			}
			opt_exten.clear();
		}
	}


	for (map<int, int>::iterator freq_item_it = freq.begin(); freq_item_it != freq.end(); freq_item_it++) {
		if (curr_seq.elements.size() == 1 && curr_seq.elements[0].size() == 1 && curr_seq.elements[0][0] == 5) {
			int lielle = 2;
		}
		if (freq_item_it->second < min_sup) { continue; };
		int freq_item = freq_item_it->first;

		int last_exten = -1;
		int exten_sup = 0;
		int proj_track = 0;

		for (vector<tuple<int, int, int, int, int>>::iterator proj_it = curr_zone.curr_range.begin(); proj_it != curr_zone.curr_range.end(); proj_it++) { // For each range in sid that contains the sequence seq

			int sid = get<2>(*proj_it);
			int sid_size = this->db[sid].size();
			int pattern_start_eid = get<4>(*proj_it);


			//Condition might vary depends on max gap definition in other algorithms:
			for (int i = get<1>((*proj_it)) + !zero_sized_pattern; i < sid_size && (max_gap == 0 || zero_sized_pattern || db[sid][i].first <= db[sid][get<1>((*proj_it))].first + max_gap); i++) {
				for (int j = 0; j < this->db[sid][i].second->events.size() && db[sid][i].second->events[j] <= freq_item; j++) {
					int item = this->db[sid][i].second->events[j];
					if (item == freq_item) {
						if (last_exten != sid) {
							if (last_exten != -1) {
								update_final_metrics(opt_exten);
							}
							last_exten = sid;
							exten_sup += 1;
						}
						if (zero_sized_pattern) {
							pattern_start_eid = i;
						}
						opt_exten.curr_range.push_back(tuple<int, int, int, int, int> {make_tuple(i, i, sid, j+1, pattern_start_eid) });
						int eid = db[sid][i].first;
						
						if (!zero_sized_pattern) {
							// We need to copy durations[proj_tracker] to our durations vector.
							opt_exten.durations.push_back(curr_zone.durations[proj_track]);
							opt_exten.durations.back().push_back(pair<int, int> {make_pair(eid, eid)});
						}
						else {
							// We append a new duration to our durations vector.
							opt_exten.durations.push_back(vector<pair<int, int>> {make_pair(eid, eid)});

						}
						update_temp_metrics(opt_exten);
						break;
					}
				}
			}
			proj_track++;
		}
		if (last_exten != -1) {
			update_final_metrics(opt_exten);
		}
		if (exten_sup >= min_sup) {
			positive_expansion = true;
			curr_seq.add_new_element(freq_item, false);
			opt_exten.sup = exten_sup;
			project_positive(opt_exten);
			curr_seq.remove_element();
		}
		opt_exten.clear();
	}


	if (!zero_sized_pattern && (!boundary_constraint || (boundary_constraint && positive_expansion))) {
		for (set<int>::iterator freq_item = frequent_items.begin(); freq_item != frequent_items.end(); freq_item++) {

			int last_exten = -1;
			int exten_sup = 0;
			int proj_track = 0;
			for (vector<tuple<int, int, int, int, int>>::iterator proj_it = curr_zone.curr_range.begin(); proj_it != curr_zone.curr_range.end(); proj_it++) { // For each range in sid that contains the sequence seq
				bool found = false;
				int sid = get<2>(*proj_it);
				int lastp_eid = db[sid][get<1>((*proj_it))].first;

				//Condition might vary depends on max gap definition in other algorithms:
				for (int i = get<1>((*proj_it)) + 1; (i < db[sid].size()) && (max_gap == 0 || db[sid][i].first <= lastp_eid + max_gap); i++) {
					for (int j = 0; j < db[sid][i].second->events.size() && db[sid][i].second->events[j] <= *freq_item; j++) {
						int item = db[sid][i].second->events[j];
						int eid = db[sid][i].first;
						if (item == *freq_item) {
							if (!found) {
								if (oneforone && (eid == lastp_eid + 1)) {
									found = true;
									continue;
								}
								else {
									if (last_exten != sid) {
										if (last_exten != -1) {
											update_final_metrics(opt_exten);
										}
										last_exten = sid;
										exten_sup += 1;
									}
									opt_exten.curr_range.push_back(tuple<int, int, int, int, int> { make_tuple(eid - 1, get<1>((*proj_it)), sid, 0, get<4>((*proj_it))) });
									// TODO: Make sure that this is the correct range:
									opt_exten.durations.push_back(curr_zone.durations[proj_track]);
									// TODO: This is probably wrong because it's an index and not an EID: 
									opt_exten.durations.back().push_back(pair<int, int> {make_pair(lastp_eid + 1, eid - 1)});
									update_temp_metrics(opt_exten);
									found = true;
								}
							}
							break;
						}
					}
				}
				if (!found && lastp_eid < get<1>(sid_ranges[sid])) {
					if (last_exten != sid) {
						if (last_exten != -1) {
							update_final_metrics(opt_exten);
						}
						last_exten = sid;
						exten_sup += 1;
					}
					opt_exten.curr_range.push_back(tuple<int, int, int, int, int> {make_tuple(db[sid].back().first - 1, get<1>(*proj_it), sid, 0, get<1>((*proj_it)))});
					opt_exten.durations.push_back(curr_zone.durations[proj_track]);
					// TODO: Make sure that this is the correct range:
					opt_exten.durations.back().push_back(pair<int, int> {make_pair(lastp_eid + 1, get<1>(sid_ranges[sid]))});
					update_temp_metrics(opt_exten);
					found = true;
				}
				proj_track++;
			}
			if (last_exten != -1) {
				update_final_metrics(opt_exten);
			}
			if (exten_sup >= min_sup) {
				positive_expansion = true;
				curr_seq.add_new_element(*freq_item, true);
				opt_exten.sup = exten_sup;
				project_negative(opt_exten);
				curr_seq.remove_element();
			}
			opt_exten.clear();
		}
	}
	//TODO: Divide everything by the vertical support (instead of this function):
	double mean_mean_duration = calculate_metrics(curr_zone, curr_seq);
	curr_seq.set_metrics(curr_zone.sup, curr_zone.curr_range.size(), mean_mean_duration);
	if (curr_seq.elements.size() > 0) {
		_os << curr_seq << endl;
	}
	return;
}


//project_negative represents projections for patterns that end with a negative zone. 
//In this case, there are 2 possible expansions: positive extension and negative composition. 
//If the pattern is composed of negative events only, marked as all_neg, then discovering a positive candidate cand does not prevent the algorithm for scanning
//the rest of the projections for other occurrences of cand for negative composition. 
void NegativeRanges::project_negative(zone& curr_zone) {

	bool zero_sized_pattern = (curr_seq.elements.back().size() == 0);

	zone opt_exten;
	
	bool all_neg = curr_seq.all_neg();
	int dist = 1;
	if (!oneforone) {
		dist = 0;
	}

	bool positive_expansion = false;

	if (!zero_sized_pattern) {

		int last_sid = -1;
		map<int, int> freq;

		for (vector<tuple<int, int, int, int, int>>::iterator proj_it = curr_zone.curr_range.begin(); proj_it != curr_zone.curr_range.end(); proj_it++) {
			int sid = get<2>(*proj_it);
			if (last_sid == sid) { continue; };
			const vector<pair<int, transaction*>> curr_sid = db[sid];
			for (int i = get<1>((*proj_it)) + 1; i < curr_sid.size(); i++) {
				for (int j = 0; j < curr_sid[i].second->events.size(); j++) {
					int item = curr_sid[i].second->events[j];
					freq[item] += 1;
				}
			}
			last_sid = sid;
		}

		for (map<int, int>::iterator freq_item = freq.begin(); freq_item != freq.end(); freq_item++) {


			if (freq_item->second < min_sup) { continue; };
			if (!allow_same && (find(curr_seq.elements.back().begin(), curr_seq.elements.back().end(), freq_item->first) != curr_seq.elements.back().end())) {
				continue;
			}

			int expand_item = freq_item->first;

			int last_exten = -1;
			int exten_sup = 0;
			int proj_track = 0;

			for (vector<tuple<int, int, int, int, int>>::iterator proj_it = curr_zone.curr_range.begin(); proj_it != curr_zone.curr_range.end(); proj_it++) { // For each range in sid that contains the sequence seq

				int sid = get<2>(*proj_it);

				bool skip = false;
				int start_range = get<1>(*proj_it);
				int i = get<1>(*proj_it);
				int lastp_eid;
				int end_eid = get<0>(*proj_it);
				int last_seen = -1;

				if (db[sid].size() == 0) { skip = true; };
				if (i == -1) {
					lastp_eid = 0;
					i = 0;
				}
				else {
					lastp_eid = db[sid][start_range].first;
					i += 1;
				}


				if (!skip) {

					//Condition might vary depends on max gap definition in other algorithms:
					while (i != this->db[sid].size() && (db[sid][i].first <= end_eid + 1) && (max_gap == 0 || curr_seq.elements.size() == 0 || all_neg || db[sid][i].first < lastp_eid + max_gap + 1)) { //TODO: Do we need to check max_gap in case of all_neg? What happenes if it's all_neg? (I think I deleted it because there is no all_neg here)
						int eid = db[sid][i].first;
						for (int j = 0; j < db[sid][i].second->events.size() && db[sid][i].second->events[j] <= expand_item; j++) { //Look through all events in the element. 

							int item = db[sid][i].second->events[j];

							if (item == expand_item && eid - lastp_eid > dist) { 
								if (last_exten != sid) {
									if (last_exten != -1) {
										update_final_metrics(opt_exten);
									}
									last_exten = sid;
									exten_sup += 1;
								}
								opt_exten.curr_range.push_back(tuple<int, int, int, int, int> { make_tuple(i, i, sid, j + 1, get<4>((*proj_it))) });
								opt_exten.durations.push_back(curr_zone.durations[proj_track]);
								get<1>(opt_exten.durations.back().back()) = eid - 1;
								opt_exten.durations.back().push_back(pair<int, int> {make_pair(eid, eid)});
								update_temp_metrics(opt_exten);
								break;
							}
						}
						i++;
					}
				}

				proj_track++;
			}
			if (last_exten != -1) {
				update_final_metrics(opt_exten);
			}

			if (exten_sup >= min_sup) {

				positive_expansion = true;
				curr_seq.add_new_element(expand_item, false);
				opt_exten.sup = exten_sup;
				project_positive(opt_exten);
				curr_seq.remove_element();
			}
			opt_exten.clear();
		}
	}
	
	if ((!boundary_constraint || positive_expansion) && (max_negative == 0 || curr_seq.elements.back().size() < max_negative)) {

		int last_item;
		if (zero_sized_pattern){
			last_item = -1;
		}
		else {
			last_item = *curr_seq.elements.back().rbegin();
		}
		for (set<int>::reverse_iterator freq_item = frequent_items.rbegin();  freq_item != frequent_items.rend() && *freq_item > last_item; freq_item++) {

			int expand_item = *freq_item;
			int last_exten = -1;
			int exten_sup = 0;

			int proj_track = 0;


			for (vector<tuple<int, int, int, int, int>>::iterator proj_it = curr_zone.curr_range.begin(); proj_it != curr_zone.curr_range.end(); proj_it++) { // For each range in sid that contains the sequence seq
				int sid = get<2>(*proj_it);

				bool skip = false;
				int start_range = get<1>(*proj_it) - zero_sized_pattern;
				int i = get<1>(*proj_it) - zero_sized_pattern;
				int lastp_eid;
				int end_eid = get<0>(*proj_it);
				int last_seen = -1;

				if (db[sid].size() == 0) { skip = true; };
				if (i == -1) {
					lastp_eid = 0;
					i = 0;
				}
				else {
					lastp_eid = db[sid][start_range].first;
				}
				if (!all_neg) {
					i += 1;
				}
				else {
					end_eid = db[sid][get<0>(*proj_it)].first;
				}
				if (!skip) {
					while (i < this->db[sid].size() && (db[sid][i].first <= end_eid + 1) && (max_gap == 0 || curr_seq.elements.size() == 0 || all_neg || db[sid][i].first < lastp_eid + max_gap)) { //TODO: Do we need to check max_gap in case of all_neg? What happenes if it's all_neg? (I think I deleted it because there is no all_neg here)
						int eid = db[sid][i].first;
						for (int j = 0; j < db[sid][i].second->events.size() && db[sid][i].second->events[j] <= expand_item; j++) { //Look through all events in the element. 

							int item = db[sid][i].second->events[j];
							if (item == expand_item) { 

								if (oneforone && (eid <= lastp_eid + 1)) { 
									last_seen = i;
								}

								if (last_seen == -1) {

									if (last_exten != sid) {
										if (last_exten != -1) {
											update_final_metrics(opt_exten);
										}
										last_exten = sid;
										exten_sup += 1;
									}
									opt_exten.curr_range.push_back(tuple<int, int, int, int, int> { make_tuple(eid - 1, start_range, sid, 0, last_seen + 1) });
									// TODO: These two are probably wrong:
									if (!zero_sized_pattern) {
										opt_exten.durations.push_back(curr_zone.durations[proj_track]);
										get<1>(opt_exten.durations.back().back()) = eid - 1;
									}
									else {
										opt_exten.durations.push_back(vector<pair<int, int>> {make_pair(db[sid][0].first, eid - 1)});
									}
									update_temp_metrics(opt_exten);
									last_seen = i;
								}
								else if (all_neg) {
									int last_seen_eid = db[sid][last_seen].first;
									if (eid - last_seen_eid > dist) {

										if (last_exten != sid) {
											if (last_exten != -1) {
												update_final_metrics(opt_exten);
											}
											last_exten = sid;
											exten_sup += 1;
										}
										opt_exten.curr_range.push_back(tuple<int, int, int, int, int> { make_tuple(eid - 1, last_seen, sid, 0, last_seen + 1) });
										if (!zero_sized_pattern) {
											opt_exten.durations.push_back(curr_zone.durations[proj_track]);
											get<0>(opt_exten.durations.back().back()) = last_seen_eid + 1;
											get<1>(opt_exten.durations.back().back()) = eid - 1;
										}
										else {
											opt_exten.durations.push_back(vector<pair<int, int>> {make_pair(last_seen_eid + 1, eid - 1)});
										}
										update_temp_metrics(opt_exten);
									}
									last_seen = i;

								}
								break;
							}
						}
						i++;
					}
				}
				if (last_seen == -1) {
					if (last_exten != sid) {
						if (last_exten != -1) {
							update_final_metrics(opt_exten);
						}
						last_exten = sid;
						exten_sup += 1;
					}
					opt_exten.curr_range.push_back(tuple<int, int, int, int, int> { make_tuple(get<0>(*proj_it), start_range, sid, 0, get<4>(*proj_it)) });
					if (!zero_sized_pattern) {
						opt_exten.durations.push_back(curr_zone.durations[proj_track]);
					}
					else {
						// TODO: This gives -1 to 0 which is wrong. 
						opt_exten.durations.push_back(vector<pair<int, int>> {make_pair(db[sid][0].first, db[sid].back().first)});
					}
					update_temp_metrics(opt_exten);
				}
				// TODO: Is this condition correct? Check when it enters here and if it's right. 
				else if (all_neg && end_eid - db[sid][last_seen].first > 1) {
					if (last_exten != sid) {
						if (last_exten != -1) {
							update_final_metrics(opt_exten);
						}
						last_exten = sid;
						exten_sup += 1;
					}
					opt_exten.curr_range.push_back(tuple<int, int, int, int, int> { make_tuple(get<0>(*proj_it), last_seen, sid, 0, last_seen + 1) });
					if (!zero_sized_pattern) {
						opt_exten.durations.push_back(curr_zone.durations[proj_track]);
						get<1>(opt_exten.durations.back().back()) = end_eid - 1;
						// TODO: last_seen?
						get<0>(opt_exten.durations.back().back()) = db[sid][last_seen].first + 1;
					}
					else {
						//end_eid = db[sid][end_eid].first;
						opt_exten.durations.push_back(vector<pair<int, int>> {make_pair(db[sid][last_seen].first + 1, end_eid)});
					}
					update_temp_metrics(opt_exten);
				}
				proj_track++;
			}

			if (last_exten != -1) {
				update_final_metrics(opt_exten);
			}
			if (exten_sup >= min_sup) {
				curr_seq.add_new_event(expand_item);
				opt_exten.sup = exten_sup;
				project_negative(opt_exten);
				curr_seq.remove_event();
			}
			opt_exten.clear();
		}
	}

	if (!boundary_constraint && !zero_sized_pattern) {
		//TODO: Divide everything by the vertical support (instead of this function):
		double mean_mean_duration = calculate_metrics(curr_zone, curr_seq);
		curr_seq.set_metrics(curr_zone.sup, curr_zone.curr_range.size(), mean_mean_duration);
		_os << curr_seq << endl;
	}

	return;
}

double NegativeRanges::calculate_metrics(zone& curr_zone, Sequence& curr_seq) {

	curr_seq.durations.clear();
	curr_seq.gaps.clear();

	for (int i = 0; i < curr_zone.final_durations.size(); i++) {
		curr_seq.durations.push_back(curr_zone.final_durations[i] / (double)curr_zone.sup);
		if (i < curr_zone.final_gaps.size()) {
			curr_seq.gaps.push_back(curr_zone.final_gaps[i] / (double)curr_zone.sup);
		}
	}

	return curr_zone.final_mean / (double)curr_zone.sup;
}


void NegativeRanges::update_temp_metrics(zone& curr_zone)
{
	curr_zone.curr_mean += curr_zone.durations.back().back().second - curr_zone.durations.back().begin()->first + 1;
	curr_zone.hs += 1;

	if (curr_zone.temp_durations.size() == 0) {
		curr_zone.temp_durations = vector<double>(curr_zone.durations.back().size());
		curr_zone.temp_gap = vector<double>(curr_zone.durations.back().size() - 1);
	}

	int i = 0;
	for (vector<pair<int, int>>::iterator it = curr_zone.durations.back().begin(); it != curr_zone.durations.back().end(); it++) {
		curr_zone.temp_durations[i] += (it->second - it->first + 1);

		if (i > 0) {
			curr_zone.temp_gap[i - 1] += (it->first - prev(it, 1)->second - 1);
		}

		i++;
	}
}

void NegativeRanges::update_final_metrics(zone& curr_zone)
{
	curr_zone.final_mean += curr_zone.curr_mean / (double)curr_zone.hs;

	if (curr_zone.final_durations.size() == 0) {
		curr_zone.final_durations = vector<double>(curr_zone.durations.back().size());
		curr_zone.final_gaps = vector<double>(curr_zone.durations.back().size() - 1);
	}

	int i = 0;
	for (vector<pair<int, int>>::iterator it = curr_zone.durations.back().begin(); it != curr_zone.durations.back().end(); it++) {
		curr_zone.final_durations[i] += curr_zone.temp_durations[i] / (double)curr_zone.hs;

		if (i > 0) {
			curr_zone.final_gaps[i - 1] += curr_zone.temp_gap[i-1] / (double)curr_zone.hs;
		}

		i++;
	}

	curr_zone.hs = 0;
	curr_zone.temp_durations.clear();
	curr_zone.temp_gap.clear();

	//TODO: Added this, make sure I didn't make a mistake here:
	curr_zone.curr_mean = 0;
}

from itertools import islice

""" This class is the searching class for searching tirps in the index file
    the constructor gets the path to the output of the RawDataToIndexFile object"""
class SearchInIndexFile:

    _index_file = None

    _main_map_dic = None
    _vs_map_dic = None
    _m_hs_list = None

    _START_INDEX = 0
    _END_INDEX = 1

    _START_INDEX_OF_TIRPS = 3

    _MIN_VERTICAL_SUPPORT_DEFAULT = 0
    _MAX_VERTICAL_SUPPORT_DEFAULT = 100
    _MIN_MEAN_HORIZONTAL_SUPPORT_DEFAULT = 1
    _MAX_MEAN_HORIZONTAL_SUPPORT_DEFAULT = float('inf')


    """ The constructor gets the path to the index file a set all the relvent data bases for the search 
        main_map_dic - dictionary that contains pairs of the sym and the first line that contains the relevant data
        vs_map_dic - dictionary that contains pairs of the vertical support(divided by 5) value and the line of the relevant data
        hs_list - list that contains tipels of the mean horizontal support value(fixed size buckets) and the first line of the relevant data"""
    def __init__( self , path ):

        self._index_file = open( path , 'r' )

        self._main_map_dic = {}
        self._vs_map_dic = {}
        self._m_hs_list = []

        self.create_map_dictionaries()
        self.creat_m_hs_list()

    """ This function creates the main_map_dic and the vs_map_dic """
    def create_map_dictionaries( self ):

        self.set_parsed_map_line( self._main_map_dic , 0 )
        prev = self.set_parsed_map_line( self._vs_map_dic , self._main_map_dic["VS"][self._START_INDEX] )
        # adds the last line of the vs section
        self._vs_map_dic[prev][self._END_INDEX] = self._main_map_dic["VS"][self._END_INDEX]

    """ This function build a given dictionary from a given index of a line """
    def set_parsed_map_line( self , dest_dic , index ):

        map_line = next( self.get_iter_lines( index , index + 1 ) ).split( " " )
        prev = None

        for pair in map_line:
            split_pair = pair.split( ":" )
            dest_dic[split_pair[0]] = [int( split_pair[1] )]
            if prev != None:
                dest_dic[prev] += [int( split_pair[1] )]
            prev = split_pair[0]

        dest_dic[prev] += [None]
        return prev

    """ This function creats the _m_hs_list as discribed above """
    def creat_m_hs_list(self):

        lst = next(self.get_iter_lines(self._main_map_dic["HS"][self._START_INDEX]))[:-1].split( " " )
        for str in lst:
            pair = str.split( ":" )
            self._m_hs_list += [( float( pair[0] ) , int( pair[1] ) )]

    """ This function gets a property: 's'/'c'/'e' and a sym as a string and returns a list of all the relevant tirps 
        see doc of the RawDataToIndexFile object for more information on the property """
    def get_tirps_by_property( self , prop , sym ):

        if not sym in self._main_map_dic:
            return []
        lines = self.get_iter_lines( self._main_map_dic[sym][self._START_INDEX] \
                                    , self._main_map_dic[sym][self._END_INDEX] + 1 )

        tirps_to_return = []
        for tirps_str in lines:
            # always add thr tirp in size 1 contains only the single symbol
            # if tirps_str[0] == "s":
            #     tirp_size = tirps_str.split(',')[2]
            #     if int(tirp_size) == 1:
            #         tirps_to_return.append((tirps_str[self._START_INDEX_OF_TIRPS:][:-1].split(" "))[0])

            if tirps_str[0] == prop:
                tirps_to_return = tirps_to_return + tirps_str[self._START_INDEX_OF_TIRPS:][:-1].split( " " )
                return tirps_to_return

    """ This function returns all the tirps that their vertical support is between the given numbers """
    def get_tirps_by_vs( self , min_vs = _MIN_VERTICAL_SUPPORT_DEFAULT , \
                                max_vs = _MAX_VERTICAL_SUPPORT_DEFAULT ):

        if min_vs < 0 or min_vs > 100 or max_vs < 0 or max_vs > 100:
            return []
        r_min_vs = self.divided_by_five_round( min_vs )
        r_max_vs = self.divided_by_five_round( max_vs )
        if r_min_vs > int(list(self._vs_map_dic)[-1]):#######################3
            return []

        for i in range( r_min_vs , r_max_vs + 1 , 5 ):
            if str( i ) in self._vs_map_dic.keys():
                r_min_vs = str( i )
                break

        for i in range( r_max_vs , int( r_min_vs ) - 1 , -5 ):
            if str( i ) in self._vs_map_dic.keys():
                r_max_vs = str( i )
                break

        tirps_line_iter = self.get_iter_lines( self._vs_map_dic[r_min_vs][self._START_INDEX] , \
                                               self._vs_map_dic[r_max_vs][self._END_INDEX] )
        return self.lines_to_tirps_list( tirps_line_iter , min_vs / 100 , max_vs / 100 )

    """ This function returns all the tirps that their mean horizontal support is between the given numbers """
    def get_tirps_by_hs( self , min_m_hs = _MIN_MEAN_HORIZONTAL_SUPPORT_DEFAULT , \
                                max_m_hs = _MAX_MEAN_HORIZONTAL_SUPPORT_DEFAULT ):

        if min_m_hs < 1 or max_m_hs < 1 or len( self._m_hs_list ) < 1:
            []

        min_hs_line = self._m_hs_list[0][1]
        max_hs_line = None

        for tup in self._m_hs_list:
            if tup[0] > min_m_hs:
                break
            min_hs_line = tup[1]

        for tup in self._m_hs_list:
            if tup[0] > max_m_hs:
                max_hs_line = tup[1]
                break

        trips_line_iter = self.get_iter_lines( min_hs_line , max_hs_line )
        return self.lines_to_tirps_list( trips_line_iter , min_m_hs , max_m_hs )

    """ This function gets a number of lines from the file and returns a list of all the tirps in those lines
        min_value\max_value - in case the line represent a line of vs or m_hs these variables is used to select only the relevant tirps"""
    def lines_to_tirps_list( self , lines , min_value = 0.0 , max_value = _MAX_MEAN_HORIZONTAL_SUPPORT_DEFAULT ):
        tirps_list = []
        for line in lines:
            line = line[:-1]
            splited_line = line.split( " " )
            if min_value <= float ( splited_line[0][:-1] ) and max_value >= float ( splited_line[0][:-1] ):
                splited_line.pop( 0 )
                tirps_list += splited_line
        return tirps_list

    """ This function returns an iterable object that contains the lines between s_index to e_index
        e_index - is optional the defult is the end of the file """
    def get_iter_lines( self , s_index , e_index = None ):

        self._index_file.seek(0)
        return islice( self._index_file , s_index , e_index )

    """ This function rounding down the given number to a number that divisible by 5 """
    def divided_by_five_round( self , num ):

        return int( num / 5 ) * 5

    """ This function sets the default min vertical support"""
    def setMinVS(self, vs):
        self._MIN_VERTICAL_SUPPORT_DEFAULT = vs
    
    def get_all_tirps(self, symbols):
        tirps = []
        for sym in symbols:
                tirps += self.get_tirps_by_property( "s" , sym )

    """ This function search for the tirps that meets all the conditions
        start_sym\contains_sym\end_sym - a list of all the symbols the tirps can start\contains\ends with
        min_vs\max_vs - min\max vertical support
        min_m_hs\max_m_hs - min\max mean horizontal support"""
    def get_serached_tirps( self , start_sym , contains_sym , end_sym , min_vs = 0 , max_vs = 100 , \
                            min_m_hs = _MIN_MEAN_HORIZONTAL_SUPPORT_DEFAULT , max_m_hs = _MAX_MEAN_HORIZONTAL_SUPPORT_DEFAULT,
                            need_to_filter_start=False, need_to_filter_contains=False, need_to_filter_end=False ):

        starts_with_tirps = []
        contains_tirps = []
        ends_with_tirps = []
        all_lists = []

        if len(start_sym) > 0: ##########
            for sym in start_sym:
                starts_with_tirps += self.get_tirps_by_property( "s" , sym )
            starts_with_tirps = list( dict.fromkeys( starts_with_tirps ) )
            all_lists.append( starts_with_tirps )

        if len(contains_sym) > 0:
            for sym in contains_sym:
                contains_tirps += self.get_tirps_by_property( "c" , sym )
            contains_tirps = list( dict.fromkeys( contains_tirps ) )
            all_lists.append( contains_tirps )

        if len(end_sym) > 0:
            for sym in end_sym:
                ends_with_tirps += self.get_tirps_by_property( "e" , sym )
            ends_with_tirps = list( dict.fromkeys( ends_with_tirps ) )
            all_lists.append( ends_with_tirps )
        # score change
        # if min_vs and max_vs:
        #     all_lists.append( self.get_tirps_by_vs( min_vs , max_vs ) )
        #
        # if min_m_hs:
        #     if not max_m_hs:
        #         max_m_hs = self._MAX_MEAN_HORIZONTAL_SUPPORT_DEFAULT
        #     all_lists.append( self.get_tirps_by_hs( min_m_hs , max_m_hs ) )
        return self.get_combaind_list(all_lists, need_to_filter_start, need_to_filter_contains, need_to_filter_end)
        # if need_to_filter:
        #     return self.get_combaind_list( all_lists )
        # else:
        #     return self.get_combaind_union_list(all_lists)

    """ This function gets a list of lists and returns one united and sorted list 
        that contains the intersection between the given lists
        empty list is ignored"""
    def get_combaind_list( self , lists, need_to_filter_start, need_to_filter_contains, need_to_filter_end ):
        #############
        if [] in lists:
            return []

        while [] in lists:
            lists.remove( [] )

        if len( lists ) < 1:
            return []

        starts_list = lists[0]
        contains_list = lists[1]
        ends_list = lists[2]

        if not (need_to_filter_start or need_to_filter_contains or need_to_filter_end):
            combaind_list = list(set(starts_list) | set(contains_list) | set(ends_list))
        else:
            # need to filter at leasy by one section
            combaind_list = list(set(starts_list) | set(contains_list) | set(ends_list)) # initialize combained by all tirps
            if need_to_filter_start:
                combaind_list = list(set(starts_list) & set(combaind_list))
            if need_to_filter_contains:
                combaind_list = list(set(contains_list) & set(combaind_list))
            if need_to_filter_end:
                combaind_list = list(set(ends_list) & set(combaind_list))

        return combaind_list
            

        # if need_to_filter_start or need_to_filter_contains or need_to_filter_end:
        #     combaind_list = list(set(starts_list) & set(contains_list) & set(ends_list))
        # else:
        #     combaind_list = list(set(starts_list) | set(contains_list) | set(ends_list))

        # combaind_list.sort( key = lambda tirp : ( tirp.replace( "(" , "" ).split( "-" )[:-1]  ) )
        # return combaind_list


    def get_combaind_union_list(self, lists):
        if [] in lists:
            return []

        while [] in lists:
            lists.remove( [] )

        if len( lists ) < 1:
            return []

        combaind_list = lists[0]
        for lst in lists:
            combaind_list = list( set(combaind_list) | set(lst) )
        combaind_list.sort( key = lambda tirp : ( tirp.replace( "(" , "" ).split( "-" )[:-1]  ) )
        return combaind_list
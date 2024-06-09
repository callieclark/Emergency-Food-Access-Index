#Author: Callie Clark (callieclark@nyu.edu)
#Last updated 6/8/2023


from scipy.spatial import cKDTree
import numpy as np
import networkx as nx
import pandas as pd
import multiprocessing

def get_time_table_id(fp_df):
    """
    Function looks at food pantry schedule and list open food pantries for each time period in dictionary format

    Parameters
    ----------
    fp_df(df): pass in dataframe of food pantry schedule


     Returns
    -------
    open_fp_dict (dictionary) with schedule as keys and corresponding nodes of open food pantries as values

    """
    open_fp_dict={}
    for dow in ['Mo','Tu','We','Th','Fr','Sa','Su']:
        open_fp_dict[dow+'_period_1']= fp_df[(fp_df[dow+'_open']<=9.5) & (fp_df[dow+'_close']>=6.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)].index.values

        open_fp_dict[dow+'_period_2']=fp_df[(fp_df[dow+'_open']<=13.5) & (fp_df[dow+'_close']>=10.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)].index.values

        open_fp_dict[dow+'_period_3']=fp_df[(fp_df[dow+'_open']<=17.5) & (fp_df[dow+'_close']>=14.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)].index.values

        open_fp_dict[dow+'_period_4']=fp_df[(fp_df[dow+'_open']<=21.5) & (fp_df[dow+'_close']>=18.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)].index.values
        
    return open_fp_dict


def get_time_table(fp_df):
    """
    Function looks at food pantry schedule and list open food pantries for each time period in dictionary format

    Parameters
    ----------
    fp_df(df): pass in dataframe of food pantry schedule


     Returns
    -------
    open_fp_dict (dictionary) with schedule as keys and corresponding nodes of open food pantries as values

    """
    open_fp_dict={}
    for dow in ['Mo','Tu','We','Th','Fr','Sa','Su']:
        open_fp_dict[dow+'_period_1']= fp_df[(fp_df[dow+'_open']<=9.5) & (fp_df[dow+'_close']>=6.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)]['node'].values

        open_fp_dict[dow+'_period_2']=fp_df[(fp_df[dow+'_open']<=13.5) & (fp_df[dow+'_close']>=10.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)]['node'].values #this does not guarantee an hour

        open_fp_dict[dow+'_period_3']=fp_df[(fp_df[dow+'_open']<=17.5) & (fp_df[dow+'_close']>=14.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)]['node'].values

        open_fp_dict[dow+'_period_4']=fp_df[(fp_df[dow+'_open']<=21.5) & (fp_df[dow+'_close']>=18.5)&(fp_df[dow+'_close']-fp_df[dow+'_open']>=0.5)]['node'].values

    return open_fp_dict


def ckdnearest(gdA, gdB,k_nearest=5): #identifies clostes k food pantries to each census tranct
    """
    Function identifies closest k food pantries to each census tract

    Parameters
    ----------
    gdA(df): census_df
    gdB(df): fp_df_open
    k_nearest(int): number specifying how many nearest food pantries to CT to identify

    Returns
    -------
    idx(list):returns the indexes of the k_nearest food pantry to each census tract. Format is list of length CT where each element is a list of length k of index values corresponding to the FP df

    """

    if k_nearest==0:
        idx=[None]*len(gdA)

    else:
        nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
        nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
        btree = cKDTree(nB)
        dist, idx = btree.query(nA, k=k_nearest)#returns the index of gdB that is closest to GDA

    return idx

def map_time_period_to_speed_weight(time_period,mode='Drive'):

    """
    Function maps time period string to string specifying weight for evaluating drive speed

    Parameters
    ----------
    time_period(str):string with time of day information, pulled from dictionary value

    mode(str): (Drive,Bike,Walk)--> weight only varies for drive due to rush hour, other modes only have one weight

     Returns
    -------
    weight (str): string that allows mapping to uber drive time

    """

    if mode=='Drive':
        if 'period_1' in time_period:
            weight='before_work_tt'
        elif 'period_2' in time_period:
            weight='morning_tt'
        elif 'period_3' in time_period:
            weight='afternoon_tt'
        elif 'period_4' in time_period:
            weight='evening_tt'
    else:
        weight='urban_tt'

    return weight


def calculate_tt(G,node_df,idx_nearest,fp_df,centroid_node,weight,time_period,df_tt,county_dict,mode):
    """
    Function calculates the TT and identifies the closest node for all CTs in a given time period

    Parameters
    ----------
    G(osmnx graph): pass in osmnx graph with adjusted travel times
    idx_nearest(list of lists): k_nearest fp nodes to each CT
    fp_df(df): fp dataframe filtered by what is open
    centroid_node(list): list of centroid nodes
    weight(str): travel time weight to use
    time_period(str): name of time_period for labeling columns
    df_tt(dF): dataframe the results are populating
    county_dict (dictionary): dictionary with map of nodes (str) to county name (str)


     Returns
    -------
    df_tt(df): returns df_tt with two added columns specifying closest node and TT for the time period passed in


    """
    print('Starting ',time_period)
    count=0
    for i in centroid_node:
        #print(i)

        if np.shape(idx_nearest)==(len(centroid_node),) and (idx_nearest[0]==None):
            df_tt.loc[i,time_period+'_tt']=None
            df_tt.loc[i,time_period+'_nearest']=None
            return df_tt
        my_array=[]
        if np.shape(idx_nearest[count])==(): #takes into account when there is only one fp and its not a list
            nearest_nodes=list(fp_df.iloc[[idx_nearest[count]]]['node'].values) #changes with each loop

        else:
            nearest_nodes=list(fp_df.iloc[idx_nearest[count]]['node'].values) #changes with each loop

        if (len(nearest_nodes)==1) and (nearest_nodes[0]==None):
            df_tt.loc[i,time_period+'_tt']=None
            df_tt.loc[i,time_period+'_stops']=None

        county_name=county_dict[i]
        for j in nearest_nodes:
            arr = nx.shortest_path_length(G, i, j, weight)  #try osmnx with multiple cpus
            
            if mode=='Drive':
                route_nodes=nx.shortest_path(G, i, j, weight)
                delay, num_delays=add_intersection_delays_multiple(node_df,route_nodes,time_period,county_name,mode)
                my_array.append(arr+delay)
            else:
                my_array.append(arr)


        count+=1
        
        #print('nearest_nodes',nearest_nodes)
        #print('my array',my_array)
        
        nearest_node=pd.DataFrame(my_array,nearest_nodes).idxmin().values[0]
        
        #print('nearest node selected',nearest_node)
        
       # print('tts',round((pd.DataFrame(my_array,nearest_nodes).min().values[0])/60,2),round(pd.DataFrame(data=[nearest_nodes, my_array],index=['node','tt']).T.sort_values(by='tt').head(n=3).tt.mean()/60,2))
        df_tt.loc[i,time_period+'_nearest']=nearest_node
        df_tt.loc[i,time_period+'_tt']=round((pd.DataFrame(my_array,nearest_nodes).min().values[0])/60,2) #convert to minutes
        df_tt.loc[i,time_period+'_tt_3']=round(pd.DataFrame(data=[nearest_nodes, my_array],index=['node','tt']).T.sort_values(by='tt').head(n=3).tt.mean()/60,2)
        
    print('Finished ',time_period)
    df_tt.to_csv('~/travel_time_df/inter/df_tt_+'+mode+'_'+time_period+'.csv')
        


    return df_tt


# def make_tt_df(G,node_df,fp_df,census_df,county_dict,mode,k_nearest):

#     """
#     Function calls all relevant function to format a result df of travel times and nearest nodes

#     Parameters
#     ----------
#     G(osmnx graph): pass in osmnx graph with adjusted travel times
#     fp_df(df): fp dataframe
#     census_df(df):census tract df
#     county_dict(dictionary): map of nodes (str) to county name (str)
#     k_nearest(int): number of surrounding FPs to calculate shortest path to for each CT
#     mode(str): (Drive,Bike,Walk)--> to allow varying mode-specific details
#      Returns
#     -------
#     df_tt(df): df with all CT nodes in index and two columns fore each time period labeld as "day_TOD_nearest_node" and "day_TOD_tt"

#     """
#     centroid_node=census_df['node'].values
#     df_tt = pd.DataFrame(index=centroid_node)
#     open_fp_dict=get_time_table(fp_df)


#     for time_period in open_fp_dict.keys():  #add multiprocessing 

#         print(time_period)
#         weight=map_time_period_to_speed_weight(time_period,mode)
#         print(weight)
#         fp_node=list(open_fp_dict[time_period])
#         fp_df_open=fp_df.loc[fp_df['node'].isin(fp_node)]#index fp_df based on open FPs

#         df_tt[time_period+'_nearest']=None
#         df_tt[time_period+'_tt']=None
#         #To do add a None value if nothing is open
#         #idx_nearest=ckdnearest(census_df, fp_df_open,min(k_nearest,len(fp_node)))
#         idx_nearest=ckdnearest(census_df, fp_df_open, min(k_nearest,len(fp_node)))
#         df_tt=calculate_tt(G,node_df,idx_nearest,fp_df_open,centroid_node,weight,time_period,df_tt,county_dict,mode)

#         df_tt.to_csv('~/travel_time_df/df_tt_inter_'+mode+'_'+str(k_nearest)+'.csv')

#     return df_tt


def process_time_period(time_period,open_fp_dict, centroid_node,G, node_df, fp_df, census_df, county_dict, mode, k_nearest):
    
    """
    Function uses multiprocessing and calls all 28 time periods at the same time 

    Parameters
    ----------
    timeperiod: (str) time period label
    open_fp_dict:result of function called in make_tt_df
    centorid_node:result of function called in make_tt_df
    G(osmnx graph): pass in osmnx graph with adjusted travel times
    fp_df(df): fp dataframe
    census_df(df):census tract df
    county_dict(dictionary): map of nodes (str) to county name (str)
    k_nearest(int): number of surrounding FPs to calculate shortest path to for each CT
    mode(str): (Drive,Bike,Walk)--> to allow varying mode-specific details
     Returns
    -------
    df_tt(df): df for each time period 

    """
    weight = map_time_period_to_speed_weight(time_period, mode)
    fp_node = list(open_fp_dict[time_period])
    fp_df_open = fp_df.loc[fp_df['node'].isin(fp_node)]
    df_tt = pd.DataFrame(index=centroid_node)
    df_tt[time_period + '_nearest'] = None
    df_tt[time_period + '_tt'] = None
    idx_nearest = ckdnearest(census_df, fp_df_open, min(k_nearest, len(fp_node)))
    df_tt = calculate_tt(G, node_df, idx_nearest, fp_df_open, centroid_node, weight, time_period, df_tt, county_dict, mode)
    return df_tt

def make_tt_df(G, node_df, fp_df, census_df, county_dict, mode, k_nearest):
    
    """
    Function calls all relevant function to format a result df of travel times and nearest nodes

    Parameters
    ----------
    G(osmnx graph): pass in osmnx graph with adjusted travel times
    fp_df(df): fp dataframe
    census_df(df):census tract df
    county_dict(dictionary): map of nodes (str) to county name (str)
    k_nearest(int): number of surrounding FPs to calculate shortest path to for each CT
    mode(str): (Drive,Bike,Walk)--> to allow varying mode-specific details
     Returns
    -------
    df_tt(df): df with all CT nodes in index and two columns fore each time period labeld as "day_TOD_nearest_node" and "day_TOD_tt"

    """
    centroid_node = census_df['node'].values
    df_tt = pd.DataFrame(index=centroid_node)
    open_fp_dict = get_time_table(fp_df)

    #with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    with multiprocessing.Pool(processes=28) as pool:
    
        results = [pool.apply_async(process_time_period, args=(time_period,open_fp_dict,centroid_node, G, node_df, fp_df, census_df, county_dict, mode, k_nearest)) for time_period in open_fp_dict.keys()]
        for result in results:
            df_tt_partial = result.get()
            df_tt = pd.concat([df_tt, df_tt_partial], axis=1)

    return df_tt

def add_intersection_delays(node_df,route_nodes,mode):
    """
    Function calculates delay in seconds based on number of nodes with a stop light

    Parameters
    ----------
    route_nodes(list): all nodes along selected shortest route

    mode(str): (Drive,Bike,Walk)--> to allow varying mode-specific details

    Returns
    -------
    delay(int): number of seconds of delay expected due to stop lights
    """
    #To Do: vary p based on mode or TOD
    #p(float):probability of hitting a stop light, can vary by mode and TOD
    if mode=='Drive':
        drive_coeff=22.15 #0.4 for sim
        intersections=sum((node_df.loc[route_nodes,'highway']=='traffic_signals')*1)
        delay=intersections*drive_coeff


    else:
        intersections=sum((node_df.loc[route_nodes,'highway']=='traffic_signals')*1)
        delay=0





    return delay, intersections

def add_intersection_delays_multiple(node_df,route_nodes,time_period,county_name,mode):
    """
    Function calculates delay in seconds based on number of nodes with a stop light

    Parameters
    ----------
    node_df (geodataframe): df with osmid and geodata on all the street nodes
    route_nodes(list): all nodes along selected shortest route

    mode(str): (Drive,Bike,Walk)--> to allow varying mode-specific details

    time_period (str): name of column and used for multi linear regression coeffs

    county_name (str): name of county, used to apply coeff

    Returns
    -------
    delay(int): number of seconds of delay expected due to stop lights
    """

    county_coeff_map={'Bronx':2.2942,'Queens':2.7802,'Staten Island':0,'Brooklyn':1.8529,'Manhattan':0.8645 }

    intersections=sum((node_df.loc[route_nodes,'highway']=='traffic_signals')*1)
    if mode=='Drive':
        is_weekday, tod_categorical_0,tod_categorical_1,tod_categorical_3=get_attributes(time_period)
        delay=intersections*0.2278+is_weekday*0.5807+tod_categorical_0*0.2969+tod_categorical_1*-0.6575+tod_categorical_3*-0.5725+1*county_coeff_map[county_name]
        delay=delay*60

    else:
        delay=0
    return delay, intersections


def get_attributes(time_period):
    """
    Function takes in time_period string and parses out associated data

    Parameters
    ----------
    time_period(str): str of day + TOD

    Returns
    -------
    is_weekend(int):0 or 1 indicating if it is the weekend (sa,Su)
    tod_categorical_0(int): 1 if it is "before work", 0 else
    tod_categorical_1 (int): 1 if it is morning. 0 else
    """
    if 'Sa' in time_period:
        is_weekday=0
    elif 'Su' in time_period:
        is_weekday=0
    else:
        is_weekday=1


    if '_1' in time_period:
        tod_categorical_0=1
        tod_categorical_1=0
        tod_categorical_3=0
    elif '_2' in time_period:
        tod_categorical_0=0
        tod_categorical_1=1
        tod_categorical_3=0

    elif '_4' in time_period:
        tod_categorical_0=0
        tod_categorical_1=0
        tod_categorical_3=1

    else:
        tod_categorical_0=0
        tod_categorical_1=0
        tod_categorical_3=0



    return is_weekday, tod_categorical_0,tod_categorical_1,tod_categorical_3

#!/usr/bin/env python

# Author: Santiago Toro
import random
import mitreattack.navlayers as navlayers
from mitreattack.navlayers.manipulators.layerops import LayerOps
from mitreattack.navlayers.core.layer import Layer


# Function to get the list of Data Types (Data Sources or Data Components)
def get_dt_list(attack, data_type):
    return attack[data_type].value_counts().to_frame().reset_index()

# Function to get the Techniques per Data Type (Data Source or Data Component)
def get_t_by_dt(attack, data_type, data_type_value):
    return attack[attack[data_type] == data_type_value]


# Function to create layer for a Specific Data Type Value
def get_layer_for_dtv(attack, data_type, data_type_value):

    t_by_dtv = attack[attack[data_type] == data_type_value]
    thisdict = {}
    dic_list_by_dt = []
    
    for ind in t_by_dtv.index:
        thisdict["techniqueID"] = t_by_dtv['technique_id'][ind]
        thisdict["score"] = 1
        thisdict["comment"] = data_type_value
        dic_list_by_dt.append(thisdict)
        thisdict = {}

    return create_layer(dic_list_by_dt, data_type, data_type_value)


# Function to create layer by Data Type (Data Source or Data Component)
def create_layer(dic_list_by_dt, data_type, data_type_value):

    layer_example = navlayers.Layer()

    layer_name = "Techniques by {} - {}".format(data_type, data_type_value)

    layer_example.from_dict(dict(name=layer_name, domain="enterprise-attack"))  # arguments required for every layer

    # configure the versions object
    layer_example.layer.versions = dict(layer="4.2", attack="9.1", navigator="4.2")

    # set a description
    #layer_example.layer.description = "This is a Layer which groups the techniques for a Specific Data Source - {}".format(data_s)

    # configure the "filters" object
    #layer_example.layer.filters = dict(platforms=['macOS'])  # platforms can be provided during initialization
    #layer_example.layer.filters.platforms = ['Windows']  # or separately

    # configure the 'sorting' setting
    #layer_example.layer.sorting = 3  # 0: sort ascending alphabetically by technique name
    # 1: sort descending alphabetically by technique name
    # 2: sort ascending by technique score
    # 3: sort descending by technique score

    # configure the layout object
    #layer_example.layer.layout = dict(layout="side",
    #                                  showID=True,
    #                                  showName=True,
    #                                  showAggregateScores=True,
    #                                  countUnscored=True,
    #                                  aggregateFunction="sum")  # average, sum, max, min

    # configure whether or not to hide disabled techniques
    layer_example.layer.hideDisabled = True
    # configure the gradient object
    layer_example.layer.gradient = dict(minValue=0, maxValue=50,
                                        colors=["#DAF7A6", "#FFC300", "#C70039", "#581845"])
    # configure collection of legend items 
    #layer_example.layer.legendItems = [dict(label='A', color='#DAF7A6'), dict(label='B', color='#581845')]
    # configure collection of metatdata values
    #layer_example.layer.metadata = [dict(name='example metadata', value='This is an example')]
    # create listing of techniques in this layer
    #layer_example.layer.techniques = [dict(techniqueID='T1000', tactic='privilege-escalation', score=15, color='#AABBCC'),
    #                                  dict(techniqueID='T1000.1', tactic='privilege-escalation', score=1, comment='Demo')]

    layer_example.layer.techniques = dic_list_by_dt

    return layer_example


# Function to to get combined layer by Data Type (Data Source or Data Component)
def get_layer_by_dt(attack, dt_list, data_type):

    list_of_layers = []
    score = 1
    for data_v in dt_list:
        t_by_dt = attack[attack[data_type] == data_v]
        dic_list_by_dt = []    
        for ind in t_by_dt.index:
            thisdict = {}
            thisdict["techniqueID"] = t_by_dt['technique_id'][ind]
            thisdict["score"] = score
            thisdict["comment"] = data_v
            dic_list_by_dt.append(thisdict)
            thisdict = {}
        #score = score + 1
        ds_layer = create_layer(dic_list_by_dt, data_type, data_v)
        #filename = "layer_t_for_ds_{}.json".format(data_v)
        #ds_layer.to_file(filename)
        list_of_layers.append(ds_layer)

    lo = LayerOps(score=lambda x: sum(x),
              comment=lambda x: ' - '.join(x),
              name=lambda x: "This is a combined Layer by {}".format(data_type),
              default_values= {
                "score": 0
                })   
    out_layer = lo.process(list_of_layers)
    
    return out_layer
import boto3
import os
import time
import logging
import json

def get_active_contexts(intent_request):
    try:
        return intent_request['sessionState'].get('activeContexts')
    except:
        return []
        
def remove_inactive_context(context_list):
    if not context_list:
        return context_list
    new_context = []
    for context in context_list:
        time_to_live = context.get('timeToLive')
        if  time_to_live and time_to_live.get('turnsToLive') != 0:
            new_context.append(context)
    return new_context
    
def set_slot(slotname, slotvalue, intent):
    if slotvalue == None:
        intent['slots'][slotname] = None
    else:
        intent['slots'][slotname] = {
                "value": {
                "interpretedValue": slotvalue,
                "originalValue": slotvalue,
                "resolvedValues": [
                    slotvalue
                ]
            }
        }
    return intent
    
def elicit_slot(active_contexts, session_attributes,intent,slotToElicit,messages):
    intent['state']= 'InProgress'

    if not session_attributes:
        session_attributes = {}
    session_attributes['previous_message'] = json.dumps(messages)
    session_attributes['previous_dialog_action_type'] = "ElicitSlot"
    session_attributes['previous_slot_to_elicit'] = None
    session_attributes['previous_intent'] = intent['name']
    
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'activeContexts': active_contexts,
            'dialogAction': {
                'type': "ElicitSlot",
                'slotToElicit': slotToElicit
            },
            'intent': intent
        },
        'requestAttributes': {},
     'messages': messages
    }
    
def elicit_intent(active_contexts, session_attributes, intent, messages):
    intent['state']= 'Fulfilled'

    if not session_attributes:
        session_attributes = {}
    session_attributes['previous_message'] = json.dumps(messages)
    session_attributes['previous_dialog_action_type'] = 'ElicitIntent'
    session_attributes['previous_slot_to_elicit'] = None
    session_attributes['previous_intent'] = intent['name']
    
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'activeContexts': active_contexts,
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            "state": "Fulfilled"
        },
        'requestAttributes': {},
     'messages': messages
    }
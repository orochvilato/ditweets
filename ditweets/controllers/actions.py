#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from ditweets import app
import pickle
actions_path = os.path.join(app.app_path,'actions')
if not os.path.exists(actions_path):
    os.makedirs(actions_path)

def add_action(action):
    import uuid
    action_id = str(uuid.uuid4())
    pickle.dump(action,open(os.path.join(actions_path,action_id),'wb'))
    return action_id

def del_action(action_id):
    action_path = os.path.join(actions_path,action_id)
    if os.path.exists(action_path):
        os.remove(action_path)
        return True
    else:
        return False
def update_action(action_id,action):
    action_path = os.path.join(actions_path,action_id)
    if os.path.exists(action_path):
        pickle.dump(action,open(action_path,'wb'))
        return True
    else:
        return False

def get_action(action_id):
    action_path = os.path.join(actions_path,action_id)
    if os.path.exists(action_path):
        return pickle.load(open(action_path,'rb'))
    else:
        return None

def get_actions():
    actions = {}
    for id in os.listdir(actions_path):
        action = get_action(id)
        action.update(id=id)
        actions[id] = action
    return actions

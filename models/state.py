class State:

    @staticmethod
    def state_local_generate():
        # Here we directly use the "user_session" global variable
        # As using the "session_get()" function returns the following error:
        # 'staticmethod' object is not callable
        global user_session
        if user_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            website_states = models_database.DB.db_user_export_websites(db_file, user_session['client_id'])
            wordpress_states = {}
            backup_states = {}
            notification_states = {}
            temp_time = datetime.datetime.utcnow()
            now = temp_time.strftime("%b-%d-%Y-%H:%M")
            if None not in [website_states, wordpress_states, backup_states, notification_states]:
                result_dict = {
                    "client_id": user_session['client_id'],
                    "last_update": now,
                    "session_id": user_session['session_id'],
                    "client_ip": user_session['client_ip'],
                    "website_states": website_states,
                    "wordpress_states": wordpress_states,
                    "backup_states": backup_states,
                    "notification_states": notification_states
                }
            else:
                return {
                    "Response": "Error",
                    "Message": "One of the states is not set!"
                }
        return result_dict

    @staticmethod
    def state_local_get():
        current_session = session_get()
        if current_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            result = models_database.DB.db_user_state_get(db_file, current_session['client_id'])
            return result

    @staticmethod
    def state_local_set(state_obj: dict):
        current_session = session_get()
        if current_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            if state_obj is not None:
                result = models_database.DB.db_user_state_set(db_file, state_obj)
                if result:
                    return {
                        "Response": "Success",
                        "Message": "State saved successfully"
                    }
                else:
                    return {
                        "Response": "Error",
                        "Message": "State not saved"
                    }

    @staticmethod
    def state_cluster_get():
        current_session = session_get()
        if current_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            url = __cluster_url__ + "/state/get"
            result = requests.post(url, json={"client_id": current_session['client_id']})
            if result:
                current_cluster_state = result.json()
                temp = State.state_local_get()
                current_local_state = json.loads(temp[0][0])
                cluster_update = datetime.datetime.strptime(current_cluster_state['last_update'], '%b-%d-%Y-%H:%M')
                local_update = datetime.datetime.strptime(current_local_state['last_update'], '%b-%d-%Y-%H:%M')
                # Here we check if the State on the Cluster is older
                if cluster_update < local_update:
                    # If the State is older:
                    # TODO: We're here in the development process
                    # Here we need to send a POST request to the Cluster and provide the local state
                    # So the State on the server can be updated
                    url2 = __cluster_url__ + "/state/set"
                    json_data = {}
                    json_data['state_obj'] = current_local_state
                    result2 = requests.post(url2, json=json_data)
                    if result2:
                        return result2.json()
                    else:
                        message = "The State for user [" + current_session['client_id'] + "] was not properly set on the Cluster"
                        return{
                            "Response": "Failure",
                            "Message": message
                        }
                else:
                    result = State.state_local_set(current_cluster_state)
                    result["Info"] = "Changed the local State"
                    return result
            else:
                return {
                    "Response": "Error",
                    "Message": "No state found for the [" + current_session['client_id'] + "] user"
                }
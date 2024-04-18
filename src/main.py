import json
from datetime import datetime, timedelta


def TopXSimpleLTVCustomers(x, D):
    dates_list = [datetime.strptime(i["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z") for i in D]
    week_range = abs(max(dates_list) - min(dates_list)).days // 7

    agg_dict = {}
    for i in D:
        if "customer_id" in i:
            customer_id = i["customer_id"]
            week_id = datetime.strptime(i["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z").isocalendar().week
            visit = 1 if i["type"] == "SITE_VISIT" else 0
            conversion = 1 if i["type"] == "ORDER" else 0
            revenues = float(i["total_amount"].strip("USD")) if i["type"] == "ORDER" else 0.0
            if customer_id not in agg_dict:
                agg_dict[customer_id] = {}
                agg_dict[customer_id][week_id] = {"visits": visit, "conversions": conversion, "revenue": revenues}
            else:
                if week_id not in agg_dict[customer_id]:
                    agg_dict[customer_id][week_id] = {"visits": visit, "conversions": conversion, "revenue": revenues}
                else:
                    agg_dict[customer_id][week_id]["visits"] += visit
                    agg_dict[customer_id][week_id]["conversions"] += conversion
                    agg_dict[customer_id][week_id]["revenue"] += revenues
    print(agg_dict)


def ingest(e, data):
    data = {"customers": {}}
    if e["file_path"]:
        file_path = e["file_path"]
        json_data = file_load(file_path)
    for event in json_data:
        customer_id = event["customer_id"] if "customer_id" in event else event["key"]
        event_date = datetime.strptime(event["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z")
        week_id = event_date - timedelta(days=event_date.weekday() + 1)

        if event["type"] == "CUSTOMER" and event["verb"] == "NEW":
            customer_data = {"created_at": event_date, "last_name": event["last_name"],
                             "address": {"city": event["adr_city"], "state": event["adr_state"]},
                             "events": {"visits": [], "conversions": [], "action": []}}
            data["customers"][customer_id] = customer_data
        if event["type"] == "SITE_VISIT" and event["verb"] == "NEW":
            event_data = {"key": event["key"], "effective_date": event_date, "week_id": week_id, "tags": event["tags"]}
            data["customers"][customer_id]["events"]["visits"].append(event_data)
        if event["type"] == "ORDER" and event["verb"] == "NEW":
            revenue = float(event["total_amount"].strip("USD"))
            event_data = {"key": event["key"], "effective_date": event_date, "week_id": week_id, "amount": revenue}
            data["customers"][customer_id]["events"]["conversions"].append(event_data)
        if event["type"] == "IMAGE" and event["verb"] == "UPLOAD":
            action_type = "image uplaod"
            action_data = {'camera_make': event["camera_make"], 'camera_model': event["camera_model"]}
            event_data = {"key": event["key"], "effective_date": event_date, "week_id": week_id,
                          "event_type": action_type, "action_data": action_data}
            data["customers"][customer_id]["events"]["action"].append(event_data)

    json_extract = json.dumps(data, default=str)
    full_dataset_path = "../output/full_dataset.json"
    save_file(full_dataset_path, json_extract)

    return data


def file_load(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

def save_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)
    return data


def main():
    data = ingest({"file_path": "../input/input_events.txt"}, None)
    # print(data)
    # TopXSimpleLTVCustomers(1, data)


if __name__ == "__main__":
    main()

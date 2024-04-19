import json
from datetime import datetime, timedelta


def get_date_ranges(data):
    dates_list = [datetime.strptime(i["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z") for i in data]
    min_week = min(dates_list) - timedelta(days=min(dates_list).weekday() + 1)
    max_week = max(dates_list) + timedelta(days=max(dates_list).weekday() + 1)
    week_range = abs(max_week - min_week).days // 7
    return week_range


def TopXSimpleLTVCustomers(x, data):
    # print(data[])
    min_date = None,
    max_date = None
    ltv = {}
    # for k,v in data.items():
    #     print(k)
    #     print(v)
    #
    #     ltv[k] = {}

    # dates_list = [datetime.strptime(i["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z") for i in D]
    # week_range = abs(max(dates_list) - min(dates_list)).days // 7
    #
    # agg_dict = {}
    # for i in D:
    #     if "customer_id" in i:
    #         customer_id = i["customer_id"]
    #         week_id = datetime.strptime(i["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z").isocalendar().week
    #         visit = 1 if i["type"] == "SITE_VISIT" else 0
    #         conversion = 1 if i["type"] == "ORDER" else 0
    #         revenues = float(i["total_amount"].strip("USD")) if i["type"] == "ORDER" else 0.0
    #         if customer_id not in agg_dict:
    #             agg_dict[customer_id] = {}
    #             agg_dict[customer_id][week_id] = {"visits": visit, "conversions": conversion, "revenue": revenues}
    #         else:
    #             if week_id not in agg_dict[customer_id]:
    #                 agg_dict[customer_id][week_id] = {"visits": visit, "conversions": conversion, "revenue": revenues}
    #             else:
    #                 agg_dict[customer_id][week_id]["visits"] += visit
    #                 agg_dict[customer_id][week_id]["conversions"] += conversion
    #                 agg_dict[customer_id][week_id]["revenue"] += revenues
    # print(agg_dict)


def ingest(e, data):
    weekly_event_range = 0
    raw_data = None
    if e["file_path"]:
        file_path = e["file_path"]
        raw_data = file_load(file_path)
    weekly_event_range = get_date_ranges(raw_data)
    data = {"batch_range in weeks": weekly_event_range, "customers": {}}
    event_count = {}

    for event in raw_data:
        customer_id = event["customer_id"] if "customer_id" in event else event["key"]
        event_date = datetime.strptime(event["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z").date()
        week_id = str(event_date - timedelta(days=event_date.weekday() + 1))

        if event["type"] == "CUSTOMER":
            update_date = event_date if event["verb"] == "UPDATE" else None
            customer_data = {"created_at": event["event_time"], "updated_at": update_date, "last_name": event["last_name"],
                             "address": {"city": event["adr_city"], "state": event["adr_state"]},
                             "events": []}
            data["customers"][customer_id] = customer_data

            event_count[customer_id] = {}
        if event["type"] == "SITE_VISIT":
            event_data = {"type": "visit", "key": event["key"], "effective_date": event["event_time"], "week_id": week_id,
                          "tags": event["tags"]}
            data["customers"][customer_id]["events"].append(event_data)

            if week_id not in event_count[customer_id]:
                counter_init = {"visits": 1, "revenues": 0}
                event_count[customer_id][week_id] = counter_init
            else:
                event_count[customer_id][week_id]["visits"] += 1
        if event["type"] == "ORDER":
            update_date = event_date if event["verb"] == "UPDATE" else None
            event_type = "order" if event["verb"] == "NEW" else "order_update"
            revenues = float(event["total_amount"].strip("USD"))
            event_data = {"type": event_type, "key": event["key"], "effective_date": event["event_time"], "updated_date": update_date, "week_id": week_id,
                          "amount": revenues}
            data["customers"][customer_id]["events"].append(event_data)

            if week_id not in event_count[customer_id]:
                counter_init = {"visits": 0, "revenues": revenues}
                event_count[customer_id][week_id] = counter_init
            else:
                event_count[customer_id][week_id]["revenues"] = event_count[customer_id][week_id]["revenues"] + revenues
        if event["type"] == "IMAGE":
            action_data = {"camera_make": event["camera_make"], "camera_model": event["camera_model"]}
            event_data = {"type": "image upload", "key": event["key"], "effective_date": event_date, "week_id": week_id,
                          "action_data": action_data}
            data["customers"][customer_id]["events"].append(event_data)

    full_dataset_path = "../output/full_dataset.json"
    json_data = json.dumps(data, default=str)
    save_file(full_dataset_path, json_data)

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
    TopXSimpleLTVCustomers(1, data)


if __name__ == "__main__":
    main()

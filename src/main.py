import json
from datetime import datetime, timedelta


def get_date_ranges(data):
    dates_list = [datetime.strptime(i["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z") for i in data]
    min_week = min(dates_list) - timedelta(days=min(dates_list).weekday() + 1)
    max_week = max(dates_list) + timedelta(days=max(dates_list).weekday() + 1)
    # setting a minimum of one week
    week_range = abs(max_week - min_week).days // 7 if max_week > min_week else 1
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
    # Loading data file based on the file_path paramater existance in the event data
    raw_data = None
    if e["file_path"]:
        file_path = e["file_path"]
        raw_data = file_load(file_path)

    # Calculating the number of weeks in the dataset
    weekly_event_range = get_date_ranges(raw_data)
    data = {"customers": {}}
    event_count = {}


    for event in raw_data:
        customer_id = event["customer_id"] if "customer_id" in event else event["key"]
        event_date = datetime.strptime(event["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z").date()
        week_id = str(event_date - timedelta(days=event_date.weekday() + 1))

        # Since this is a client value oriented analysis, Customer is the main grouping for the dataset
        # For better performance event_counter is added to create data averages per client within the same `for` loop
        if event["type"] == "CUSTOMER":
            update_date = event_date if event["verb"] == "UPDATE" else None
            customer_data = {"created_at": event["event_time"], "updated_at": update_date, "last_name": event["last_name"],
                             "address": {"city": event["adr_city"], "state": event["adr_state"]}, "visits": [], "images": {}, "orders": {}}
            data["customers"][customer_id] = customer_data

            event_count[customer_id] = {}

        # Registering Client visits
        if event["type"] == "SITE_VISIT":
            event_data = {"Page_id": event["key"], "effective_date": event["event_time"], "tags": event["tags"]}
            data["customers"][customer_id]["visits"].append(event_data)

            # building a per week event counter to calculate averages
            if week_id not in event_count[customer_id]:
                counter_init = {"visits": 1, "revenues": 0}
                event_count[customer_id][week_id] = counter_init
            else:
                event_count[customer_id][week_id]["visits"] += 1

        # Registering orders, if an order's revenues were updated, it would be considered as revenues for the week of the update
        if event["type"] == "ORDER":
            order_id = event["key"]
            revenues = float(event["total_amount"].strip("USD"))
            revenues_diff = None
            if event["verb"] == "NEW":
                event_data = {"order_date": event["event_time"], "update_date": None, "amount": revenues}
                data["customers"][customer_id]["orders"][order_id] = event_data

                # TODO: there is a way to combine both UPDATE and NEW order Counter calculation to a single if, but,
                #  it would be less readable

                # building a per week event counter to calculate averages - new order
                if week_id not in event_count[customer_id]:
                    counter_init = {"visits": 0, "revenues": revenues}
                    event_count[customer_id][week_id] = counter_init
                else:
                    event_count[customer_id][week_id]["revenues"] = event_count[customer_id][week_id][
                                                                        "revenues"] + revenues

            else:
                event_data = {"update_date": event["event_time"], "amount": revenues}
                data["customers"][customer_id]["orders"][order_id].update(event_data)

                # building a per week event counter to calculate averages - order update
                revenues_diff = revenues - data["customers"][customer_id]["orders"][order_id]["amount"]
                if revenues_diff != 0:
                    if week_id not in event_count[customer_id]:
                        counter_init = {"visits": 0, "revenues": revenues_diff}
                        event_count[customer_id][week_id] = counter_init
                    else:
                        event_count[customer_id][week_id]["revenues"] = event_count[customer_id][week_id][
                                                                        "revenues"] + revenues_diff

        # registering image uploads
        if event["type"] == "IMAGE":
            image_id = event["key"]
            camera_data = {"camera_make": event["camera_make"], "camera_model": event["camera_model"]}
            event_data = {"upload_date": event_date, "camera_data": camera_data}
            data["customers"][customer_id]["images"][image_id] = event_data

    # calculating averages per week
    stats = {}
    for ck,cv in event_count.items():
        stats[ck] = {}

        total_weekly_rev = 0
        total_visits = 0
        for wk, wv in event_count[ck].items():

            total_weekly_rev = total_weekly_rev + wv["revenues"]/wv["visits"]
            total_visits = total_visits + wv["visits"]
        stats_data = {"weekly_rev_per_visits_revenue": total_weekly_rev/weekly_event_range, "weekly_average_visits": total_visits/weekly_event_range}
        data["customers"][ck]["stats"] = stats_data

    full_dataset_path = "../output/full_dataset.json"
    json_data = json.dumps(data, default=str)
    save_file(full_dataset_path, json_data)
    #
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

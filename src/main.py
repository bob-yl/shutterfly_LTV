import ast
from datetime import datetime


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
    if data["file_path"]:
        file_path = data["file_path"]
        with open(file_path) as f:
            data = ast.literal_eval(f.read())

    return data


def main():
    data = ingest(None, {"file_path": "../input/input_events.txt"})
    # print(data)
    TopXSimpleLTVCustomers(1, data)


if __name__ == "__main__":
    main()

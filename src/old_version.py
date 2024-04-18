import json
from datetime import datetime


def get_week_delta(dates_list):
    return abs(max(dates_list) - min(dates_list)).days // 7


def agg_LTV_values(data):
    agg_dict = {}
    for i in data:
        if "customer_id" in i:
            customer_id = i["customer_id"]
            visit = 1 if i["type"] == "SITE_VISIT" else 0
            revenues = float(i["total_amount"].strip("USD")) if i["type"] == "ORDER" else 0.0
            if customer_id not in agg_dict:
                agg_dict[customer_id] = {"visits": visit, "revenues": revenues}
            else:
                agg_dict[customer_id]["visits"] += visit
                agg_dict[customer_id]["revenues"] += revenues
    return agg_dict


def TopXSimpleLTVCustomers(x, D):
    week_count = get_week_delta([datetime.strptime(i["event_time"], "%Y-%m-%dT%H:%M:%S.%f%z") for i in D])

    agg_dict = agg_LTV_values(D)
    result = {}
    for k, v in agg_dict.items():
        result[k] = (((v["revenues"] / v["visits"]) * v["visits"]) / week_count) * 520

    sorted(result.items(), reverse=True)

    return list(result.keys())[:x]


def ingest(e, data):
    if e["file_path"]:
        file_path = e["file_path"]
        with open(file_path) as f:
            data = json.load(f)

    return data

def save_to_file(file_path, data):
    with open(file_path, 'wt') as file:
        file.write("\n".join(data))


def main():
    data = ingest({"file_path": "../input/input_events.txt"}, None)
    result = TopXSimpleLTVCustomers(1, data)
    save_to_file('../output/results.txt', result)


if __name__ == "__main__":
    main()

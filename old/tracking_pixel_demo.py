from src.classification.tracking import check_for_tracking_pixels


if __name__ == "__main__":
    browser_data_path = "tmp/schooltogo.de_legal/browser_data_log.jsonl"
    network_requests_path = "tmp/schooltogo.de_legal/network_requests.json"

    issues = check_for_tracking_pixels(browser_data_path, network_requests_path)
    print(issues)

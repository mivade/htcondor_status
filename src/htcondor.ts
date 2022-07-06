import { DateTime } from "luxon";
import { Tabulator } from "tabulator-tables";

const statusMap = {
  1: "Idle",
  2: "Running",
  3: "Removed",
  4: "Completed",
  5: "Held",
  6: "Transferring Output",
  7: "Suspended"
};

/**
 * @brief Format the `QDate` parameter from HTCondor
 * @param timestamp Number of seconds since the epoch
 * @returns Formatted timestamp
 */
export function formatQDate(timestamp: number): string {
  return DateTime.fromSeconds(timestamp).toISO();
}

/**
 * @brief Format the job status number into a human-friendly string
 * @param status
 * @returns Formatted job status
 */
export function formatJobStatusString(status: number): string {
  return statusMap[status];
}

export function initialize() {
  var table = new Tabulator("#table-jobs", {
    columns: [
      {title: "ClusterId"},
      {title: "Queued"},
      {title: "Owner"},
      {title: "Cmd"},
      {title: "JobName"},
      {title: "JobStatus"},
    ]
  });
}

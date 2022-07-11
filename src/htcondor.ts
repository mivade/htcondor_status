import { DateTime } from "luxon";
import { Tabulator, AjaxModule, SortModule } from "tabulator-tables";

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
  for (const module of [AjaxModule, SortModule]) {
    Tabulator.registerModule(module);
  }

  var table = new Tabulator("#table-jobs", {
    columns: [
      {title: "ClusterId", field: "ClusterId"},
      {title: "Queued", field: "QDate"},
      {title: "Owner", field: "Owner"},
      {title: "Cmd", field: "Cmd"},
      {title: "JobName", field: "JobName"},
      {title: "JobStatus", field: "JobStatus"},
    ],
    initialSort: [{column: "Queued", dir: "desc"}],
    ajaxURL: "/summary.json",
    ajaxResponse: function (url, params, response) {
      let data = response.jobs;
      data.forEach((row) => {
        row.QDate = formatQDate(row.QDate);
        row.JobStatus = formatJobStatusString(row.JobStatus);
      });
      console.debug(data);
      return data;
    }
  });

  window.setInterval(() => table.setData("/summary.json"), 10000);
}

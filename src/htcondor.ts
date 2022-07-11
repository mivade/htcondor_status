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

/**
 * Update the dashboard displaying the counts of jobs in different statuses
 * @param jobStatuses
 */
function updateJobCounts(jobStatuses: Array<string>) {
  const counts = {
    "total-job-count": jobStatuses.length,
    "running-job-count": getJobCount(jobStatuses, "Running"),
    "idle-job-count": getJobCount(jobStatuses, "Idle"),
    "held-job-count": getJobCount(jobStatuses, "Held"),
  };

  for (let key in counts) {
    setText(key, counts[key].toString());
  }
}

/**
 * @brief Get the count of jobs with a given status
 * @param jobStatuses
 * @param status Status string to search for
 * @returns
 */
function getJobCount(jobStatuses: Array<string>, status: string): number {
  let count = 0;

  for (let item of jobStatuses) {
    if (item == status) {
      count += 1;
    }
  }
  return count;
}

/**
 * @brief Set the text of an HTML element
 * @param id HTML element ID
 * @param text Text to set
 */
function setText(id: string, text: string) {
  let element = document.getElementById(id);

  if (element != null) {
    element.innerHTML = text;
  }
  else {
    console.error(`Unable to locate element ${id}`);
  }
}

/**
 * @brief Start polling for updates
 */
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
    initialSort: [{column: "QDate", dir: "desc"}],
    layout: "fitDataFill",
    ajaxURL: "/summary.json",
    ajaxResponse: function (url, params, response) {
      let data = response.jobs;
      let jobStatuses: Array<string> = [];
      data.forEach((row) => {
        row.QDate = formatQDate(row.QDate);
        row.JobStatus = formatJobStatusString(row.JobStatus);
        jobStatuses.push(row.JobStatus);
      });
      updateJobCounts(jobStatuses);
      console.debug(data);
      return data;
    }
  });

  // Periodically refresh data
  window.setInterval(() => table.setData("/summary.json"), 10000);
}

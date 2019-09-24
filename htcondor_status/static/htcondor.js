/**
 * @brief Update and display HTCondor jobs in the queue.
 * @param element selector for the element to use for the table
 * @param refreshInterval interval in ms to refresh the table
 */
class HTCondorJobs {
  constructor(element, refreshInterval) {
    this.element = element;
    this.refreshInterval = refreshInterval;
    this.table = $(this.element);
    this.reloadData();
    this.timer = window.setInterval(() => this.reloadData(), refreshInterval);
  }

  /**
   * @brief Reload data and update the table.
   */
  reloadData() {
    console.debug("reloadData");
    fetch("jobs.json")
    .then((response) => { return response.json(); })
    .then((data) => {
      console.debug(data);
      this.table.bootstrapTable("load", data.jobs);
    });
  };
}

window.onload = function () {
  window.jobs = new HTCondorJobs("#htcondor-jobs-table", 5000);
}

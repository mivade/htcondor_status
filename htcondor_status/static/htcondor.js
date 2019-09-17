/**
 * @brief Update and display HTCondor jobs in the queue.
 * @param element selector for the element to use for the table
 * @param refreshInterval interval in ms to refresh the table
 */
class HTCondorJobs {
  constructor(element, refreshInterval) {
    this.element = element;
    this.refreshInterval = refreshInterval;
    this.table = null;
    this.gridOptions = {
      columnDefs: this.columnDefs,
      onGridReady: (params) => {
        params.api.sizeColumnsToFit();
        window.addEventListener(
          "resize", function () {
            this.setTimeout(
              function () {
                params.api.sizeColumnsToFit();
              }
            )
          }
        )
      }
    };
    this.initializeTable();
  }

  /**
   * @brief Column names to display.
   */
  get columnNames() {
    return [
      "ClusterId", "Owner", "Cmd", "JobName", "JobStatus"
    ];
  }

  /**
   * Column definitions.
   */
  get columnDefs() {
    return this.columnNames.map((name) => {
      return {headerName: name, field: name, sortable: true, filter: true};
    });
  }

  /**
   * @brief Initialize the table.
   */
  initializeTable() {
    if (this.table === null) {
      this.table = new agGrid.Grid(document.querySelector(this.element), this.gridOptions);
      this.reloadData();
      window.setInterval(() => this.reloadData(), this.refreshInterval);
    }
  }

  /**
   * @brief Reload data and update the table.
   */
  reloadData() {
    agGrid.simpleHttpRequest({url: "jobs.json"}).then((data) => {
      console.debug(data);
      this.table.gridOptions.api.setRowData(data.jobs);
    });
  };
}

window.onload = function () {
  window.jobs = new HTCondorJobs("#htcondor-jobs-table", 5000);
}

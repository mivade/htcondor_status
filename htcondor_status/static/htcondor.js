window.onload = function () {
  const columnNames = [
    "ClusterId", "Owner", "Cmd", "JobName", "JobStatus"
  ];
  const columnDefs = columnNames.map((name) => {
    return {headerName: name, field: name, sortable: true, filter: true};
  });
  let gridOptions = {
    columnDefs: columnDefs,
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

  new window.agGrid.Grid(document.querySelector("#htcondor-jobs-table"), gridOptions);

  const reloadData = () => {
    window.agGrid.simpleHttpRequest({url: "/jobs.json"}).then((data) => {
      console.log(data);
      gridOptions.api.setRowData(data.jobs);
    });
  };

  reloadData();
  window.setInterval(reloadData, 5000);
};

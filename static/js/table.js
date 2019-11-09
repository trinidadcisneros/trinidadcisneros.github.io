function contructTable(species) {
  d3.csv(`static/documents/python_list_operations.csv`).then(function(data) {

    // Select the table header tag
    var thead = d3.select("thead");
    thead.html("");

    // Append info for each warning to the table body
    const header_keys = Object.keys(data[0]);
    Object.entries(header_keys).forEach(function([key, value]) {
      //Append all values of the event to the row
      var th = thead.append("th").text(value);
    });

    // Select the table body tag
    var tbody = d3.select("tbody");
    tbody.html("");

    data.forEach(event => {
      //Create new row for each warning
      var row = tbody.append("tr");
      Object.entries(event).forEach(function([key, value]) {
        {
          var td = row.append("td").text(value);
        }
      });
    });
  });
}

function init() {
  contructTable();
}

init();

// A construct table function
function contructTable() {
  // use the d3.csv() reads in a csv file and converts it into an array of objects
  d3.csv(`python_list_operations.csv`).then(function(data) {

    // Select the table header tag
    var thead = d3.select("thead");
    thead.html("");

    // Append the data into the head
    const header_keys = Object.keys(data[0]);
    Object.entries(header_keys).forEach(function([key, value]) {
      
      //Append all values of the event to the row
      var th = thead.append("th").text(value);
    });

    // Select the table body tag
    var tbody = d3.select("tbody");
    // This code clears out the tbody in case there is any data already in the table body
    // This is important if you want the table to update when the csv data is updated
    tbody.html("");

    // This code will add the actual data into the body of the table
    data.forEach(event => {
      //Create new row for each warning
      var row = tbody.append("tr");
      
      // Add data into each row
      Object.entries(event).forEach(function([key, value]) {
        {
          var td = row.append("td").text(value);
        }
      });
    });
  });
}

// Invoke the function
contructTable();

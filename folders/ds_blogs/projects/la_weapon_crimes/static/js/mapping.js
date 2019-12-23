// -----------------------------------------------------------
// ------------ GLOBAL VARIABLES -----------------------------
// -----------------------------------------------------------
// NEEDED TO MAKE markersGROUP a GLOBAL VARIABLE TO UPDATE MAP
var markersGroup;

// ------------------------------------------------------------------
// ------------- OPERATING FUNCTIONS -------------------------------
// ------------------------------------------------------------------

// STEP 1 GLOBAL: IMPORT DATA
// ***************************************** //
// *********** GET DATA USING D3 ************ //
// ***************************************** //
function initializeCrimeMap() {
  d3.csv("projects/la_weapon_crimes/static/data/crime_map_data.csv").then(function(data) {
    // Convert to numeric datatypes
    data.forEach(function(d) {
      d.Vict_Age = +d.Vict_Age;
      d.Year = +d.Year;
      d.Lat = +d.Lat;
      d.Lng = +d.Lng;
    });

    // STEP 2: FUNCTIONALITY - ALLOW USERS TO VIEW CRIMES BY WEAPON
    // *********************************************** //
    // **** POPULATE DROP DOWN MENU WITH WEAPONS ***** //
    // ********************************************** //
    // STEP 2A: CREATE AN ARRAY WITH ALL THE WEAPON DATA
    var weapon_array = [];
    for (var i = 0; i < data.length; i++) {
      weapon_array.push(data[i].Weapon_Desc);
    }
    // STEP 2B: USE THE SET METHOD TO CREATE A NEW ARRAY WITH ONLY UNIQUE VALUES
    var uniqueWeaponList = Array.from(new Set(weapon_array));

    // STEP 2C: INVOKE CREATE DROPDOWN FUNCTION TO POPULATE
    // DROP DOWN ELEMENT WITH UNIQUE ARRAY
    createDropDown("#selection", uniqueWeaponList);

    // STEP 3: FILTER DATA SO MARKERS CAN BE DISPLAYED
    // TOO MANY EVENTS TO BE DISPLAYED AT ONCE
    // ********************************************* //
    // ***** FILTER DATA FOR DISPLAY *************** //
    // ********************************************* //
    // STEP 3A: FILTER DATA BY YEAR
    var filtered_2019 = data.filter(function(d) {
      return d.Year === 2019;
    });

    // STEP 3B: FILTER DATA BY WEAPON
    // STEP 3B1: GET THE FIRST VALUE FROM THE DROPDOWN
    var sel = document.getElementById("selection");
    var weaponInitializer = sel.options[sel.selectedIndex].value;

    // STEP 3B2: PASS THIS TO THE FILTER
    var filtered_2019_weapon = filtered_2019.filter(function(d) {
      return d.Weapon_Desc === weaponInitializer;
    });

    // STEP 4: INITIALIZE THE MAP
    // ***************************************** //
    // **************** CREATE MAP ************* //
    // ***************************************** //
    // STEP 4A: CREATE THE MAP OBJECT CENTERED IN LA
    var map = L.map("map", {
      center: [34.0522, -118.2437],
      zoom: 10
    });

    // STEP 4B: SET-UP BASEMAP THAT WILL BE USED
    // WITH THE LAYER CONTROL SWITCH
    // ADD TO MAP
    var osmBasemap = L.tileLayer(
      "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution:
          '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        maxZoom: 18
      }
    ).addTo(map);

    var basemaps = {
      OSM: osmBasemap
    };

    // STEP 4C: SET-UP OVERLAYS
    var overlays = {
      // "2018": filtered_2018
    };

    // STEP 4D: ADD CONTROL LAYER
    // L.control
    //   .layers(basemaps, overlays, {
    //     collapsed: false
    //   }).addTo(map);

    // STEP 5: ADD CRIME MARKERS
    // ***************************************** //
    // *************** ADD MARKERS ************* //
    // ***************************************** //
    // STEP 5A - PASS FILTERED DATA TO  getMarkerData() function
    // STEP 5B - getMarkerData() WILL PASS DATA TO getRandom()
    // STEP 5C - getRandom() WILL PREPARED A RANDOM SUBSET
    // STEP 5D - RANDOM SUBSET IS RETURNED
    getMarkerData(filtered_2019_weapon);

    markersGroup = L.layerGroup().addTo(map);
    // STEP 5E - RANDOM SUBSET IS PLOTTED ON MAP USING A FOR LOOP
    for (var i = 0; i < random_subset.length; i++) {
      var lat = +random_subset[i].Lat;
      var lng = +random_subset[i].Lng;

      var popupContent = '<b>Weapon</b>: ' + random_subset[i].Weapon_Desc;
      popupContent += '<br>';
      popupContent += '<b>Crime Reported</b>: ' + random_subset[i].Crime_Code;
      popupContent += '<br>';
      popupContent += '<b>Date Reported</b>: ' + random_subset[i].Date_Reported;
      popupContent += '<br>';
      popupContent += '<b>Area Name</b>: ' + random_subset[i].Area_Name;
      popupContent += '<br>';
      popupContent += '<b>Victim Age</b>: ' + random_subset[i].Vict_Age;
      popupContent += '<br>';
      popupContent += '<b>Victim Sex</b>: ' + random_subset[i].Vict_Sex;
      popupContent += '<br>';
      popupContent += '<b>Victim Ethnicity</b>: ' + random_subset[i].Vict_Desc;
      popupContent += '<br>';
      popupContent += '<b>Status of Case</b>: ' + random_subset[i].Status_Desc;

      // var popupText = 'test ' + random_subset[i].Weapon_Desc;

      // STEP 5F - EXTRACTED DATA ASSIGNED TO VARIABLES
      var markerLocation = new L.LatLng(lat, lng);
      var marker = new L.Marker(markerLocation);

      // STEP 5G - VARIABLES ADDED TO MAP
      // marker.bindPopup(popupText);
      marker.bindPopup(popupContent);
      markersGroup.addLayer(marker);
      // map.addLayer(marker);
    }
  });
}

// STEP 2 GLOBAL: UPDATE MAP ON USER SELECTION
function updateCrimeMAP(newSelection) {
  d3.csv("projects/la_weapon_crimes/static/data/crime_map_data.csv").then(function(data) {
    // Convert to numeric datatypes
    data.forEach(function(d) {
      d.Vict_Age = +d.Vict_Age;
      d.Year = +d.Year;
      d.Lat = +d.Lat;
      d.Lng = +d.Lng;
    });

    // STEP 1A: FILTER DATA BY YEAR
    var filtered_2019 = data.filter(function(d) {
      return d.Year === 2019;
    });

    // STEP 1B: FILTER DATA BASED ON WEAPON SELECTION
    var filtered_2019_weapon = filtered_2019.filter(function(d) {
      return d.Weapon_Desc === newSelection;
    });

    // STEP 2: CLEAR previous maker layers
    markersGroup.clearLayers();

    // STEP 3: ADD NEW CRIME MARKERS
    // STEP 3A - PASS FILTERED DATA TO  getMarkerData() function
    // STEP 3B - getMarkerData() WILL PASS DATA TO getRandom()
    // STEP 3C - getRandom() WILL PREPARED A RANDOM SUBSET
    // STEP 3D - RANDOM SUBSET IS RETURNED
    getMarkerData(filtered_2019_weapon);

    // STEP 3E - RANDOM SUBSET IS PLOTTED ON MAP USING A FOR LOOP
    for (var i = 0; i < random_subset.length; i++) {
      var lat = +random_subset[i].Lat;
      var lng = +random_subset[i].Lng;

      var popupContent = '<b>Weapon</b>: ' + random_subset[i].Weapon_Desc;
      popupContent += '<br>';
      popupContent += '<b>Crime Reported</b>: ' + random_subset[i].Crime_Code;
      popupContent += '<br>';
      popupContent += '<b>Date Reported</b>: ' + random_subset[i].Date_Reported;
      popupContent += '<br>';
      popupContent += '<b>Area Name</b>: ' + random_subset[i].Area_Name;
      popupContent += '<br>';
      popupContent += '<b>Victim Age</b>: ' + random_subset[i].Vict_Age;
      popupContent += '<br>';
      popupContent += '<b>Victim Sex</b>: ' + random_subset[i].Vict_Sex;
      popupContent += '<br>';
      popupContent += '<b>Victim Ethnicity</b>: ' + random_subset[i].Vict_Desc;
      popupContent += '<br>';
      popupContent += '<b>Status of Case</b>: ' + random_subset[i].Status_Desc;

      // STEP 3D1 - EXTRACTED DATA ASSIGNED TO VARIABLES
      var markerLocation = new L.LatLng(lat, lng);
      var marker = new L.Marker(markerLocation);

      // STEP 3D2 - VARIABLES ADDED TO MAP
      marker.bindPopup(popupContent);
      markersGroup.addLayer(marker);
      // map.addLayer(marker);
    }
  });
}

// ------------------------------------------------------------------
// ------------- SUPPORTING FUNCTIONS -------------------------------
// ------------------------------------------------------------------

// ***************************************************** //
// *** FUNCTION THAT WILL CREATE A DYNAMIC DROPDOWN  *** //
// ***************************************************** //
function createDropDown(id, array) {
  var selector = d3.select(id);
  array.forEach(weapon => {
    selector
      .append("option")
      .text(weapon)
      .property("value", weapon);
  });
}

// ****************************************** //
// ***** FUNCTION TO GET RANDOM ARRAY  ****** //
// ****************************************** //
function getRandom(arr, n) {
  if (arr.length < 20) n = arr.length;
  var result = new Array(n),
    len = arr.length,
    taken = new Array(len);
  if (n > len)
    throw new RangeError("getRandom: more elements taken than available");
  while (n--) {
    var x = Math.floor(Math.random() * len);
    result[n] = arr[x in taken ? taken[x] : x];
    taken[x] = --len in taken ? taken[len] : len;
  }
  return result;
}

// *********************************************** //
// *** GET RANDOM SUBSET FOR PLOTTING MARKERS  *** //
// *********************************************** //

function getMarkerData(filtered_data) {
  // STEP 1: CALL ON THE getRandom() FUNCTION
  // TO GET A RANDOM SUBSET, AND THE SECOND PARAMETER
  // IS THE NUMBER OF RECORDS TO RETURN
  random_subset = getRandom(filtered_data, 40);
  return random_subset;
}

// ------------------------------------------------------------------
// ------------- INSTANTIATING SECTION -------------------------------
// ------------------------------------------------------------------

// INITIALIZE THE MAP
function init() {
  initializeCrimeMap();
}

// THEN UPDATE THE MAP WHEN A NEW WEAPON FROM DROP DOWN SELECTED
function updateWeapon(newSelection) {
  console.log(newSelection);
  updateCrimeMAP(newSelection);
}

init();

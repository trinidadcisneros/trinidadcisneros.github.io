console.log("js working");
console.log("Hello world!");


function load_navbase() {
    document.getElementById("navbar-frame").innerHTML='<object type="text/html" data="navbar.html" ></object>';
    console.log("in function");
}

load_navbase();
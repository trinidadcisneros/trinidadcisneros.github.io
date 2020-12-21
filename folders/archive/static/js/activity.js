console.log("hello");

function clearHTML() {
    document.getElementById("prompt").innerHTML = '';
};

function respondActivity() {
    d3.csv('static/data/activity.csv').then(function(data) {
        var question = data[Math.floor(Math.random() * data.length)];
        document.getElementById("prompt").innerHTML = question.prompt;
    })
};

function init() {
    respondActivity();
};

init();
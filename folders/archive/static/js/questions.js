console.log("hello");

function clearHTML() {
    document.getElementById("prompt").innerHTML = '';
};

function postPrompt() {
    d3.csv('static/data/questions.csv').then(function(data) {
        var question = data[Math.floor(Math.random() * data.length)];
        document.getElementById("prompt").innerHTML = question.prompt;
    })
};

function init() {
    postPrompt();
};

init();
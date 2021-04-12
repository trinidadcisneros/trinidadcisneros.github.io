// Import latest MathJax library
var script = document.createElement('script');

    script.src = 
"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js";

    document.head.appendChild(script);

// Imports the polyfill library that helps mathjax render on various broswers, including older ones
var script2 = document.createElement('script');

    script2.src = 
"https://polyfill.io/v3/polyfill.min.js?features=es6";

    document.head.appendChild(script2);

MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']]
    },
    "HTML-CSS" : { linebreaks : { automatic : true } },
    CommonHTML : { linebreaks : { automatic : true } },
    svg: {
        fontCache: 'global',
        linebreaks: {automatic: true}
    }
};

// Function to update typeset for mathjax code in jupyter notebook div
// Waits 10th for notebook to be loaded, then typesets.
function UpdateNotebook() {
    setTimeout(function () {
      const node = document.getElementById('#jnotebook');
      MathJax.typesetPromise();
    }, 500);
    console.log('Update Notebook Completed');
  };

UpdateNotebook();

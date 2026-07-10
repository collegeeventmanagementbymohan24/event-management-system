// Fade Alerts Automatically

setTimeout(function(){

let alerts=document.querySelectorAll(".alert");

alerts.forEach(function(alert){

alert.style.transition="0.6s";

alert.style.opacity="0";

setTimeout(()=>{

alert.remove();

},600);

});

},3000);


// Button Hover Animation

let buttons=document.querySelectorAll(".btn");

buttons.forEach(function(btn){

btn.addEventListener("mouseenter",function(){

btn.style.transform="scale(1.05)";

btn.style.transition=".3s";

});

btn.addEventListener("mouseleave",function(){

btn.style.transform="scale(1)";

});

});
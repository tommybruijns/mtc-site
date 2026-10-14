(function(){var h=document.documentElement,b=document.getElementById("lang");h.classList.add("js");
function set(l){h.setAttribute("data-lang",l);h.lang=l;b.textContent=l==="nl"?"EN":"NL";try{localStorage.setItem("l",l)}catch(e){}document.dispatchEvent(new CustomEvent("mtc-lang",{detail:l}))}
try{var s=localStorage.getItem("l");if(s)set(s)}catch(e){}
b.addEventListener("click",function(){set(h.getAttribute("data-lang")==="nl"?"en":"nl")});
var r=document.querySelectorAll(".reveal");
if(!("IntersectionObserver" in window)||matchMedia("(prefers-reduced-motion: reduce)").matches){r.forEach(function(e){e.classList.add("in")});return}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}})},{threshold:.12});
r.forEach(function(e){io.observe(e)});})();

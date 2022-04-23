function myfunction()
{

    let message = document.getElementById("myapology").innerHTML;
    console.log(message);
    var ajax = new XMLHttpRequest();

    ajax.onreadystatechange = function()
    {
       if(ajax.readyState == 4 && ajax.status == 200)
       {
          document.getElementById("demo").innerHTML = ajax.responseText;
       }
    };

    ajax.open("GET", "static/" + message + ".html", true);
    ajax.send();


}



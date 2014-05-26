// Add an onclick function onto the add new target button to show the relevant fields
window.onload = function()
{
    var b = document.getElementById("button");
    b.onclick = function()
    {

        //Name Field
        var name = document.createElement("span");
        var nametext = document.createTextNode('Name: ');
        var nameinput = document.createElement("input");
        nameinput.setAttribute("name", "name");
        nameinput.setAttribute("type", "text");
        var br1 = document.createElement("br");

        //URI Field
        var url = document.createElement("span");
        var urltext = document.createTextNode('URL: ');
        var uriinput = document.createElement("input");
        uriinput.setAttribute("name", "uri");
        uriinput.setAttribute("type", "text");
        var br2 = document.createElement("br");
        var br3 = document.createElement("br");

        //Add Button
        var add = document.createElement("input");
        add.setAttribute("type", "submit");
        add.setAttribute("value", "Add");

        document.addnew.button.setAttribute("type", "hidden");

        document.getElementById("addnew").appendChild(name).appendChild(nametext);
        document.getElementById("addnew").appendChild(nameinput);
        document.getElementById("addnew").appendChild(br1);
        document.getElementById("addnew").appendChild(url).appendChild(urltext);
        document.getElementById("addnew").appendChild(uriinput);
        document.getElementById("addnew").appendChild(br2);
        document.getElementById("addnew").appendChild(br3);
        document.getElementById("addnew").appendChild(add);
    }
}
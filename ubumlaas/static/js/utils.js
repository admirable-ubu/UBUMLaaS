function titleCase(str) {
   
    var splitStr = str.split("_").join(" ").toLowerCase().split(' ');
    for (var i = 0; i < splitStr.length; i++) {
        // You do not need to check if i is larger than splitStr length, as your for does that for you
        // Assign it back to the array
        splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);     
    }
    // Directly return the joined string
    return splitStr.join(' '); 
}

function firstClick(){
    setTimeout(function(){
        $(".selectpicker").each(function(){
            console.log($(this).parent());
            $(this).next().click();
            $("body").click();
        });
    }, 100);

}
 
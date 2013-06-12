/*
 * jQuery javascript code snippet to check form is saved before navigation away from it 
 *
 * from http://www.nateyolles.com/tag/window-onbeforeunload/
 *
 * Accessed February 2011
 * 
 */

var myProject = myProject || {};
 
myProject.isConfirmNav = true; //used for the bypass feature
myProject.elementsAtLoad = new Object;
 
//Collect form data and return an array
myProject.gatherFormElements = function(){
    var elements = new Array();
 
    // get all input elements and exclude all hidden and .NET generated fields
    var $formElements = $('input, textarea, select').not('[id^=__], :hidden');
 
    $formElements.each(function(index){
        var $obj = $(this);
 
        if ($obj.is(':text') || $obj.is('textarea') || $obj.is('select') || $obj.is(':file'))
        {
            if ($obj.val() == null || $obj.val() == "")
                elements[index] = "null";
            else
                elements[index] = $obj.val().toString();
        }
        else if ($obj.is(':checkbox') || $obj.is(':radio'))
        {
            if ($obj.attr('checked'))
                elements[index] = true;
            else
                elements[index] = false;
        }
        else
        {
            elements[index] = "null";
        }
 
    });
 
    return elements;
};
 
// Compare two arrays of form data
myProject.isFormChanged = function(startValues, endValues){
    var isChanged = false;
 
    jQuery.each(startValues, function(index, value){
        if (startValues[index] != endValues[index]){
            isChanged = true;
            return false; //brakes each loop
        }
    });
 
    return isChanged;
};
 
// Function assigned to window.onbeforeunload
// 1: Check to see if feature is bypassed
// 2: Collect form data at point of user action/navigation
// 3: Compare form data to original form data and utilize "special" return of text to window.onbeforeunload
myProject.confirmNavigation = function(){
    if (!myProject.isConfirmNav)
        return;
 
    var elementsAtSubmit = myProject.gatherFormElements();
 
    if (myProject.isFormChanged(myProject.elementsAtLoad, elementsAtSubmit)){
        return "Save any changes that you made before leaving this screen. If you do not save the changes, they will be lost."
    }
 
}
 
// used for bypass feature
myProject.bypassConfirm = function(){
    myProject.isConfirmNav = false;
}
 
//on document.ready set window.onbeforeunload and collect first set of unaltered form data
$(function(){
    window.onbeforeunload = myProject.confirmNavigation;
    myProject.elementsAtLoad = myProject.gatherFormElements();
});
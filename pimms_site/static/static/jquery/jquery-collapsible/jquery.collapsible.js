/*
 * jQuery collapsable panel plugin
 *
 * from http://www.webdesignerwall.com/tutorials/jquery-tutorials-for-designers/
 *
 * Accessed February 2011
 * 
 */
$(document).ready(function()
      {
        //hide the all of the element with class msg_body
        $(".msg_body").hide();
        //toggle the component with class msg_body
        $(".msg_head").click(function()
        {
          $(this).next(".msg_body").slideToggle(600);
        });
      });
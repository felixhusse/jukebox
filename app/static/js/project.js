/* Project specific Javascript goes here. */
function update_messages(messages){
    const levels = {20: 'info', 25: 'success', 30: 'warning', 40: 'error'}
      $("#jukebox_message").html("");
        var level = 20;
      $.each(messages, function (i, m) {
          level = m.level;
          $("#jukebox_message").append("<div class='alert alert-dismissible alert-"+levels[m.level]+"' id='notification'>"
            +m.message+
            "<button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button></div>");
      });
      if (level > 30) {

      }
      else {
          $("#notification").hide();
          $("#notification").fadeTo(2000, 500).slideUp(500, function() {
            $("#notification").slideUp(500);
          });
      }

  }

  function show_spinner(spinner_text){
    const levels = {20: 'info', 25: 'success', 30: 'warning', 40: 'error'}
      $("#jukebox_message").html("");
     $("#jukebox_message").append("<div class='alert alert-dismissible alert-"+levels[20]+"' id='notification'><div className='spinner-border' role='status'><span class=\"visually-hidden\">Loading...</span></div>"

        +spinner_text+
        "<button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button></div>");
  }

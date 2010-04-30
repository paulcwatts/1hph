// Javascript Hunt objects
(function($) {
  $.fn.huntList = function(settings) {
      var config = {
          'url': "",
          'defaultImage': null
      };
      if (settings) {
        $.extend(config, settings)
      }

      var html = '<li><img class="thumb-icon"/><div class="clearfix"><h2 class="phrase"></h2><h3></h3></div>'
      this.each(function() {
          var list = this;
          $.getJSON(config.url, function(data) {
              $.each(data.hunts, function(i,hunt) {
                  var li = $(html);
                  if (hunt.thumbnail) {
                    $("img",li).attr("src", hunt.thumbnail);
                  }
                  else {
                    $("img",li).attr("src", ""); //config.defaultImage);
                  }
                  $("h2",li).text(hunt.phrase);
                  var start_time = new Date(hunt.start_time);
                  var end_time = new Date(hunt.end_time);
                  var vote_end_time = new Date(hunt.vote_end_time);
                  var now = new Date();
                  var timeText = "";
                  // Future hunt?
                  if (start_time > now) {
                    timeText = "Hunt begins on " + start_time.toLocaleString();
                    // TODO: Countdown
                  }
                  else if (end_time > now) {
                    timeText = "Hunt ends on " + end_time.toLocaleString();
                    // TODO: Countdown
                  }
                  else if (vote_end_time > now) {
                    timeText = "Voting ends on " + vote_end_time.toLocaleString();
                  }
                  else {
                    timeText = "Hunt ended on: " + vote_end_time.toLocaleString();
                  }
                  $("h3", li).text(timeText);

                  li.click(function() {
                      window.location = hunt.url;
                  }).appendTo(list);
              });
          });
      });

      return this;
  };
})(jQuery);

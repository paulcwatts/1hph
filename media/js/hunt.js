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

      var html = '<li class="two-line-item clickable"><img class="thumb-icon thumb-icon-left"/><div class="clearfix"><h2 class="line1 phrase"></h2><h3 class="line2"></h3></div></li>'
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

  $.fn.commentList = function(settings) {
      var config = {
        'url': '',
        'form': ''
      };
      if (settings) {
         $.extend(config, settings)
      }
      var html = '<li class="comment-item"><img class="comment-thumb-icon thumb-icon-left"/><div class="clearfix"><a class="comment-from"></a> <span class="comment"></span><br/><span class="comment-line2 comment-time"></span></li>'
      this.each(function() {
          var list = this;
          // Add an onsubmit handler to the form to do an ajaxSubmit rather than a regular submit

          $.getJSON(config.url, function(data) {
              var now = new Date();
              $.each(data.comments, function(i,comment) {
                  var li = $(html);
                  var source = comment.source;
                  if (source.photo) {
                      $("img",li).attr("src", hunt.thumbnail);
                  }
                  else {
                      $("img",li).attr("src", ""); //config.defaultImage);
                  }
                  var url = source.url;
                  if (!url) {
                    url = "#";
                  }
                  $(".comment-from", li).attr("href", url).text(source.name);
                  $(".comment", li).text(comment.text);

                  var time = new Date(comment.time);
                  $(".comment-time", li).text(Utils.getRelativeTimeSpanString(time, now));
                  li.appendTo(list);
              });
          });
      });

  };
})(jQuery);

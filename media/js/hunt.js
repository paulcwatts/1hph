// Javascript Hunt objects
(function($) {
  $.fn.setImage	= function(src,def,width,height) {
    var img;
    if (src) {
      img = src;
    }
    else if (def) {
      img = def;
    }
    else {
      // Nothing to do...
      return this;
    }
    this.each(function() {
      var dest = $(this);
      // TODO: When given width and height, use the width and height
      // of the destination element as a guide to resizing the image
      // so as to preserve its aspect ratio.
      dest.attr("src", img);
    });
    return this;
  };

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
                  $("img",li).setImage(hunt.thumbnail, config.defaultImage);
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

  $.fn.setSource = function(source) {
      var url = source.url;
      if (!url) {
        url = "#";
      }
      this.attr("href", url).text(source.name);
      return this;
  }

  $.fn.commentList = function(settings) {
      var config = {
        'url': '',
        'form': '',
        'defaultImage': null
      };
      if (settings) {
         $.extend(config, settings)
      }
      var html = '<li class="comment-item"><img class="comment-thumb-icon thumb-icon-left"/><div class="clearfix"><a class="from"></a> <span class="comment"></span><br/><span class="comment-line2 time comment-time"></span></li>'
      this.each(function() {
          var list = this;
          function add(comment, slide, now) {
              var li = $(html);
              var source = comment.source;
              // No profile image yet???
              $("img",li).setImage(config.defaultImage);
              $(".from", li).setSource(source);
              $(".comment", li).text(comment.text);

              var time = new Date(comment.time);
              $(".time", li).text(Utils.getRelativeTimeSpanString(time, now));
              if (slide) {
                li.hide().prependTo(list).slideDown();
              }
              else {
                li.appendTo(list);
              }
          }

          // Add an onsubmit handler to the form to do an ajaxSubmit rather than a regular submit
          var form = $(config.form);
          form.submit(function() {
            var indicator = $(" .indicator", form);
            indicator.show();
            form.ajaxSubmit({ dataType: 'json',
              success: function(data, status, xhr) {
                add(data, true, new Date());
              },
              error: function(xhr, status, error) {
              },
              complete: function(xhr, status) {
                indicator.hide();
                form.clearForm();
            }});

            return false;
          });

          $.getJSON(config.url, function(data) {
              var now = new Date();
              $.each(data.comments, function(i,comment) {
                add(comment, false, now);
              });
          });
      });
      return this;
  };

  $.fn.submissionList = function(settings) {
      var config = {
        'url': '',
        'add': null
      };
      if (settings) {
         $.extend(config, settings)
      }
      var html = '<li class="submission-item"><a class="img-link" href=""><img class="submission-thumb-icon" src="" alt="submitted photo"/></a><br/>Posted by <a class="from"></a><br/><span class="time"></span></li>';
      this.each(function() {
          var list = this;
          function add(photo, slide, now) {
              var li = $(html);
              var source = photo.source;
              $("img",li).setImage(photo.thumbnail_url);
              $(".img-link", li).attr("href", photo.url);
              $(".from", li).setSource(source);

              var time = new Date(photo.time);
              $(".time", li).text(Utils.getRelativeTimeSpanString(time, now));
              if (slide) {
                li.hide().prependTo(list).slideDown();
              }
              else {
                li.appendTo(list);
              }
          }
          if (config.add) {
            add(config.add, true, new Date());
            return this;
          }

          $.getJSON(config.url, function(data) {
              var now = new Date();
              $.each(data.submissions, function(i,submissions) {
                add(submissions, false, now);
              });
          });
      });
      return this;
  };
})(jQuery);

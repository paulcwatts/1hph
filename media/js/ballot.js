(function($) {
  $.fn.ballotError = function(xhr) {
    if (xhr.responseText) {
      var json = $.parseJSON(xhr.responseText);
      if (json) {
        this.text(json.error);
      }
    }
    return this;
  }
  $.fn.ballot = function(settings) {
      var config = {
          'url': "",
      };
      if (settings) {
        $.extend(config, settings)
      }
      this.each(function() {
        var ballot = $(this);
        var imgcontainer = $(".ballot-img-container", ballot);
        var loading = $(".loading", ballot);
        var error = $(".load-error", ballot);
        var overlays = $(".ballot-overlay", ballot);
        var ballotleft = $(".ballot-left", imgcontainer);
        var ballotright = $(".ballot-right", imgcontainer);

        var leftimg = null;
        var rightimg = null;
        var numLoaded = 0;
        function onImgLoad() {
            ++numLoaded;
            if (numLoaded == 2) {
              // Now we can show the container and hide loading
              loading.hide();
              ballotleft.prepend(leftimg);
              ballotright.prepend(rightimg);

              imgcontainer.fadeIn('fast');
            }
        }
        function onImgLeftClick() {
          doVote(leftimg, rightimg);
        }
        function onImgRightClick() {
          doVote(rightimg, leftimg);
        }
        function showBallot(data) {
            var submissions = data.submissions;
            var left = submissions[0];
            var right = submissions[1];
            numLoaded = 0;
            leftimg = $('<img/>')
              .data("json", left)
              .addClass("submission")
              .load(onImgLoad)
              .click(onImgLeftClick)
              .attr('src', left.thumbnail_url);
            rightimg = $('<img/>')
              .data("json", right)
              .addClass("submission")
              .load(onImgLoad)
              .click(onImgRightClick)
              .attr('src', right.thumbnail_url);

        }
        function doVote(winner, loser) {
            var json = winner.data("json");
            winner.parent().addClass("winner");
            loser.parent().addClass("loser");
            // Wait for a second and then go back to the beginning
            window.setTimeout(function() {
              imgcontainer.fadeOut('fast', function() {
                  // Remove the old images
                var imgs = $(".submission", imgcontainer);
                imgs.parents()
                  .removeClass("winner")
                  .removeClass("loser");
                imgs.remove();
                $.ajax({
                    type: 'POST',
                    url: config.url,
                    data: { url: json.url },
                    dataType: 'json',
                    success: function(data, textStatus, xhr) {
                      showBallot(data);
                    },
                    error: function(xhr, textStatus) {
                      loading.hide();
                      error.ballotError(xhr).show();
                    }
                  });
                });
              loading.show();
           }, 500);
        }

        // show loading
        imgcontainer.hide();
        error.hide();
        loading.show();

        // getJSON of ballot
        $.ajax({
            url: config.url,
            dataType: 'json',
            success: function(data, textStatus, xhr) {
              showBallot(data);
            },
            error: function(xhr, textStatus) {
              loading.hide();
              error.ballotError(xhr).show();
            }
        });
      });
      return this;
  };
})(jQuery);

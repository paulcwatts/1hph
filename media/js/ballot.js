(function($) {
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
        var leftimg = $(".ballot-left img", ballot);
        var rightimg = $(".ballot-right img", ballot);
        var overlays = $(".ballot-overlay", ballot);

        var numLoaded = 0;
        function onImgLoad() {
            ++numLoaded;
            if (numLoaded == 2) {
              // Now we can show the container and hide loading
              loading.hide();
              // Ensure the winner and loser classes aren't there
              leftimg.parent().removeClass("winner").removeClass("loser");
              rightimg.parent().removeClass("winner").removeClass("loser");
              imgcontainer.slideDown();
            }
        }
        function showBallot(data) {
            var submissions = data.submissions;
            var left = submissions[0];
            var right = submissions[1];
            numLoaded = 0;
            leftimg.data("json", left);
            rightimg.data("json", right);
            leftimg.attr("src", left.thumbnail_url);
            rightimg.attr("src", right.thumbnail_url);
        }
        function doVote(winner, loser) {
            var img = $(this);
            var json = winner.data("json");
            winner.parent().addClass("winner");
            loser.parent().addClass("loser");
            // Wait for a second and then go back to the beginning
            window.setTimeout(function() {
              imgcontainer.slideUp();
              loading.show();
              $.ajax({
                type: 'POST',
                url: config.url,
                data: { url: json.url },
                dataType: 'json',
                success: function(data, textStatus, xhr) {
                  showBallot(data);
                },
                error: function(xhr, textStatus) {
                  alert("ERROR");
                }
              });
            }, 1000);
        }
        function onImgLeftClick() {
          doVote(leftimg, rightimg);
        }
        function onImgRightClick() {
          doVote(rightimg, leftimg);
        }

        // set up onclicks and loads for the images
        leftimg.click(onImgLeftClick).load(onImgLoad);
        rightimg.click(onImgRightClick).load(onImgLoad);

        // show loading
        imgcontainer.hide();
        loading.show();

        // getJSON of ballot
        $.getJSON(config.url, function(data) {
          showBallot(data);
        });
      });
      return this;
  };
})(jQuery);

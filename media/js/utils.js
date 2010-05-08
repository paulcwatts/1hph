Utils = new Object();

var REGEXP_ISODATE = new RegExp(/(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))/);

// http://blog.dansnetwork.com/2008/11/01/javascript-iso8601rfc3339-date-parser/
Utils.iso_date = function(dString) {
  var result = new Date();
  if (dString.toString().match(REGEXP_ISODATE)) {
    var d = dString.match(REGEXP_ISODATE);
    var offset = 0;
    result.setUTCDate(1);
    result.setUTCFullYear(parseInt(d[1],10));
    result.setUTCMonth(parseInt(d[3],10) - 1);
    result.setUTCDate(parseInt(d[5],10));
    result.setUTCHours(parseInt(d[7],10));
    result.setUTCMinutes(parseInt(d[9],10));
    result.setUTCSeconds(parseInt(d[11],10));
    if (d[12]) {
      result.setUTCMilliseconds(parseFloat(d[12]) * 1000);
    }
    else {
      result.setUTCMilliseconds(0);
    }
    if (d[13] != 'Z') {
       offset = (d[15] * 60) + parseInt(d[17],10);
       offset *= ((d[14] == '-') ? -1 : 1);
       result.setTime(result.getTime() - offset * 60 * 1000);
    }
  }
  else {
    result.setTime(Date.parse(dString));
  }
  return result;
};


// Adapted from django's time_since
//
// Takes two datetime objects and returns the time between d and now
// as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
// then "0 minutes" is returned.

// Units used are years, months, weeks, days, hours, and minutes.
// Seconds and microseconds are ignored.  Up to two adjacent units will be
// displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
// possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.
Utils.pluralize = function(n, singular, plural) {
  return (n == 0 || n > 1) ? plural : singular;
}

Utils.time_since = function(d, now) {
  var chunks = [
    { seconds: 60 * 60 * 24 * 365, text: function(n) { return Utils.pluralize(n, 'year', 'years') } },
    { seconds: 60 * 60 * 24 * 30,  text: function(n) { return Utils.pluralize(n, 'month', 'months') } },
    { seconds: 60 * 60 * 24 * 7,   text: function(n) { return Utils.pluralize(n, 'week', 'weeks') } },
    { seconds: 60 * 60 * 24,       text: function(n) { return Utils.pluralize(n, 'day', 'days') } },
    { seconds: 60 * 60, 		   text: function(n) { return Utils.pluralize(n, 'hour', 'hours') } },
    { seconds: 60, 				   text: function(n) { return Utils.pluralize(n, 'minute', 'minutes') } }
  ];
  if (!now) {
     now = new Date();
  }
  // we only care about second precision
  var dseconds = d.getTime()/1000;
  var nowseconds = now.getTime()/1000;
  var since = nowseconds - dseconds;
  if (since <= 0) {
    // d is in the future compared to now, stop processing
    return '0 minutes';
  }
  var i=0;
  var count=0;
  for (; i < chunks.length; ++i) {
     var chunk = chunks[i];
     count = Math.floor(since / chunk.seconds);
     if (count != 0) {
       break;
     }
  }
  var s = count + " " + chunks[i].text(count);
  if (i + 1 < chunks.length) {
    // now get the second item
    var chunk2 = chunks[i+1];
    var count2 = Math.floor((since - (chunks[i].seconds * count)) / chunk2.seconds)
    if (count2 != 0) {
      s += ", " + count2 + " " + chunk2.text(count2);
    }
  }
  return s;
}

Utils.time_until = function(d, now) {
  if (!now) {
    now = new Date();
  }
  return Utils.time_since(now, d)
}

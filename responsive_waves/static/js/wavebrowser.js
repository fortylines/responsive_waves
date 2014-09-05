/* Copyright (c) 2012-2014, Fortylines LLC
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
   TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. */

/* This file contains the waveform and ruler widgets used by the Value Change
   Browser application.
 */

/** Helper function to show messages
 */
function showMessages(messages, style) {
    $("#messages").removeClass('hidden');
    var messageBlock = $('<div class="alert alert-block"><button type="button" class="close" data-dismiss="alert">&times;</button></div>');
    $("#messages .row").append(messageBlock);
    if( style ) {
        messageBlock.addClass("alert-" + style);
    }
    for( var i = 0; i < messages.length; ++i ) {
        messageBlock.append('<p>' + messages[i] + '</p>');
    }
    $("html, body").animate({ scrollTop: $("#messages").offset().top - 50 },
        500);
}


/** Helper function to create a call to the http api.
*/
function api_location(category, command) {
    apiLoc = document.location.origin
        + '/api/' + category + '/' + $('.browser-panel').attr('id') + '/';
    if( command ) {
        apiLoc += command
    }
    return apiLoc;
}


var responsive_waves_api = {
    'scope': 'scope-not-used',
    'list_variables': api_location('variables', ''),
    'time_records': api_location('values', ''),
    'update_ranks': api_location('browser','ranks'),
    'update_variable': api_location('browser', 'variables'),
}


/** Helper function to return a font height, ascent, and descent in pixels
*/
function getTextHeight(font, fontsize, fontweight, fontstyle, fontvariant,
					   thetext) {
	var result={};
	var blockdiv = document.createElement("div");
	blockdiv.style.display="inline-block";
	blockdiv.style.width="1px";
	blockdiv.style.height="0px";
	var body=document.getElementsByTagName("body")[0];
	var aspan=document.createElement("span");
	if(typeof font === 'undefined'){
	  return result;
	}
	aspan.style.fontFamily=font;
	if(typeof fontsize !== 'undefined'){
	    aspan.style.fontSize=fontsize;
	}
	if(typeof fontweight !== 'undefined'){
	    aspan.style.fontWeight=fontweight;
	}
	if(typeof fontstyle !== 'undefined'){
	    aspan.style.fontStyle=fontstyle;
	}
	if(typeof fontvariant !== 'undefined'){
	    aspan.style.fontVariant=fontvariant;
	}
	if(typeof thetext !== 'undefined'){
	    aspan.innerHTML=thetext;
	}else{
	    aspan.innerHTML="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
	}

	var adiv=document.createElement("div");
	adiv.appendChild(aspan);
	adiv.appendChild(blockdiv);

	var body=document.getElementsByTagName('body')[0]
	try {
	    body.appendChild(adiv);
	    blockdiv.style.verticalAlign="baseline";
	    result.ascent=blockdiv.offsetTop - aspan.offsetTop;
	    blockdiv.style.verticalAlign="bottom";
	    result.height=blockdiv.offsetTop - aspan.offsetTop;
	    result.descent=result.height-result.ascent;
	} finally {
	  body.removeChild(adiv);
	}
	return result;
};

(function( $, undefined ) {
$.widget( "fortylines.colorPicker", {
    options: {
        container: null,
        themes: {
            'red-on-black': { "color": "#f00", "background-color": "#000" },
            'green-on-black': { "color": "#0f0", "background-color": "#000" },
            'blue-on-black': { "color": "#00f", "background-color": "#000" },
            'purple-on-black': { "color":"#800080","background-color": "#000" },
            'white-on-black': { "color": "#fff", "background-color": "#000" },
            'red-on-white': { "color": "#f00", "background-color": "#fff" },
            'green-on-white': { "color": "#0f0", "background-color": "#fff" },
            'blue-on-white': { "color": "#00f", "background-color": "#fff" },
            'black-on-white': { "color": "#000", "background-color": "#fff" }
        },
    },

    _create: function() {
        var self = this;
        for (var themeName in self.options.themes) {
            this.element.find('.' + themeName).click(function(event) {
                event.preventDefault();
                var themeName = $.trim($(this).attr('class'));
                cvm.selection().style(self.options.themes[themeName]);
                self.options.container.dialog( "close" );
            });
        }
        this.element.find('.cancel').click(function() {
            event.preventDefault();
            self.options.container.dialog( "close" );
        });
    },
});
})(jQuery);


(function( $, undefined ) {
$.widget( "fortylines.shapePicker", {
    options: {
        container: null,
    },

    _create: function() {
        var self = this;
        var shapes = [ 'bin', 'oct', 'dec', 'hex',
                       'inv-bin', 'inv-oct', 'inv-dec', 'inv-hex',
                       'bin-rev', 'oct-rev', 'dec-rev', 'hex-rev',
                       'analog', 'gradient' ];
        for( var i = 0; i < shapes.length; ++i ) {
            var shapeName = shapes[i];
            this.element.find('.' + shapeName).click(function(event) {
                event.preventDefault();
                var shapeName = $.trim($(this).attr('class'));
                cvm.selection().shape(shapeName);
                self.options.container.dialog( "close" );
            });
        }
        this.element.find('.cancel').click(function() {
            event.preventDefault();
            self.options.container.dialog( "close" );
        });
    },
});
})(jQuery);


(function( $, undefined ) {
$.widget( "fortylines.waveWidget", {
    options: {
        /* dimensions of the canvas on which the waveform is drawn */
        height: 20,
        width: 800,

        /* time range that is displayed by the ruler.
           (must be included in full window) */
        disp_start_time: 0,
        disp_end_time: 1000,
    },

    _create: function() {
    },

    _setOption: function( key, value ) {
        var int_value = parseInt(value, 10);
        if( key === "disp_start_time" ) {
            /* Modiyfing the start time results in a translation
               of the display window. */
            this.options[ "disp_end_time" ] = int_value
                + (this.options.disp_end_time - this.options.disp_start_time);
            this.options[ key ] = int_value;
        } else if( key === "disp_end_time" ) {
            /* Modiyfing the end time results in a scaling
               of the display window. */
            this.options[ key ] = int_value;
        } else if( key === "width" ) {
            /* We changed the width of the element containing the canvas. */
            this.element.width(int_value);
            this.options[ key ] = int_value;
        } else {
            this._super(key, value);
        }
    },

    /** Returns pixel offset from the left border of convas
        on which a timestamp falls using the appropriate scale. */
    _pixel_offset_from_time: function(ctx, timestamp) {
        var disp_start_time = this.options.disp_start_time;
        var disp_end_time = this.options.disp_end_time;
        return Math.round(((timestamp - disp_start_time) * ctx.canvas.width)
                          / (disp_end_time - disp_start_time));
    },
});
})(jQuery);

(function( $, undefined ) {
$.widget( "fortylines.waveform", $.fortylines.waveWidget, {

    options: {
        /* identifier code of the variable and its values as a list of
           (timestamp, value) tuple. */
        path: null,
        shape: null,
        values: [],
        bitsize: 1,
        blockShapes: ['bin', 'oct', 'dec', 'hex',
                      'inv-bin', 'inv-oct', 'inv-dec', 'inv-hex',
                      'bin-rev', 'oct-rev', 'dec-rev', 'hex-rev' ],
        curveShapes: ['analog'],
        gradShapes: ['gradient'],
    },

    _create: function() {
        var $this = this;
        var container = document.createElement("div");
        $this.element.append(container);
        $this.options.svg = d3.select(container)
            .append("svg")
            .attr("width", $this.options.width)
            .attr("height", $this.options.height);

        // Extract bitsize from the pathname
        var first = this.options.path.lastIndexOf('['),
        last = this.options.path.lastIndexOf(']');
        if( first > 0 && last > 0 ) {
            var bounds = this.options.path.substring(first+1, last).split(":"),
            upper = parseInt(bounds[0]),
            lower = parseInt(bounds[1]);
            this.options.bitsize = upper - lower + 1;
        }
        this.update();
    },

    update: function(){
        var $this = this;
        $.getJSON(responsive_waves_api.time_records,
                  { 'vars': '["' + $this.options.path + '"]',
                    'start_time': $this.options.disp_start_time,
                    'end_time': $this.options.disp_end_time,
                    'res': Math.floor(($this.options.disp_end_time
                                       - $this.options.disp_start_time)
                                      / $this.options.width) },
                  function success(data, textStatus, jqXHR) {
                      $this.options.values = data[$this.options.path];
                      $this._render();
                  });
    },

    /** returns _value_ as a formatted string based on the _shape_
     parameter ('bin', 'oct', 'dec', 'hex').
     _value_ is a string either representing a number in base 2 encoding
     or a single character that indicates an invalid value (i.e. 'X', 'Z') */
    _stringFromShape: function(value, shape, bitsize) {
        var leadingChar;
        if( value.charAt(0) === '0' || value.charAt(0) === '1' ) {
            leadingChar = '0';
        } else {
            leadingChar = value.charAt(0);
        }
        var result;
            if(bitsize - value.length > 0) {
                result = Array(
                    bitsize + 1 - value.length).join(leadingChar) + value;
            } else {
                result = value;
            }
        var intVal = parseInt(value, 2),
        base = 2;
        if( isNaN(intVal) ) {
            return result;
        }
        if( shape.indexOf('inv') >= 0 ) {
            intVal = ~intVal;
        }
        if( shape.indexOf('oct') >= 0 ) {
            result = intVal.toString(8);
        } else if( shape.indexOf('dec') >= 0 ) {
            result = intVal.toString(10);
        } else if( shape.indexOf('hex') >= 0 ) {
            result = intVal.toString(16);
        }
        if( shape.indexOf('rev') >= 0 ) {
            result = result.split("").reverse().join("");
        }
        return result;
    },

    _render: function() {
        var $this = this,
        disp_start_time = $this.options.disp_start_time,
        disp_end_time = $this.options.disp_end_time,
        width = $this.options.width,
        data = $this.options.values,
        shape = $this.options.shape;

        var strokeStyle = $this.element.css('color'),
        fillStyle = $this.element.css('background-color');

        // *x* scale will fit all values from data[] within pixels 0-w
        var x = d3.scale.linear()
            .domain([disp_start_time, disp_end_time])
            .range([0, width]);

        var bitsize = $this.options.bitsize,
        maxval = (1 << $this.options.bitsize) - 1,
            y = d3.scale.linear()
            .domain([0, maxval])
            .range([0, $this.options.height]);

        /* Draw the value change waveform. Here we recreate the whole SVG DOM
           tree instead of using d3js update feature. This seems more
           appropriate since there is often very little relationship between
           two subsquent datasets. */
        if( shape && $this.options.values && $this.options.values.length > 0 ) {
            if( $.inArray(shape, $this.options.curveShapes) >= 0 ) {

                function orthseg(elem, prev, next) {
                    /* prev   next     | drawn        hazard
                       valid   valid   |  H+V         none
                       valid   invalid |  H           none
                       invalid valid   |  M(next)     rect
                       invalid invalid |  none        rect
                     */
                    prevValue = parseInt(prev ? prev[1] : "X", 2);
                    prevTime = parseInt(prev ? prev[0] : "T");
                    if( isNaN(prevTime) ) {
                        prevTime = 0;
                    }
                    nextValue = parseInt(next ? next[1] : "X", 2);
                    nextTime = parseInt(next ? next[0] : "T");
                    if( isNaN(nextTime) ) {
                        nextTime = disp_end_time;
                    }
                    if( !isNaN(prevValue) ) {
                        /* Previous value is valid */
                        if( !isNaN(nextValue) ) {
                            return "H" + x(nextTime) + "V" + y(nextValue);
                        } else {
                            return "H" + x(nextTime);
                        }
                    } else {
                        prevValue = prev ? prev[1] : "U";
                        hazardWidth = x(nextTime) - x(prevTime);
                        hazard = elem.append("g");
                        hazard.append("rect")
                            .attr("x", x(prevTime))
                            .attr("y", y(0))
                            .attr("height", y(maxval))
                            .attr("width", hazardWidth);
                        hazard.append("text")
                            .attr("class", "svg-wave-text")
                            .attr("x", x(prevTime) + hazardWidth / 2)
                            .attr("y", y(maxval / 2))
                            .text(prevValue);
                        if( !isNaN(nextValue) ) {
                            return "M" + x(nextTime) + "," + y(nextValue);
                        }
                    }
                    return "";
                }

                function orthwave(elem, data) {
                    var drawn = orthseg(elem, null, data[0]);
                    for( i = 0; i < data.length - 1; ++i ) {
                        drawn += orthseg(elem, data[i], data[i+1]);
                    }
                    drawn += orthseg(elem, data[data.length - 1], null);
                    return drawn;
                }

                values = $this.options.svg.selectAll(".little");
                values.remove();
                values = $this.options.svg.append("g")
                    .attr("class", "little")
                    .attr("stroke", strokeStyle)
                    .attr("fill", fillStyle);
                values.append("path")
                  .attr("transform","translate(0, "+y(maxval)+") scale(1, -1)")
                  .attr("d", orthwave(values, data));

            } else if( $.inArray(shape, $this.options.blockShapes) >= 0 ) {
                /* This is a lot easier here, we have a sequence of polygons
                   with same shape. */
                var prevTime, nextTime;
                values = $this.options.svg.selectAll(".little");
                values.remove();
                values = $this.options.svg.append("g")
                    .attr("class", "little")
                    .attr("stroke", strokeStyle)
                    .attr("fill", fillStyle);
                for( i = 0; i < data.length - 1; ++i ) {
                    prevTime = x(data[i][0]);
                    nextTime = x(data[i+1][0]);
                    points = " " + prevTime + "," + y(maxval / 2)
                            + " " + (prevTime + 5) + "," + y(0)
                            + " " + (nextTime - 5) + "," + y(0)
                            + " " + nextTime     + "," + y(maxval / 2)
                            + " " + (nextTime - 5) + "," + y(maxval)
                            + " " + (prevTime + 5) + "," + y(maxval);
                    middle = prevTime + (nextTime - prevTime) / 2;
                    values.append("polygon")
                        .attr("points", points);
                    values.append("text")
                        .attr("class", "svg-wave-text")
                        .attr("x", middle)
                        .attr("y", y(maxval / 2))
                        .text($this._stringFromShape(
                            data[i][1], shape, bitsize));
                }
                prevTime = x(data[data.length - 1][0]);
                nextTime = x(disp_end_time);
                points = " " + prevTime + "," + y(maxval / 2)
                    + " " + (prevTime + 5) + "," + y(0)
                    + " " + (nextTime - 5) + "," + y(0)
                    + " " + nextTime     + "," + y(maxval / 2)
                    + " " + (nextTime - 5) + "," + y(maxval)
                    + " " + (prevTime + 5) + "," + y(maxval);
                middle = prevTime + (nextTime - prevTime) / 2;
                values.append("polygon")
                    .attr("points", points);
                values.append("text")
                    .attr("class", "svg-wave-text")
                    .attr("x", middle)
                    .attr("y", y(maxval / 2))
                    .text($this._stringFromShape(
                        data[data.length - 1][1], shape, bitsize));

            } else if( $.inArray(shape, $this.options.gradShapes) >= 0 ) {
                /* Values as a color gradient. */
                console.log('XXX not yet implemented: as a color gradient');
            }
        }
    }
});
})(jQuery);


(function( $, undefined ) {
$.widget( "fortylines.timeruler", $.fortylines.waveWidget, {
    options: {
        height: 50,
        /* context options which are not in the css. */
        lineWidth: .5,
    },

    _create: function() {
        var self = this,
        control = this.element;
        domCanvas = document.createElement("canvas");
        domCanvas.style.zIndex = 0;
        domCanvas.height = this.options.height;
        domCanvas.width = this.options.width;

        this.element.append(domCanvas);
        this.refresh(this.options.disp_start_time, this.options.disp_end_time);
    },

    update: function(){
        this._render();
    },

    refresh: function( first, last ) {
        this.options.disp_start_time = parseInt(first, 10);
        this.options.disp_end_time = parseInt(last, 10);
        this._render();
    },

    _render: function() {
        var $this = this,
        canvas_ref = $this.element.find('canvas')[0],
        disp_start_time = $this.options.disp_start_time,
        disp_end_time = $this.options.disp_end_time,
        ctx = canvas_ref.getContext('2d');

        /* Resize the canvas to fill the parent element.
           This also clears the canvas as a side effect. */

        ctx.canvas.width = Math.floor($this.element.width()) - 1;

        // XXX defaults
        ctx.lineWidth= this.options.lineWidth;
        ctx.strokeStyle = this.element.css('color');
        ctx.fillStyle = this.element.css('color');

        var textheight = getTextHeight(ctx.font).height;
        var drawoffset = 100;
        var nextclear = 0;
        var offset;

        for( var ctr = disp_start_time; ctr < disp_end_time; ctr += 50 ) {
            var text = ctr;
            var x = $this._pixel_offset_from_time(ctx, ctr);
            var textwidth = ctx.measureText(text).width;
            var xpos = Math.round( x - textwidth / 2);
            if( xpos >= nextclear ){
                ctx.fillText(text, xpos, ctx.canvas.height - 50 + textheight);
                nextclear = xpos + textwidth + 2;
            }
            ctx.beginPath();
            ctx.moveTo(x + .5, 0);
            ctx.lineTo(x + .5, 5);
            ctx.stroke();
        }
    }
});
})(jQuery);

(function( $, undefined ) {
$.widget( "fortylines.slidingWindow", $.ui.slider, {
    widgetEventPrefix: "slide",

    options: {
        range: true,

        /* full time range of the trace dump. */
        max: 1000,
        min: 0,

        /* time range that is displayed by the ruler.
           (must be included in full window) */
        values: [0, 1000]
    },

    startTime: function() {
        return this.options.values[0];
    },

    endTime: function() {
        return this.options.values[1];
    },

    _create: function() {
        this._super('_create');
        this.refresh(this.startTime(), this.endTime());
    },

    _change: function( event, index ) {
        if ( !this._keySliding && !this._mouseSliding ) {
            if( index == 0 ) {
                this.refresh( event, this.endTime() );
            } else /* right */ {
                this.refresh( this.startTime(), event );
            }
            var uiHash = {
                handle: this.handles[ index ],
                value: this.value()
            };
            if ( this.options.values && this.options.values.length ) {
                uiHash.value = this.values( index );
                uiHash.values = this.values();
            }
            this._trigger( "change", event, uiHash );
        }
    },

    _slide: function( event, index, newVal ) {
        if( index == 0 ) {
            this.refresh( event, this.endTime() );
        } else /* right */ {
            this.refresh( this.startTime(), event );
        }
    },

    _setOption: function( key, value ) {
        var int_value = parseInt(value, 10);
        if( key === "disp_start_time" ) {
            /* Modiyfing the start time results in a translation
               of the display window. */
            this.options.values[1] = int_value
                + (this.endTime() - this.startTime());
            this.options.values[0] = int_value;
        } else if( key === "disp_end_time" ) {
            /* Modiyfing the end time results in a scaling
               of the display window. */
            this.options.values[1] = int_value;
        } else if( key === "width" ) {
            /* We changed the width of the element. */
            this.element.width(int_value);
        } else {
            this._super(key, value);
        }
    },

    /** Returns an offset (as percent units) from the left border
        on which a timestamp falls using the appropriate scale.
    */
    _percent_from_time: function(val) {
        var step = 1,
          width = this.element.find('.ui-slider-track').outerWidth(),
          min = this.options.min,
          max = this.options.max;

        val = parseFloat(val);
        if ( isNaN(val) ) {
            return;
        }

       // From jQuery UI slider, the following source will round
        // to the nearest step.
        var pxStep = width / ( (max - min) / step ),
            valModStep = ( val - min ) % step;
        var alignValue = val - valModStep;

        if ( Math.abs(valModStep) * 2 >= step ) {
            alignValue += ( valModStep > 0 ) ? step : ( -step );
        }

        var percentPerStep = 100 / ((max - min) / step);
        // Since JavaScript has problems with large floats, round
        // the final value to 5 digits after the decimal point
        // (see jQueryUI: #4124)
        val = parseFloat( alignValue.toFixed(5) );

        percent = ( val - min ) * percentPerStep * ( 1 / step );

        if ( percent < 0 ) {
            percent = 0;
        }
        if ( percent > 100 ) {
            percent = 100;
        }
        return percent;
    },

    _time_from_event: function (event) {
        var pageX = event.pageX,
        min = this.options.min,
        max = this.options.max,
        left = this.element.find('.ui-slider-track').offset().left,
        width = this.element.find('.ui-slider-track').outerWidth(),
        offset = pageX - left;

        if( offset < min ) offset = min;
        if( offset > max ) offset = max;
        first = Math.round( ( offset / width ) * (max - min) );
        return first;
    },

    update: function(){
        this.refresh(this.startTime(), this.endTime());
    },

    _refreshValue: function() {
    },

    refresh: function( first, last ) {
        var step = 1,
        min = this.options.min,
        max = this.options.max;

        if ( typeof first === "object" ) {
            pageX = first.pageX;
            pageY = first.pageY;
            first = this._time_from_event(first);
            last = first + (this.endTime() - this.startTime());
        } else if ( typeof last === "object" ) {
            pageX = last.pageX;
            pageY = last.pageY;
            last = this._time_from_event(last);
        }
        if ( first === undefined || last === undefined ) {
            return;
        }

        // Clip [first, last[ according to constraints.
        if( first < min ) {
            first = min;
        }
        if( last > max ) {
            last = max;
        }
        if( first > (last - 30) ) {
            first = last - 30;
        }

        var newDispStartPercent = this._percent_from_time(first),
          newDispEndPercent = this._percent_from_time(last);

        var disp = this.element.find(".ui-ruler-disp-track");
        disp.css( "left", newDispStartPercent + "%" );
        disp.css("width", (newDispEndPercent - newDispStartPercent) + "%");
        this.options.values[0] = first;
        this.options.values[1] = last;
    }
});
})(jQuery);

String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

var ObservableVariable = function(path, style, shape) {
    this.path = ko.observable(path);
    this.style = ko.observable(style);
    this.shape = ko.observable(shape);

    this.label = ko.computed(function() {
        return this.path();
    }, this);

    this.inverseStyle = ko.computed(function() {
        return { color: this.style()['backgroundColor'],
                 backgroundColor: this.style()['color'],
                 borderColor: this.style()['color'] };
    }, this);

    /* Subscribe to observables so we can send updates
       back to the server. */
    function persist(newVal, id, key) {
        var data = {};
        data[key] = newVal;
        $.ajax({
            type: "PATCH",
            url: responsive_waves_api.update_variable + id,
            data: ko.toJSON(data),
            datatype: "json",
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                // nothing to be done
            }
        }).fail(function(data) {
            showMessages([
                "An error occurred while updating a browser variable ("
                    + data.status + " " + data.statusText
                    + "). Please accept our apologies."], "danger");
        });
    }
    function makePersist(id, key) {
        return function(newVal) {
            persist(newVal, id, key);
        };
    }

    this.style.subscribe(makePersist(this.path(), "style"));
    this.shape.subscribe(makePersist(this.path(), "shape"));
};

function createBrowseFunc(q) {
    return function(event) {
        var self = cvm;
        event.preventDefault();
        self.query(q);
    }
}

/** Value Change Browser Application. */
function VCBViewModel(variable_list) {
    var self = this; // <3 JS !

    self.disp_start_time = ko.observable(0);
    self.disp_end_time = ko.observable(1000);
    self.disp_width = ko.observable(800);

    self.variables = ko.observableArray(
        ko.utils.arrayMap(variable_list, function(variable) {
            return new ObservableVariable(
                variable.path, variable.style, variable.shape);
        }));

    self.candidates = ko.observableArray();
    self.query = ko.observable("");
    self.showRemoveButton = ko.observable(false);

    self.selected = null;


    self.selection = function() {
        return self.selected
    }

    self.setSelected = function( element ) {
        self.selected = element
    }

    self.add_variable = function( path, style, shape ) {
        self.variables.push(new ObservableVariable(path, style, shape));
    }

    /* Add rows into the waveform display table for each variable specified
       in *variable_list*. */
    self.add_wave = function( panel ) {

        self.query.subscribe(function(newValue) {
            // load variables
            $.getJSON(responsive_waves_api.list_variables,
                { 'q': newValue },
                function success(data, textStatus, jqXHR) {
                    self.candidates.removeAll()
                    for( i = 0; i < data.length; ++i ) {
                        variable = data[i];
                        self.candidates.push(new ObservableVariable(
                            variable.path, variable.style, variable.shape));
                    }
                }).fail(function() {
                    showMessages([$('.browser-panel').attr('id')
                                  + ': trace not found.'], 'danger');
                });

            var li = null;
            var $this = $("#variables_list #prefix");
            var pat=/^\/(\w+)(\/.*)/;
            var list = pat.exec(newValue);
            var prefix = ''
            $this.empty();
            while( list ) {
                prefix = prefix + '/' + list[1]
                if( li ) {
                    $this.append(li);
                }
                var q = prefix + '/[^/]+/?$'
                var link = $('<button class="btn" href="#">');
                link.append(list[1] + "/");
                link.click(createBrowseFunc(q));
                li = $("<li>");
                li.append(link);
                list = pat.exec(list[2]);
            }
        });

        self.showRemoveButton.subscribe(function(newValue) {
            $this = $("#removeToggle")
            if( newValue ) {
                $this.text(" Edit ");
            } else {
                $this.text("Remove");
            }
        });


        /* Subscribe to the observable array so we can send ordering
           updates back to the server. */
           self.variables.subscribe(function(newValue) {
               var ranks = new Array();
               for( var index = 0; index < self.variables().length; ++index ) {
                   ranks[index] = self.variables()[index].path();
               }
               $.ajax({
                    type: "PUT",
                    url: responsive_waves_api.update_ranks,
                    data: ko.toJSON(ranks),
                    datatype: "json",
                    contentType: "application/json; charset=utf-8",
                    success: function(data) {
                        // nothing to be done
                    }
                });
               $(".browser-panel").height($(".browser-panel .variables-panel").height());
            });
    }
}

function browserCreate(browser, variable_list) {

    var cvm = new VCBViewModel(variable_list);

    function toggle_tools() {
        var edit_wave_panel = browser.find('.edit-waveforms-panel');
        var edit_panel = edit_wave_panel.find('.edit-panel');
        var left_pos =  parseInt(edit_wave_panel.css('left'), 10);
        edit_tools_width = 150;
        if( left_pos < 250 ) {
            browser.find('.variables-edit-tools-toggle').text('Done');
            edit_wave_panel.animate({left: '+=' + edit_tools_width }, 500,
                function() {
                    edit_wave_panel.css('z-index', 40 /* edit-panel-visible */);
                });
        } else {
            browser.find('.variables-edit-tools-toggle').text('Edit');
            edit_wave_panel.css('z-index', 30 /* edit-panel-hidden */);
            edit_wave_panel.animate({left: '-=' + edit_tools_width }, 500);
        }
    }

    browser.find('.variables-edit-tools-toggle').click(function(event) {
        event.preventDefault();
        toggle_tools();
    });

    return cvm;
}

/** sets the query to return toplevel variables and modules */
function topClick(event) {
    var self = cvm;
    // this is the ObservableVariable :)
    self.query('/[^/]+/?$');
}

/** sets the query to empty, no candidates panel */
function clearClick(event) {
    var self = cvm;
    // this is the ObservableVariable :)
    self.query('');
}

function downNodeClick(event) {
    var self = cvm;
    // this is the ObservableVariable :)
    self.query('/' + this.path() + '[^/]+/?$');
}

function addVariableClick(event) {
    var self = cvm;
    // *this* is the ObservableVariable :)
    self.add_variable(this.path(), this.style(), this.shape());
}


function removeVariableClick() {
    var self = cvm;
    // this is the ObservableVariable :)
    self.variables.remove(this);
}

function toggleRemoveButtonClick() {
    var self = cvm;
    // this is the ObservableVariable :)
    self.showRemoveButton(!self.showRemoveButton());
}

function updateShapeClick(event) {
    var self = cvm;
    self.setSelected(this);
    $('#shape-picker-container').dialog({modal: true, width: "200px"});
}

function updateColorClick(event) {
    var self = cvm;
    self.setSelected(this);
    $('#color-picker-container').dialog({modal: true});
}

function updateRankDrop( event, ui ) {
    var $this = $(this)
    var self = cvm;

    var target_index = $this.parent().parent().parent().index();
    var source_index = ui.draggable.parent().parent().parent().index();

    ui.draggable.css('top', '0');
    ui.draggable.css('left', '0');

    source_entry = self.variables()[source_index];
    if( source_index > target_index ) {
        for( var index = source_index; index > target_index; --index ) {
            self.variables()[index] = self.variables()[index - 1];
        }
    } else {
        for( var index = source_index; index < target_index; ++index ) {
            self.variables()[index] = self.variables()[index + 1];
        }
    }
    self.variables()[target_index] = source_entry;
    self.variables.valueHasMutated();
}


function browserResize(browser, cvm) {
    var wave_panel_width = browser.width() - 250;
    cvm.disp_width(wave_panel_width);
}

(function($, undefined) {

    ko.bindingHandlers.draggable = {
        init: function (element, valueAccessor, allBindingsAccessor,
                        viewModel, bindingContext) {
            var options = allBindingsAccessor().draggable || {};
            $(element).draggable(options);
        },
    };

    ko.bindingHandlers.droppable = {
        init: function (element, valueAccessor, allBindingsAccessor,
                        viewModel, bindingContext) {
            var options = allBindingsAccessor().droppable || {};
            $(element).droppable(options);
        },
    };

    ko.bindingHandlers.slider = {
        init: function (element, valueAccessor, allBindingsAccessor,
                        viewModel, bindingContext) {
            var options = allBindingsAccessor().percentageSliderOptions || {};
            $(element).slidingWindow(options);
            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                $(element).slider("destroy");
            });
            ko.utils.registerEventHandler(element, "slidechange", function () {
                /* It is important we keep a copy of startTime and endTime
                   before updating the observables. */
                var startTimeObservable = valueAccessor()['disp_start_time'],
                  endTimeObservable = valueAccessor()['disp_end_time'],
                  startTime = $(element).slidingWindow("startTime"),
                  endTime = $(element).slidingWindow("endTime");

                endTimeObservable(endTime);
                startTimeObservable(startTime);
            });
        },

        /* The updates to the slider that where not triggered by the slider
           itself will be done through the jquery binding. */
    };

/* Reference from
   https://github.com/SteveSanderson/knockout/wiki/Bindings---jqueryui-widgets
*/
    ko.bindingHandlers['jqueryui'] = {
        update: function(
            element, valueAccessor, allBindingsAccessor, viewModel) {
            var widgetBindings = _getWidgetBindings(
                element, valueAccessor, allBindingsAccessor, viewModel);

            // Attach the jQuery UI Widget and/or update its options.
            // (The syntax is the same for both.)
            $(element)[widgetBindings.widgetName](widgetBindings.widgetOptions);
            $(element)[widgetBindings.widgetName]("update");
        }
    };

    function _getWidgetBindings(
        element, valueAccessor, allBindingsAccessor, viewModel) {
        // Extract widgetName and widgetOptions from the data binding,
        // with some sanity checking and error reporting.
        // Returns dict: widgetName, widgetOptions.

        var value = valueAccessor(),
            myBinding = ko.utils.unwrapObservable(value),
            allBindings = allBindingsAccessor();

        if (typeof(myBinding) === 'string') {
            // Short-form data-bind='jqueryui: "widget_name"'
            // with no additional options
            myBinding = {'widget': myBinding};
        }

        var widgetName = myBinding.widget,
            widgetOptions = myBinding.options; // ok if undefined

        // Sanity check: can't directly check that it's truly a _widget_, but
        // can at least verify that it's a defined function on jQuery:
        if (typeof $.fn[widgetName] !== 'function') {
            throw new Error("jqueryui binding doesn't recognize '" + widgetName
                + "' as jQuery UI widget");
        }

        // Sanity check: don't confuse KO's 'options' binding
        // with jqueryui binding's 'options' property
        if( allBindings.options && !widgetOptions && element.tagName
            !== 'SELECT') {
            throw new Error("jqueryui binding options should be specified like this:\n"
                + "  data-bind='jqueryui: {widget:32f00c915f33483b915ab82fa06f475f1c9946a3quot;" + widgetName + "32f00c915f33483b915ab82fa06f475f1c9946a3quot;, options:{...} }'");
        }

        return {
            widgetName: widgetName,
            widgetOptions: widgetOptions
        };
    }
})(jQuery);


/** XXX This looks like a hack. Still easiest way to get that init code
    setup until we figure out something better. */
function initWaveBrowserWhenDocumentReady(csrf_token, variable_list) {
    cvm = browserCreate($(".browser-panel"), variable_list);
    ko.applyBindings( cvm );
    cvm.add_wave($(".browser-panel"));
    cvm.query("/[^/]+/$");
    browserResize($(".browser-panel"), cvm);

    $('#color-picker').colorPicker({ container: $('#color-picker-container') });
    $('#shape-picker').shapePicker({ container: $('#shape-picker-container') });

    $(window).resize(function() {
        browserResize($(".browser-panel"), cvm);
    });
}

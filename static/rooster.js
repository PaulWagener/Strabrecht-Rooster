var colors = [
    // Blue
    {
        border: 'rgb(27, 173, 248)',
        background: 'rgba(191, 233, 255, 0.6999)',
        text: 'rgb(17, 111, 159)'
    },
    // Green
    {
        border: 'rgb(101, 219, 57)',
        background: 'rgba(209, 255, 191, 0.699)',
        text: 'rgb(60, 130, 34)'
    },
    // Red
    {
        border: 'rgb(255, 45, 85)',
        background: 'rgba(255, 191, 203, 0.699)',
        text: 'rgb(166, 29, 55)'
    },
    // Yellow
    {
        border: 'rgb(255, 204, 0)',
        background: 'rgba(255, 242, 191, 0.699)',
        text: 'rgb(166, 133, 0)'
    },
    // Purple
    {
        border: 'rgb(204, 115, 225)',
        background: 'rgba(243, 191, 255, 0.699)',
        text: 'rgb(123, 68, 136)'
    },
    // Brown
    {
        border: 'rgb(162, 132, 94)',
        background: 'rgba(224, 211, 193, 0.699)',
        text: 'rgb(77, 60, 38)'
    }
    ];
angular.module('RoosterApp', ['ui.bootstrap'])
.config( [
    '$compileProvider',
    function( $compileProvider )
    {
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|webcal):/);
    }
])
.controller('RoosterController', function($scope, $http) {
    $scope.activeSources = [];
    $scope.sources = window.sources;

    $(JSON.parse(localStorage['activeTitles'] || '[]')).each(function(i, title) {
        $($scope.sources).each(function(i, source) {
            if(source.title == title) {
                $scope.activeSources.push(source);
            }
        })
    });

    $scope.$watchCollection('activeSources', function(newSources, oldSources) {
        if(newSources == oldSources)
            oldSources = [];

        // Set colors
        $(newSources).each(function(i, e){
            var color = colors[i % colors.length];
            e.backgroundColor = color.background;
            e.borderColor = color.border;
            e.textColor = color.text;
        });

        // Remove old sources
        $(oldSources).not(newSources).each(function(i, e) {
            $('#calendar').fullCalendar('removeEventSource', e)
        });

        // Add new sources
        $(newSources).not(oldSources).each(function(i, e) {
            e.cache = true;
            $('#calendar').fullCalendar('addEventSource', e)
        });

        // Save in local storage
        var activeTitles = $(newSources).map(function(i, s) {return s.title;}).get();
        localStorage['activeTitles'] = JSON.stringify(activeTitles);
    });

    $scope.select = function(source) {
        $scope.selected = '';
        if($scope.activeSources.indexOf(source) == -1) {
            $scope.activeSources.push(source);
        }
    };
    $scope.remove = function(index) {
        $scope.activeSources.splice(index, 1);
    }

    // Set us up the calendar
    $('#calendar').fullCalendar({
        theme: true,
        weekends: false,
        allDaySlot: false,
        minTime: '8:00:00',
        maxTime: '18:00:00',
        timezone: 'local',
        axisFormat: 'H:mm',
        contentHeight: 8000,
        slotEventOverlap: false,
        defaultView: 'agendaWeek',
        header:{
          left: '',
          center: 'prev,title,next',
          right: 'today'
        },
        columnFormat: {
            month: 'ddd',    // Mon
            week: 'dd D', // Mon 9/7
            day: 'dddd'      // Monday
        },
        titleFormat: {
            month: 'MMMM YYYY', // September 2009
            week: "D MMMM YYYY", // Sep 13 2009
            day: 'MMMM D YYYY'  // September 8 2009
        },
        eventRender: function(event, element) {
            $(element).find('.fc-event-inner').append($('<div class="fc-event-location">'+event.location+'</div>'))
        },
        viewRender: function(view, element) {
            // Add HTML elements for styling

            // Title
            var h2 = $('#calendar .fc-header-title h2');
            var date_range = h2.text().substring(0, h2.text().lastIndexOf(" "));
            var year = h2.text().substring(h2.text().lastIndexOf(" "));
            h2.html('<strong>' + date_range + '</strong>' + year);

            // Day headers
            var th = $('#calendar thead .ui-widget-header').each(function(i, e) {
                var text = $(e).text();
                var day = text.substring(0, text.indexOf(" "));
                var date = text.substring(text.indexOf(" "));
                $(e).html('<span class="fc-date">'+date+'</span> <span class="fc-day">'+day.toLowerCase()+'</span>');
            });

            // Prev / next
            $('.fc-button-prev').html('<');
            $('.fc-button-next').html('>');
        },
        loading: function(isLoading, view) {
            $('#calendar').toggleClass('loading', isLoading);
        }
    }).fullCalendar( 'gotoDate', window.startdate);

    // Custom ctrl+f
    $(window).keydown(function(e){
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 70) {
            $('#select').focus();
            e.preventDefault();
        }
    });
});
// You know, for touch interfaces
$(function() {
    $(document.body).on('touchstart', '.source-container', function(e) {
        $(e.currentTarget).toggleClass('active');
    });
})
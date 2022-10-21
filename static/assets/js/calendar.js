(function ($) {
    'use strict';
    $(function () {
        if ($('#calendar').length) {
            var today = new Date();
            var date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
            var calendar = $('#calendar').fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,basicWeek,basicDay'
                },
                eventRender: function (event, element) {
                    var startTime = $.fullCalendar.formatDate(event.start, 'Y-MM-DD HH:mm:ss');
                    var endTime = event.end != null ? $.fullCalendar.formatDate(event.end, 'Y-MM-DD HH:mm:ss') : '';

                    var location = "";
                    $(element).popover({
                        title: event.title,
                        placement: 'top',
                        trigger: 'hover',
                        content: startTime + " to " + endTime + " " + location,
                        container: 'body'
                    }).popover('show');
                },
                defaultDate: date,
                navLinks: true, // can click day/week names to navigate views
                editable: true,
                eventLimit: true, // allow "more" link when too many events
                eventSources: [{
                    url: events_url + '&loadCalendarEvents=loadCalendarEvents', /* Set this to whatever is appropriate */
                    // data: function() {
                    //     var v = $('#calendar').fullCalendar('getView');
                    //     var start = today.getFullYear() + '-0' + (today.getMonth() + 1) + '-01';
                    //     var end=today.getFullYear() + '-0' + (today.getMonth() + 1) + '-28';;
                    //     if(v.start!==undefined){
                    //         start=v.start.format();
                    //         end=v.end.format();
                            
                    //     }
                    //   return {
                    //     '_start': start,
                    //     '_end': end,
                    //   };
                    // },
                  }],
                selectable: true,
                selectHelper: true,
                dayClick: function (start, allDay, jsEvent, view) {
                    

                    var popover = $(this).popover({
                        html: true,
                        title: '<h4>Actions <a class="fa fa-close pull-right"></a></h4>',
                        placement: 'top',
                        trigger: 'hover',
                        content: function () {
                            return `<a class="btn" id="new-task"><i class="fa fa-plus text-primary"></i> Add New Task</a>`;
                        },
                        container: 'body'
                    });
                    $('.popover').not(this).popover('hide');
                    popover.popover('toggle');
                    popover.on('shown.bs.popover', function () {
                        $('.popover-header a').click(function () {
                            popover.popover('hide');
                        });
                        $('.popover-body a').click(function () {
                            var key = $(this).attr("id");
                            var startFormatted = $.fullCalendar.formatDate(start, 'Y-MM-DD');
                            var endFormatted = startFormatted;//$.fullCalendar.formatDate(end, 'Y-MM-DD HH:mm:ss');

                            if (key === 'new-task') {
                                var title = prompt("Task Title");
                                if (title) {

                                    // calendar.fullCalendar('renderEvent', {
                                    //     title: title,
                                    //     start: start, end: start, allDay: allDay
                                    // }, true);
                                    calendar.fullCalendar("unselect");
                                    popover.popover('toggle');

                                    $.ajax({
                                        type: 'POST',
                                        url: events_url,
                                        data: { uploadUserTask: "uploadUserTask", content: title, start_time: startFormatted, end_time: endFormatted, user_id: user_id },
                                        success: function (html) {
                                            calendar.fullCalendar('refetchEvents');
                                        }
                                    });

                                    //Save the task in the database
                                    // calendar.fullCalendar('refetchEvents');
                                }
                            } else if (key === 'new-schedule') {
                                var startFormatted = $.fullCalendar.formatDate(start, 'Y-MM-DD');
                                showModal('index.php?modal=onboarding/add_employee_schedule&date=' + encodeURIComponent(startFormatted));
                            }
                            //custom logic
                        });
                    });
                },
                select: function (start, end, allDay) {
                    // var title = prompt("Task Title");

                    // if (title) {
                    //     var startFormatted = $.fullCalendar.formatDate(start, 'Y-MM-DD HH:mm:ss');
                    //     var endFormatted = $.fullCalendar.formatDate(end, 'Y-MM-DD HH:mm:ss');

                    //     calendar.fullCalendar('renderEvent',{
                    //         title:title,
                    //         start:start,end:end,allDay:allDay
                    //     },true);
                    //     calendar.fullCalendar("unselect");

                    //     $.ajax({
                    //         type: 'POST',
                    //         url: events_url,
                    //         data: {uploadUserTask: "uploadUserTask", content: title, start_time: startFormatted, end_time: endFormatted, user_id: user_id},
                    //         success: function (html) {

                    //         }
                    //     });

                    //     //Save the task in the database
                    //     calendar.fullCalendar('refetchEvents');
                    // }
                },
                eventResize: function (event) {
                    var start = $.fullCalendar.formatDate(event.start, 'Y-MM-DD HH:mm:ss'),
                        end = $.fullCalendar.formatDate(event.end, 'Y-MM-DD HH:mm:ss'),
                        title = event.title,
                        id = event.id;
                    //Save the task in the database
                    // calendar.fullCalendar('refetchEvents');

                },
                eventDrop: function (event) {//On moving the event form place to place
                    var start = $.fullCalendar.formatDate(event.start, 'Y-MM-DD HH:mm:ss'),
                        end = $.fullCalendar.formatDate(event.end, 'Y-MM-DD HH:mm:ss'),
                        title = event.title,
                        id = event.id;
                    $.ajax({
                        type: 'POST',
                        url: events_url,
                        data: { updateUserTask: "updateUserTask", id: id, content: title, start_time: start, end_time: end, user_id: user_id },
                        success: function (html) {
                        }
                    });
                    //Save the task changes in the database
                    calendar.fullCalendar('refetchEvents');
                },
                eventClick: function (event) {
                    var modal = $('#calendar-event'), timeContent = $.fullCalendar.formatDate(event.start, 'Y-MM-DD HH:mm:ss');
                    modal.modal('show');
                    modal.find('.modal-title').html(event.title);
                    modal.find('#event-description').html(event.description);
                    if (event.is_task) {
                        modal.find('#event-description').append(event.response_form);
                    }
                    if (event.end !== null) {
                        // timeContent+=' - ' + $.fullCalendar.formatDate(event.end, 'Y-MM-DD HH:mm:ss');
                    }
                    modal.find('#event-time').html(timeContent);
                    //loadCalendarEvent();
                }
            });
            // if($('#employee_meeting_schedule_form').length){
            $("#employee_meeting_schedule_form").submit(function(e) {
                e.preventDefault();
                alert("Here");
            });
        // }

            // function addEmployeeMeetingSchedule(date, month) {
            //     var user_ids = $('#scheduled_users').val();
            //     if (date && month && user)_ids {
            //         alert(user_ids);
            //     }
            // }
        }
    });
})(jQuery);
// *******************
// COMMON DECLARATIONS
// -------------------
// Version: 1.50
// Date: 08-12-2017

var keywords = new Object();
var script_version = 1;
var default_timeout = 100;
var default_loader_timeout = 300;

var IsDebug = 0;                  // Turn on/off Debug-mode  
var IsDeepDebug = 0;              // Turn on/off DeepDebug-mode  
var IsTrace = 0;                  // Turn on/off Trace-mode
var IsLog = 0;                    // Turn on/off console log
var IsTraceCommit = 0;            // Alert Field's state controller Commit-errors
var IsTraceRollback = 0;          // Alert Field's state controller Rollback-errors
var IsTraceErrorException = 0;    // Alert(show) error exception
var IsForcedRefresh = 0;          // Forced refresh any images in filesystem-cache (load with timestamp-link)
var IsAssumeExchangeError = 0;    // Exchange errors allowed or not (for localhost debug reasons)
var IsXMLDump = 0;                // For 'internal' only - dump request/response or not
var IsCleanBefore = 1;            // For 'internal' only - how to referesh items (clean before or not)
var IsCheckImageTimeout = 0;      // Wait images will be refreshed before init a new state
var IsTriggeredSubmit = 0;        // Show/Hide startup page
var IsShowLoader = 0;             // Apply submit image

// ---------------------------------------------------------
//  Line Page Submit Type:
//  0 - page submit, 1 - startup action, 2 - selected action
// ---------------------------------------------------------
var default_submit_mode = 0;
var default_action = null;        // Action for submit mode > 0
var default_log_action = null;    // Action for Log Tab
var default_input_name = '';      // Name of LINE input tag

var current_context = '';         // Current context name

var selected_menu_action = null;  // Selected DataMenu Action
var selected_control = null;      // Selected form's control

var semaphore_state = null;

// ==========================================================================================================

// ----------------
// Global Constants
// ----------------

var TID = new Array();

var LINE = '';
var SUBLINE = '';
var TABLINE = 'tabline';

var isWebServiceExecute = false;
var isSubmitted = false;
var isKeyboardDisabled = false;
var isConfirmation = false;
var isDropdownActive = false;

var confirm_action = '';

var DEFAULT_HTML_SPLITTER = ':';

// ------------
// Module items
// ------------

var baseURI = '';
var loaderURI = '';

var page_state = -1;

var is_loaded_success = false;
var is_show_error = false;

// ----------------
// Global Functions
// ----------------

function interrupt(start, mode, timeout, callback, index, type) {
    //
    //  start [true, false] - фаза исполнения: true-старт, false-финиш
    //  mode - индекс алгоритма
    //  timeout - длительность таймаута
    //  callback - функция обратного вызова[9] (строка) или строковый параметр[-1]
    //  index - индекс таймаута
    //  type - тип функции: setTimeout/setInterval
    //
    if (start) {
        var i = (index != null) ? index : TID.length;
        //var s = "interrupt(false, "+mode+", 0, "+(callback ? "'"+callback+"'" : 'null')+", "+i+")";
        var delay = timeout ? timeout : default_timeout;
        var func = function() { interrupt(false, mode, 0, callback, i, type); };
        if (i == TID.length) TID.push(null);
        TID[i] = (type === 1) ? window.setInterval(func, delay) : window.setTimeout(func, delay);

        if (IsLog)
            console.log('start:'+mode+', index:'+i+', len:'+TID.length);
    } else if (mode) {
        if (IsLog)
            console.log('interrupt:'+mode+', TID:'+TID.join('-'));

        if (mode == -1) {
            if (!callback) callback = '';
            window.location.replace(callback);
        } else if (mode == 1) {
            interrupt(false, 0, 0, null, index);
            $ShowOnStartup();
        } else if (mode == 9)
            $Semaphore.run(index);

    } else if (TID.length > index && TID[index] != null) {
        if (type === 1)
            window.clearInterval(TID[index]);
        else 
            window.clearTimeout(TID[index]);

        if (index == TID.length-1)
            TID.splice(index, 1);
        else
            TID[index] = null;

        if (IsLog)
            console.log('stop index:'+index+', len:'+TID.length);
    }
}

function $_screen_center(mode) {
    var f = !$IS_FRAME ? true : false;
    var m = mode || (f ? 'screen-max' : 'screen-min');
    return { 'W':$_width(m), 'H':$_height(m) };
}

function $_height(m) {
    //var ob = $(window);
    if (m == 'screen-max')
        return Math.max(window.screen.availHeight, verge.viewportH());
    if (m == 'screen-min')
        return Math.min(window.screen.availHeight, verge.viewportH());
    if (m == 'max')
        return Math.max(
            window.screen.height, 
            window.screen.availHeight, 
            document.body.clientHeight, 
            document.documentElement.clientHeight
            //ob.height()
        );
    else
        return Math.min(
            window.screen.height,
            window.screen.availHeight, 
            document.body.clientHeight, 
            document.documentElement.clientHeight
            //ob.height()
        );
}

function $_width(m) {
    //var ob = $(window);
    var f = !$IS_FRAME ? true : false;
    if (m == 'screen-max')
        return Math.max(window.screen.availWidth, verge.viewportW());
    if (m == 'screen-min')
        return Math.min(window.screen.availWidth, verge.viewportW());
    if (m == 'max')
        return Math.max(
            window.screen.width,                    // S
            window.screen.availWidth,               // W
            document.body.clientWidth,              // B
            document.documentElement.clientWidth    // H
            //ob.width()
        );
    else
        return Math.min(
            window.screen.width, 
            window.screen.availWidth, 
            document.body.clientWidth, 
            document.documentElement.clientWidth
            //ob.width()
        );
}

function $_get_item_id(ob, index) {
    var x = ob.attr('id') || 0;
    var id = (x && x.indexOf(DEFAULT_HTML_SPLITTER) > -1 && x.startswith('row')) ? x.split(DEFAULT_HTML_SPLITTER)[index || 1] : x;
    return id;
}

function $_set_body_value(id, value) {
    $("#"+id).each(function() { $(this).val(value); });
}

function $_init() {
    $ShowPageSubmitMessages();
    $Init();
    $ShowPage(false);
}

// ===============
// Action Handlers
// ===============

function $CurrentContext() {
    return current_context || 'default';
}

function $ShowPage(disable) {
    var startup_page_container = $("#html-container");
    if (disable)
        startup_page_container
            .hide();
    else
        startup_page_container
            .show();
}

function $ShowOnStartup() {
    selected_menu_action = default_log_action;
    $Go(
        selected_menu_action
    );
}

function $ShowPageSubmitMessages() {
    function _get_object(id) {
        var ob = $("#"+id);
        return !is_null(ob) ? ob.val() : null;
    }

    var errors = _get_object('errors');
    var OK = _get_object('OK');

    if (!is_empty(errors))
        $ShowError(errors, true, true, false);

    else if (!is_empty(OK))
        $NotificationDialog.open(OK);
}

function $ShowSystemMessages(reset, error) {}

function $TriggerActions(disable) {
    if (IsTriggeredSubmit && default_submit_mode == 0)
        $ShowPage(disable);
}

function $ShowError(msg, is_ok, is_err, is_session_close) {
    if (is_show_error || !msg)
        return;
    var container = $("#error-container");

    $("#error-text").html(msg);

    if (is_ok) {
        $("#error-button").append(
            '<button id="error-button-ok" class="ui-button-text" onclick="javascript:$HideError();">'+keywords['OK']+'</button>'
        );
    }
    if (is_err)
        container.removeClass("warning").addClass("error");
    else
        container.removeClass("error").addClass("warning");

    var f = !$IS_FRAME ? true : false;
    var c = $_screen_center('min');
    var top = (int((c.H-container.height())/2)-(f?20:0)).toString()+'px';
    var left = (int((c.W-container.width())/2)).toString()+'px';

    container
        .css('top', top).css('left', left)
        .show();
    is_show_error = true;

    $("#error-button-ok").focus();

    if (is_session_close && !$IS_DEMO) interrupt(true, -1, 5000, '', 0);
}

function $HideError() {
    $("#error-container").hide();
    $("#error-button").html('');
    is_show_error = false;

    $SetFocus();
}

function $ShowLoader(start) {
    //alert('loader:'+start+':'+isWebServiceExecute);

    if (start) {
        var loader = $("#page-loader");
        var container = $("#html-container");
        if (start == -1) { 
            isWebServiceExecute = false;
            if (IsShowLoader)
                loader.hide();
            else {
                container.removeClass("inprogress");
                $InProgress(null);
            }
        } else {
            isWebServiceExecute = true;
            if (IsShowLoader)
                loader.show();
            else
                container.addClass("inprogress");
        }
    }
}

function $InProgress(ob, mode) {
    if (!is_null(ob) && mode == 1) {
        ob.addClass("inprogress");
        selected_control = ob;
    }
    else if (!is_null(selected_control)) {
        selected_control.removeClass("inprogress");
        selected_control = null;
    }
}

function $SetFocus(ob) {}

function $ResetSearch(deactivate) {
    //
    // Set Search icon and clean search context box
    //
    if (deactivate)
        $_deactivate_search();

    var search = $("#search-context");

    if (search.val()) {
        var src = $SCRIPT_ROOT+'/static/img/';

        if (is_search_activated) {
            $("#search-icon")
                .attr('title', keywords['Cancel search'])
                .attr('src', src+'db-close.png');
        } else {
            $("#search-icon")
                .attr('title', keywords['Search'])
                .attr('src', src+'db-search.png');
            search.val('');
        }
    }
}

function $HideLogPage() {
    var ob = SelectedGetItem(SUBLINE, 'ob');
    if (!is_null(ob))
        $onToggleSelectedClass(SUBLINE, ob, 'remove', null);
}

function $ShowLogPage() {
    if (!is_null(current_subline))
        $onToggleSelectedClass(SUBLINE, current_subline, 'add', null);
}

function $ResetLogPage() {
    current_subline = null;
    $("#command").val('');
}

function $Go(action) {
    $web_logging(action, null);
}

function $Handle(action, handler, params) {
    $web_logging(action, handler, params);
}

// =======================
// Event's Action Handlers
// =======================

function $onParentFormSubmit(id) {
    var frm = $("#"+(id || 'filter-form'));
    var action = frm.attr('action');

    $SidebarControl.onBeforeSubmit();

    frm.submit();
}

function $onLineFormSubmit() {
    switch (default_submit_mode) {
        case 0:
            $onParentFormSubmit();
            break;
        case 1:
        case 2:
            $Go(default_action);
            break;
    }
}

function $onPageLinkSubmit(link) {
    var x = link.split('?');
    var url = x[0];
    var qs = x.length > 1 ? strip(x[1]) : '';

    url = url+'?'+(qs > '' ? qs+'&' : '')+'sidebar='+$SidebarControl.state.toString();

    window.location.replace(url);
}

function $onToggleSelectedClass(key, ob, action, command, force) {
    var id = !is_null(ob) ? $_get_item_id(ob) : SelectedGetItem(key, 'id');
    var mask = [LINE, SUBLINE, TABLINE].indexOf(key) > -1 ? 'td' : 'dd';
    var input = "input[name^='"+default_input_name+"']";

    if (isWebServiceExecute)
        return;

    //alert(id+':'+action+':'+mask+':'+input);

    function make(ob, action, mode) {
        $(mask, ob).each(function() {
            if (action == 'add') {
                $(this).addClass("selected");
                if (key == LINE && mode == 1)
                    $(input).each(function() { $(this).val(id); });
                SelectedSetItem(key, 'ob', ob);
            }
            else
                $(this).removeClass("selected");
        });
    }

    $("#command").val(!is_null(command) ? command : '');

    if (action == 'submit') {
        $(input).each(function() { $(this).val(id); });

        if (force) {
            $onParentFormSubmit();
            return;
        }

        if (default_submit_mode > 0) {
            make(SelectedGetItem(LINE, 'ob'), 'remove', 0);
            SelectedReset();
            make(ob, 'add', 0);
        }

        $onLineFormSubmit();
    }
    else if (action == 'clean') {
        $(input).each(function() { $(this).val(''); });
        SelectedSetItem(key, 'ob', null);
    } 
    else
        make(ob, action, 1);
}

function $setPaginationFormSubmit(page) {
    $("input[name='page']").each(function() { $(this).val(is_null(page) ? '1' : page.toString()); });
}

function $onOpenHelp() {
    $HelpDialog.open();
    return true;
}

function $onRefreshClick() {
    $("#command").val('refresh');
    $onParentFormSubmit();
}

function $onResetClick() {
    $("#command").val('init-filter');
    $onParentFormSubmit('init-form');
}

function $onExportClick() {
    $("#command").val('export');
    $onParentFormSubmit();
}

function $onControlPanelClick(ob) {
    if (isDropdownActive)
        return;

    var id = ob.attr('id');
    var dropdown = (
        id == "admin-panel-dropdown" ? $("#admin-panel") : (
        id == "services-dropdown" ? $("#services") : null
        ));
    var dropdown_id = dropdown.attr('id');
    //
    // Was another selected item open before?
    //
    var is_selected = !(is_null(selected_dropdown) || selected_dropdown[0].attr('id') == dropdown_id);

    isDropdownActive = true;

    if (is_selected)
        selected_dropdown[0].slideToggle('slow');

    dropdown.slideToggle('slow', function() {
        isDropdownActive = false;
    });

    //
    // Is selected item closed?
    //
    var is_closed = !is_null(selected_dropdown) && selected_dropdown[1] == dropdown_id;

    selected_dropdown = is_closed ? null : new Array(dropdown, dropdown_id);
}

// =======================
// Common Event Listeners
// =======================

jQuery(function($) 
{
    $("#sidebar-navigator").click(function(e) {
        $SidebarControl.onNavigatorClick(false);
    });

    $("#sidebarFrame").mouseenter(function(e) {
        $SidebarControl.onFrameMouseOver();
        e.stopPropagation();
    }).mouseleave(function(e) {
        if ((isIE || isFirefox) && $(this).has(e.target).length > 0) { 
            e.stopPropagation();
            return;
        }
        $SidebarControl.onFrameMouseOut();
        e.stopPropagation();
    });

    // ---------
    // Main Menu
    // ---------

    $("a.mainmenu").click(function(e) {
        var link = $(this).prop('href');
        $onPageLinkSubmit(link);
        e.preventDefault();
        return false;
    });

    // -----------------
    // Top Command Panel
    // -----------------

    $("#refresh").click(function(e) {
        $onRefreshClick();
        e.preventDefault();
    });

    $("#init-filter").click(function(e) {
        $onResetClick();
        e.preventDefault();
    });

    $("#export").click(function(e) {
        $onExportClick();
        e.preventDefault();
    });

    // ---------------------
    // Search context events
    // ---------------------

    function $onSearchSubmit(e) {
        var s = strip($("#search-context").val());
        if (s.length > 0) {
            search_context = s;
            $("#search-context").val(s);
            $("input[id='searched']").each(function() { $(this).val(s); });
            $LineSelector.onFormSubmit();
            $setPaginationFormSubmit(1);
            $onParentFormSubmit('filter-form');
        }
    }

    $("#search-context").focusin(function(e) {
        is_search_focused = true;
    }).focusout(function(e) {
        is_search_focused = false;
    });

    $("#search-icon").click(function(e) {
        $onSearchSubmit(null);
        $onParentFormSubmit('filter-form');
    });

    $("#search-form").submit(function(e) {
        $onSearchSubmit(e);
    });

    // -------------------
    // Dropdown Containers
    // -------------------

    $(".dropdown-link").click(function(e) {
        $onControlPanelClick($(this));
        e.preventDefault();
    });

    // ---------------
    // Activate window
    // ---------------

    $(window).focus(function() {
        $Semaphore.start(true);
    }).blur(function() {
        $Semaphore.stop(false);
    });

    // -------------
    // Resize window
    // -------------

    $(window).on("resize", function() {
        $SidebarControl.initState();
    });

    // ---------------
    // Navigator links
    // ---------------

    $("a.page").click(function(e) {
        var link = $(this).prop('href');
        $onPageLinkSubmit(link);
        e.preventDefault();
        return false;
    });

    // ---------------
    // Keyboard Events
    // ---------------

    $(window).keydown(function(e) {
        var exit = false;

        if (!e.ctrlKey && e.keyCode==116) {                      // F5 !!! IMPORTANT
            $onRefreshClick();
            exit = true;
        }

        if (e.shiftKey && e.keyCode==112)                        // Shift-F1
            exit = $onOpenHelp();

        //alert(e.keyCode);

        if ($LogSearchDialog.is_focused() || $TagSearchDialog.is_focused() || $ConfirmDialog.is_focused() || $NotificationDialog.is_focused() || isKeyboardDisabled)
            return;

        if (e.shiftKey && [67, 79].indexOf(e.keyCode) > -1) {    // Shift-C,Shift-O
            $SidebarControl.onNavigatorClick(false);
            exit = true;
        }

        else if (e.shiftKey && e.keyCode==82) {                  // Shift-R
            $onResetClick();
            exit = true;
        }

        else if (e.shiftKey && e.keyCode==83) {                  // Shift-S
            var focused = $("#search-context");
            $SidebarControl.onFrameMouseOver(focused);
            focused.focus();
            exit = true;
        }

        else if (e.ctrlKey || e.shiftKey) {
            if (isWebServiceExecute)
                return;
            /*
            if (e.keyCode > 0)
                alert(e.ctrlKey+':'+e.keyCode);

            else if (e.keyCode==13)                             // Ctrl-Enter
            */
            if (e.keyCode==38)                                  // Ctrl-Up
                exit = $LineSelector.up();
            else if (e.keyCode==40)                             // Ctrl-Down
                exit = $LineSelector.down();
            else if (e.ctrlKey && e.keyCode==36)                // Ctrl-Home
                exit = $LineSelector.home();
            else if (e.shiftKey && e.keyCode==33)               // Shift-PgUp
                exit = $LineSelector.pgup();
            else if (e.shiftKey && e.keyCode==34)               // Shift-PgDown
                exit = $LineSelector.pgdown();
            else if (e.ctrlKey && e.keyCode==35)                // Ctrl-End
                exit = $LineSelector.end();
            else if (e.keyCode==9)                              // Ctrl-Tab
                exit = $TabSelector.tab();
            else if (e.ctrlKey && e.keyCode==37)                // Ctrl-Left
                exit = $TabSelector.left();
            else if (e.ctrlKey && e.keyCode==39)                // Ctrl-Right
                exit = $TabSelector.right();
        }

        else if (e.altKey) {
            if (isWebServiceExecute)
                return;
            /*
            if (e.keyCode > 0)
                alert(e.altKey+':'+e.keyCode);
            */
            if (e.keyCode==38)                                  // Alt-Up
                exit = $SublineSelector.up();
            else if (e.keyCode==40)                             // Alt-Down
                exit = $SublineSelector.down();
            else if ([33, 36].indexOf(e.keyCode) > -1)          // Alt-Home:Alt-PgUp
                exit = $SublineSelector.home();
            else if ([34, 35].indexOf(e.keyCode) > -1)          // Alt-End:Alt-PgDown
                exit = $SublineSelector.end();
        }

        if (exit) {
            e.preventDefault();
            return false;
        }
    });
});

// ============
// WEB-SERVICES
// ============

function $web_semaphore(action) {
    if (isWebServiceExecute || !$Semaphore.isEnabled())
        return;

    if (IsLog)
        console.log('web_semaphore:', action);

    $Semaphore.running();

    var args = {
        'action'   : action,
        'template' : $Semaphore.template,
        'lid'      : $Semaphore.lid,
    };

    //alert(args.lid);

    $.post($SCRIPT_ROOT + '/semaphore/loader', args, function(x) {
        var state = x['state'];

        $Semaphore.refresh(state);

    }, 'json')
    .fail(function() {

        $Semaphore.error();

    })
    .always(function() {

    });
}


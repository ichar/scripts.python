﻿// ***********************************
// CARDS PAGE DECLARATION: /cards.html
// -----------------------------------
// Version: 1.50
// Date: 08-12-2017

default_submit_mode = 2;
default_action      = '700';
default_log_action  = '701';
default_input_name  = 'pers_id';

LINE    = 'pers';
SUBLINE = 'oper';

var is_noprogress = false;
var sid = 'selected-batches';
var selected_report_id = '';

// ----------------------
// Dialog Action Handlers
// ----------------------

function $_reset_current_sort() {
    current_page = 1;
}

function $_next_current_sort() {
    current_sort = current_sort == LOG_SORT.length-1 ? 0 : current_sort + 1;
    $_reset_current_sort();
}

function $_deactivate_search() {
    is_search_activated = false;
    search_context = '';
    current_page = 1;
}

function $_reset_item() {
    refresh_current_state = true;
    SelectedReset();
}

function $_reset_page() {
    SelectedReset();
    current_row_id = null;
}

function $_calculating_disabled() {
    return false;
}

// --------------
// Page Functions
// --------------

function sidebar_callback() {
    $onInfoContainerChanged();
}

function $Init() {
    $SidebarControl.init(sidebar_callback);

    page_sort_title = $("#sort_icon").attr('title');

    SelectedReset();

    $LineSelector.init();

    var parent = $("#line-content");
    var ob = $("tr[class~='selected']", parent);
    $onToggleSelectedClass(LINE, ob, 'add', null);

    $LineSelector.set_current(ob);

    $SublineSelector.init();

    var parent = $("#subline-content");
    var ob = $("tr[class~='selected']", parent);
    $onToggleSelectedClass(SUBLINE, ob, 'add', null);

    $SublineSelector.set_current(ob);

    $ShowMenu('data-menu-opers');

    $TabSelector.init();

    // ------------------------
    // Start default log action
    // ------------------------

    interrupt(true, 1);
}

function $ActivateInfoData(show) {
    var container = $("#info-data");

    if (show)
        container
            .show();
    else {
        container.hide();
        return;
    }

    $PageScroller.reset(true);
}

function $Confirm(mode, ob) {
    $ConfirmDialog.close();

    switch (mode) {
        case 0:
            break;
        case 1:
            if (['activate','reject'].indexOf(confirm_action) > -1) {
                var ids = $getSelectedItems();

                $("input[name='selected_pers_ids']").each(function() { $(this).val(ids); });
                $("#command").val('admin:'+confirm_action);

                $onParentFormSubmit();
            }
            break;
    }
}

function $Notification(mode, ob) {
    $NotificationDialog.close();
}

function $ShowMenu(id) {
    //
    // Show (open) selected DataMenu item (Tabs)
    //
    var opers = $("#subline-content");
    var logs = $("#logs-content");
    var units = $("#units-content");
    var params = $("#params-content");

    if (selected_data_menu)
        selected_data_menu.removeClass('selected');

    selected_data_menu = $("#"+id);

    opers.hide();
    logs.hide();
    units.hide();
    params.hide();

    if (id == 'data-menu-opers')
        opers.show();
    else if (id == 'data-menu-logs')
        logs.show();
    else if (id == 'data-menu-units')
        units.show();
    else if (id == 'data-menu-params')
        params.show();

    if (id == 'data-menu-opers' && SelectedGetItem(SUBLINE, 'id'))
        $ActivateInfoData(1);
    else
        $ActivateInfoData(0);

    selected_data_menu.addClass('selected');
    selected_data_menu_id = id;
}

function $onPaginationFormSubmit(frm) {
    return true;
}

function $onFilterFormSubmit(frm) {
    return true;
}

function $onInfoContainerChanged() {
    //alert($_width('screen-min')-$("#sidebarFrame").width()+':'+$("#line-table").width());
}

function $onTabSelect(ob) {
    var id = ob.attr("id");
    var action = 
        id == 'data-menu-logs' ? '702' : (
        id == 'data-menu-units' ? '703' : (
        id == 'data-menu-params' ? '704' : null
        ));

    selected_menu_action = action;

    if (action != null) {
        $InProgress(ob, 1);
        $Go(action);
    }
    else if (default_submit_mode > 1) {
        selected_menu_action = default_log_action;
        $InProgress(ob, 1);
        $Go(default_action);
    }
    else
        $ShowMenu(id);

    return true;
}

// -----------------------
// Custom Control Handlers
// -----------------------

function $addSelection(ob) {
    if (is_null(ob))
        return;

    var container = $("#"+sid);
    var oid = $_get_item_id(ob, 1);
    var is_break = false;

    $("option", container).each(function() {
        var x = $(this).attr('value');
        if (x == oid) {
            is_break = true;
            return;
        }
    });

    if (is_break)
        return;

    var options = container.prop("options");
    var option = new Option(oid, oid, false, false);
    //alert('add:'+ob.attr('id')+':'+oid+':'+container.length);
    options[options.length] = option;
}

function $removeSelection() {
    var container = $("#"+sid);
    //var oid = container.find(":selected").text();
    //alert('remove:'+oid+':'+container.length);
    $('option:selected', container).remove();
    $setSelection(sid, 1);
}

function $setSelection(focused, forced) {
    var container = document.getElementById(sid);
    var options = container.options;

    if (!is_null(container) && options.length > 0 && (focused != sid || forced)) {
        //alert(options.selectedIndex);
        if (options.selectedIndex == -1)
            options.selectedIndex = 0;
        container.focus();
    }
    else
        container.blur();
}

function $hasSelectedItems() {
    var container = $("#"+sid);
    var options = container.prop("options");
    return options.length;
}

function $getSelectedItems() {
    var container = $("#"+sid);
    var values = new Array();

    $("option", container).each(function() {
        var x = $(this).attr('value');
        values.push(x);
    });

    return values.join(':');
}

// ===========================
// Dialog windows declarations
// ===========================

function MakeFilterSubmit(mode, page) {
    $("#filter-form").attr("action", baseURI);

    switch (mode) {

        // -------------
        // Submit modes:
        // -------------
        //  0 - changed client
        //  1 - changed filename
        //  2 - changed status
        //  3 - changed persstatus
        //  4 - changed perstype
        //  5 - changed date from
        //  6 - changed date to
        //  7 - changed state

        case 0:
            $("#oper_id").each(function() { $(this).val(0); });
            $("#filename").each(function() { $(this).val(''); });
        case 1:
            $("#perstype").val(0);
            $("#persstatus").val('');
        case 2:
            $("#persstatus").val('');
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
            break;

        // ---------------------------
        // LineSelector Handler submit
        // ---------------------------

        case 9:
            $("#pers_id").each(function() { $(this).val(0); });
            $("#oper_id").each(function() { $(this).val(0); });
    }

    $ResetLogPage();
    $setPaginationFormSubmit(page);
    $onParentFormSubmit('filter-form');
}

function makeTodayRequest() {
    var date = new Date();
    var now = date.getToday();

    $("#client").each(function() { $(this).val(''); });
    $("#filename").each(function() { $(this).val(''); });
    $("#status").each(function() { $(this).val(0); });
    $("#perstatus").each(function() { $(this).val(''); });
    $("#perstype").each(function() { $(this).val(0); });
    $("#order-date-from").val(now);

    $onParentFormSubmit('filter-form');
}

// =========================
// Custom routine assigments
// =========================

function selectFileBatches(x) {
    var data = x['data'];

    if (data.length == 0) {
        $NotificationDialog.open(keywords['Warning:No inactive batches'], 500);
        return;
    }

    //alert(data);

    var container = $("#"+sid);
    var options = container.prop("options");

    $('option', container).remove();

    //alert(options.length);

    data.forEach(function(s) {
        var oid = s.toString();
        var option = new Option(oid, oid, false, false);
        options[options.length] = option;
    });
}

function rejectSelectedBatches() {
    confirm_action = 'reject';

    $ConfirmDialog.open(keywords['Command:Reject activation'], 600);
}

function activateTask(x) {
    var data = x['data'];
    var props = x['props'];
    var errors = x['errors'];

    //alert(x['currentfile']+':'+errors.join('|')+':'+errors.length);

    if (errors.length > 0) {
        var msg = errors.join('<br>');
        $ShowError(msg, true, true, false);
        return;
    }

    //alert(is_empty(selected_report_id)+':'+selected_report_id);

    if (!is_empty(selected_report_id)) {
        var report = getsplitteditem(selected_report_id, '-', 1, null);
        printCardsSelectedReport(data, props, report);
        selected_report_id = '';
        return;
    }

    confirm_action = 'activate';

    printCardsPacket(data, props);

    $ConfirmDialog.open(keywords['Command:Activate selected batches'], 500);
}

// ====================
// Page Event Listeners
// ====================

jQuery(function($) 
{
    // --------------
    // Line selection
    // --------------

    $(".line").click(function(e) {
        if (is_show_error)
            return;

        is_noprogress = true;

        $DblClickAction.click(
            function(ob) {
                is_noprogress = false;
                $LineSelector.set_current(ob);
                $onToggleSelectedClass(LINE, ob, 'submit', null);
            },
            function(ob) {
                $addSelection(ob);
            },
            $(this)
        );
    })
    .on("dblclick", function(e){
        e.preventDefault();
    });

    // ----------------------
    // Selection item remover
    // ----------------------

    $("#selected-batches").click(function(e) {
        if (is_show_error)
            return;

        $DblClickAction.click(null, function(ob) { $removeSelection(); }, $(this));
    })
    .on("dblclick", function(e){
        e.preventDefault();
    });

    // -----------------
    // SubLine selection
    // -----------------

    $("#subline-content").on('click', '.subline', function(e) {
        if (is_show_error)
            return;

        var ob = $(this);
        $SublineSelector.onRefresh(ob);
    });

    // ---------------------
    // Data Section progress
    // ---------------------

    $("#data-section").on('click', '.column', function(e) {
        if (is_noprogress || is_show_error) {
            is_noprogress = false;
            return;
        }

        //alert('is_noprogress:'+is_noprogress);

        var ob = $(this);
        var parent = ob.parents("*[class*='line']").first();
        if (!is_null(parent) && !parent.hasClass("tabline"))
            $InProgress(ob, 1);
    });

    // ----------------------
    // Cards Operator Buttons
    // ----------------------

    function $acivateSelectedBatches() {
        if ($hasSelectedItems())
            $Handle('710', function(x) { activateTask(x); });
        else
            $ShowError(keywords['Warning:No selected items'], true, true, false);
    }

    function $rejectSelectedBatches() {
        if ($hasSelectedItems())
            rejectSelectedBatches();
        else
            $ShowError(keywords['Warning:No selected items'], true, true, false);
    }

    $("button[id^='CARDS']", this).click(function(e) {
        var ob = $(this);
        var x = ob.attr("id").split('_');
        var id = x.length == 2 ? x[1] : null;

        switch (id) {
            case 'ACTIVATION':
                $acivateSelectedBatches();
                break;
        }
    });

    // ------------------------------
    // Tab table lines data selection
    // ------------------------------

    $(".view-lines").on('click', '.tabline', function(e) {
        var ob = $(this);

        if (!is_null(current_tabline))
            $onToggleSelectedClass(TABLINE, current_tabline, 'remove', null);
        
        current_tabline = ob;
        SelectedSetItem(TABLINE, 'ob', current_tabline);

        $onToggleSelectedClass(TABLINE, current_tabline, 'add', null);
    });

    // ------------------------
    // Control Panel Menu items
    // ------------------------

    function $activateFileBatches() {
        $Handle('705', function(x) { selectFileBatches(x); });
    }

    $("#status-confirm-container").on('click', '.change-status-item', function(e) {
        $StatusChangeDialog.toggle($(this));
    });

    $("button[id^='admin']", this).click(function(e) {
        var ob = $(this);
        var command = ob.attr('id');

        $onControlPanelClick($("#admin-panel-dropdown"));

        if (is_null(command))
            return;

        if (['admin:activate'].indexOf(command) > -1) {
            $activateFileBatches();
            return;
        }

        if (['admin:reject'].indexOf(command) > -1) {
            $rejectSelectedBatches();
            return;
        }

        $onToggleSelectedClass(LINE, null, 'submit', command, true);
    });

    $("button[id^='service']", this).click(function(e) {
        var ob = $(this);
        var command = ob.attr('id');

        $onControlPanelClick($("#services-dropdown"));

        if (!is_null(command)) {
            selected_report_id = getsplitteditem(command, ':', 1, null);
            $acivateSelectedBatches();
        }

        e.preventDefault();
    });

    // --------------
    // Tabs Data menu
    // --------------

    $("div[id^='data-menu']", this).click(function(e) {
        $TabSelector.onClick($(this));
    });

    // --------
    // Keyboard
    // --------

    $(window).keydown(function(e) {
        if ($ConfirmDialog.is_focused() || $NotificationDialog.is_focused())
            return;

        var focused = document.activeElement.id;

        //alert(e.ctrlKey+':'+e.shiftKey+':'+e.altKey+':'+e.keyCode);

        if (is_show_error)
            return;

        if (e.keyCode==13)                               // Enter
            if (focused != sid && !is_search_focused)
                $addSelection(SelectedGetItem(LINE, 'ob'));

        if (e.keyCode==46)                               // Del
            if (focused == sid)
                $removeSelection();

        var exit = false;

        if (e.shiftKey && e.keyCode==65) {               // Shift-A
            $activateFileBatches();
            exit = true;
        }

        if (e.shiftKey && e.keyCode==80) {               // Shift-P
            $acivateSelectedBatches();
            exit = true;
        }

        if (e.shiftKey && e.keyCode==9) {                // Shift-TAB
            $setSelection(focused, 0);
            exit = true;
        }

        else if (e.shiftKey && e.keyCode==81) {          // Shift-Q
            $TagSearchDialog.open();
            exit = true;
        }

        else if (e.shiftKey && e.keyCode==84) {          // Shift-T
            makeTodayRequest();
            exit = true;
        }

        if (exit) {
            e.preventDefault();
            return false;
        }
    });
});

// =======
// STARTER
// =======

$(function() 
{
    if (IsTrace)
        alert('Document Ready (cards)');

    current_context = 'cards';

    $("#search-context").attr("placeholder", "Найти (имя файла, ТЗ)...");

    $_init();
});



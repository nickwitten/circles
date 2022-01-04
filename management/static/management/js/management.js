class AdminManage extends JqueryElement {
    constructor(id, parent) {
        super(id, parent)
        this.folders = new Folders("admin_folders", this);
        this.init_users();
        this.init_chapters();
    }

    init_users() {
        var user_elements = $('#users').find('.user');
        var items = []
        for (var i=0; i<user_elements.length; i++ ) {
            items.push($(user_elements[i]));
        }
        this.users = new DataList("users", items, this);
        this.users.reset();
    }

    init_chapters() {
        var elements = $('#chapters').find('.item');
        var items = []
        for (var i=0; i<elements.length; i++ ) {
            items.push($(elements[i]));
        }
        this.chapters = new DataList("chapters", items, this);
        this.chapters.reset();
    }
}


class SiteManage extends JqueryElement {
    constructor(id, parent) {
        super(id, parent)
    }
}


class ManagementMenu extends Menu {
    constructor(id, menu_btn_id) {
        super(id, menu_btn_id);
        this.admin = null;
        this.site = null;
        this.manage_select = new MenuSiteSelect('menu_site_select', 'radio');
        this.manage_listeners();
        this.init_admin();
    }

    init_admin() {
        this.admin = new AdminManage('main_container', this);
    }

    init_site() {
        this.site = new SiteManage('main_container', this);
    }

    trigger_update() {
        var url = url_management;
        url += "?manage=" + this.manage_select.value[0];
        history.pushState({}, '', url)
        $(window).trigger('popstate');
    }

    manage_listeners() {
        this.manage_select.element.on(":change", {'object': this, 'func': this.trigger_update}, this.dispatch);
    }
}

// Checks if there are unsaved changes before leaving
function discard_changes() {
//     var active_slide = learning_list.active_slide;
//     if (active_slide && !active_slide.changes_saved) {
//         return 'You have unsaved changes';
//     }
}


function update_page() {
    var query = parseQuery(window.location.search);
    // If there is no query, trigger an update from menu
    if (!Object.keys(query).length) {
        management_menu.trigger_update();
        return
    }
    console.log(query);
    console.log(management_menu.manage_select.value);

//     if (query.site) {
//         learning_list.site_select.set_value(query.site, true);
//     }
//     if (query.type) {
//         learning_list.type_select.set_value(query.type);
//     }
//     if (query.id && learning_list.slide_inds.hasOwnProperty(query.model_type)) {
//         learning_list.show_item_info(query.model_type, query.id);
//     }
}


var management_menu;
$(document).ready(function() {
    management_menu = new ManagementMenu('menu', 'menu_btn');
    $(window).bind('beforeunload', discard_changes);
    $(window).on('popstate', update_page);
    $(window).trigger('popstate');
});


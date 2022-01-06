class ModelListEdit extends JqueryElement {
    constructor(id, datalist_id, form_id, parent) {
        super(id, parent)
        this.datalist_id = datalist_id;
        this.form_id = form_id;
        this.init_datalist();
        this.listeners();
    }

    init_datalist() {
        var list_elements = this.element.find('.list-item');
        var jquery_items = []
        for (var i=0; i<list_elements.length; i++ ) {
            jquery_items.push($(list_elements[i]));
        }
        this.data_list = new DataList(this.datalist_id, jquery_items, this);
        this.data_list.reset();
    }

    select_form(option) {
        if ($(option).attr("data-url")) {
            this.form = new AjaxForm(this.form_id, $(option).attr("data-url"), this);
            this.element.find(".content.hide").removeClass("hide");
        }
    }

    listeners() {
        this.element.children().off(".list-edit");
        this.element.find(".option").on("click.list-edit", {'object': this, 'func': this.select_form}, this.dispatch);
    }
}

class Users extends JqueryElement {
    constructor(id, parent) {
        super(id, parent)
        var user_elements = this.element.find('.user');
        var items = []
        for (var i=0; i<user_elements.length; i++ ) {
            items.push($(user_elements[i]));
        }
        this.users = new DataList("users", items, this);
        this.users.reset();
        this.user_form = new AjaxForm("user_form_container", url_create_user, this);
        this.listeners();
    }

    select_form(option) {
        if ($(option).attr("data-url")) {
            this.user_form = new AjaxForm("user_form_container", $(option).attr("data-url"), this);
            this.element.find(".content.hide").removeClass("hide");
        }
    }

    listeners() {
        this.element.children().off(".manage");
        this.element.find(".option").on("click.manage", {'object': this, 'func': this.select_form}, this.dispatch);
    }
}

class Chapters extends JqueryElement {
    constructor(id, parent) {
        super(id, parent);
        var elements = this.element.find('.item');
        var items = []
        for (var i=0; i<elements.length; i++ ) {
            items.push($(elements[i]));
        }
        this.chapters = new DataList("chapters", items, this);
        this.chapters.reset();
        this.chapter_form = new AjaxForm("chapter_form_container", url_create_chapter, this);
        this.listeners();
    }

    select_form(option) {
        if ($(option).attr("data-url")) {
            this.chapter_form = new AjaxForm("chapter_form_container", $(option).attr("data-url"), this);
            this.element.find(".content.hide").removeClass("hide");
        }
    }

    listeners() {
        this.element.children().off(".manage");
        this.element.find(".option").on("click.manage", {'object': this, 'func': this.select_form}, this.dispatch);
    }
}


class AdminManage extends JqueryElement {
    constructor(id, parent) {
        super(id, parent)
        this.folders = new Folders("admin_folders", this);
        this.users = new ModelListEdit("users_content", "users", "user_form_container", this);
        this.chapters = new ModelListEdit("chapters_content", "chapters", "chapter_form_container", this);
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

